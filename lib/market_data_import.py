"""Prepare a traceable market-statistic brief from a locally downloaded CSV.

No network, no scraping, no claims of official verification. The user supplies
a source URL and confirms the original dataset independently.
"""
from __future__ import annotations
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from .market_evidence import EvidenceError, _https_url, _date, percent_change


def _number(value: str) -> Decimal:
    try:
        number = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError) as exc:
        raise EvidenceError("Invalid transaction amount.") from exc
    if not number.is_finite() or number < 0:
        raise EvidenceError("Transaction amount must be nonnegative.")
    return number


def summarize_csv(path: str, *, date_column: str, amount_column: str,
                  first_start: str, first_end: str, second_start: str,
                  second_end: str, source_name: str, source_url: str,
                  retrieved_on: str, published_on: str) -> dict:
    """Count rows and sum amounts in two nonoverlapping periods.

    This is a mechanical summary of the supplied file, not an assertion that
    its rows are valid DLD transactions. Currency, units and transaction types
    must be independently checked before any public claim.
    """
    _https_url(source_url)
    dates = [_date(x, name) for name, x in
             (("first_start", first_start), ("first_end", first_end),
              ("second_start", second_start), ("second_end", second_end),
              ("retrieved_on", retrieved_on), ("published_on", published_on))]
    a, b, c, d, retrieved, published = dates
    if not (a <= b < c <= d):
        raise EvidenceError("Comparison periods must be ordered and nonoverlapping.")
    if published > retrieved:
        raise EvidenceError("Publication date cannot follow retrieval.")
    counts = [0, 0]
    totals = [Decimal(0), Decimal(0)]
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or date_column not in reader.fieldnames or amount_column not in reader.fieldnames:
            raise EvidenceError("CSV is missing the specified date or amount column.")
        for line, row in enumerate(reader, start=2):
            try:
                day = date.fromisoformat(row[date_column].strip()).isoformat()
                amount = _number(row[amount_column])
            except (ValueError, AttributeError, EvidenceError) as exc:
                raise EvidenceError(f"Invalid CSV data at line {line}: {exc}") from exc
            index = 0 if a <= day <= b else 1 if c <= day <= d else None
            if index is not None:
                counts[index] += 1
                totals[index] += amount
    if not counts[0]:
        raise EvidenceError("First comparison period has no rows; cannot calculate change.")
    count_change = percent_change(str(counts[0]), str(counts[1]))
    return {
        "state": "Unverified research brief — do not publish",
        "source": {"name": source_name, "url": source_url,
                   "published_on": published, "retrieved_on": retrieved,
                   "local_file": str(path)},
        "comparison": {
            "first": {"start": a, "end": b, "rows": counts[0], "amount_sum": str(totals[0])},
            "second": {"start": c, "end": d, "rows": counts[1], "amount_sum": str(totals[1])},
            "row_count_change_percent": count_change
        },
        "draft_angle": "What changed between the two periods, and what should an investor verify?",
        "required_review": [
            "Confirm original publisher and exact downloadable dataset URL.",
            "Confirm file contains the intended transaction types and no duplicate records.",
            "Confirm date format, amount currency/units and whether records were filtered.",
            "Check original dataset values and methodology; then create a human-verified evidence bundle.",
            "Never describe CSV row counts as official transaction counts before those checks."
        ],
        "publish_allowed": False
    }
