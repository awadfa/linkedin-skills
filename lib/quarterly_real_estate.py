"""Offline aggregation of Data Dubai's quarterly real-estate statistics CSV.

The dataset contains one measure per (year, quarter, transaction, property type,
measure) key, NOT one row per property transaction. Values are kept in their
original units until confirmed from the publisher's metadata.
"""
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


class QuarterlyDataError(ValueError):
    pass


REQUIRED = {"Year", "Quarter_Number", "Title", "Type", "Description", "Value"}
MEASURES = {"Number", "Value"}


def analyze_quarters(path, *, transaction="Sales", year=None):
    grouped = defaultdict(lambda: {"Number": Decimal(0), "Value": Decimal(0), "types": set()})
    seen = set()
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise QuarterlyDataError("Missing required quarterly dataset columns")
        rows = 0
        for line, row in enumerate(reader, 2):
            rows += 1
            try:
                yr = int(row["Year"])
                quarter = int(row["Quarter_Number"])
                measure = row["Description"].strip()
                category = row["Type"].strip()
                title = row["Title"].strip()
                number = Decimal(row["Value"].strip())
            except (ValueError, TypeError, AttributeError, InvalidOperation) as exc:
                raise QuarterlyDataError(f"Invalid row {line}") from exc
            if quarter not in (1, 2, 3, 4) or measure not in MEASURES or not category or not title:
                raise QuarterlyDataError(f"Unexpected category at row {line}")
            if not number.is_finite() or number < 0 or (measure == "Number" and number != number.to_integral_value()):
                raise QuarterlyDataError(f"Invalid measure at row {line}")
            key = (yr, quarter, title, category, measure)
            if key in seen:
                raise QuarterlyDataError(f"Duplicate statistical key at row {line}")
            seen.add(key)
            if title != transaction or (year is not None and yr != int(year)):
                continue
            item = grouped[(yr, quarter)]
            item[measure] += number
            item["types"].add(category)
    periods = []
    for (yr, quarter), data in sorted(grouped.items()):
        periods.append({
            "year": yr, "quarter": quarter,
            "transaction": transaction,
            "recorded_count": int(data["Number"]),
            "recorded_value_raw": str(data["Value"]),
            "property_types": sorted(data["types"]),
            "currency_confirmed": False,
        })
    return {
        "status": "RESEARCH ONLY — source metadata and coverage require verification",
        "source_format": "Data Dubai quarterly aggregate statistics",
        "input_rows": rows,
        "periods": periods,
        "warnings": [
            "Values retain source units; do not label as AED without verifying metadata.",
            "Totals sum reported property-type categories, not individual transactions.",
            "Check the source's coverage and category definitions before publication.",
            "Quarterly series may be incomplete or revised; compare only like-for-like periods.",
        ],
        "publish_allowed": False,
    }
