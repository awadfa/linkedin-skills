import csv
import tempfile
import unittest
from pathlib import Path
from lib.quarterly_real_estate import analyze_quarters, QuarterlyDataError


class QuarterlyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "sample.csv"
        self.rows = [
            ["2026", "1", "Sales", "Units", "Number", "3"],
            ["2026", "1", "Sales", "Units", "Value", "900"],
            ["2026", "1", "Sales", "Land", "Number", "2"],
            ["2026", "1", "Sales", "Land", "Value", "500"],
            ["2026", "1", "Mortgages", "Units", "Number", "10"],
        ]
        self.save()

    def save(self):
        with self.file.open("w", encoding="utf-8", newline="") as stream:
            w = csv.writer(stream)
            w.writerow(["Year", "Quarter_Number", "Title", "Type", "Description", "Value"])
            w.writerows(self.rows)

    def test_aggregates_without_mixing_measures_or_transactions(self):
        result = analyze_quarters(self.file, year=2026)
        self.assertEqual(len(result["periods"]), 1)
        self.assertEqual(result["periods"][0]["recorded_count"], 5)
        self.assertEqual(result["periods"][0]["recorded_value_raw"], "1400")
        self.assertFalse(result["publish_allowed"])
        self.assertFalse(result["periods"][0]["currency_confirmed"])

    def test_duplicate_key_is_rejected(self):
        self.rows.append(self.rows[0])
        self.save()
        with self.assertRaises(QuarterlyDataError):
            analyze_quarters(self.file)

    def test_invalid_negative_measure_is_rejected(self):
        self.rows[0][-1] = "-1"
        self.save()
        with self.assertRaises(QuarterlyDataError):
            analyze_quarters(self.file)

    def test_noninteger_count_is_rejected(self):
        self.rows[0][-1] = "1.5"
        self.save()
        with self.assertRaises(QuarterlyDataError):
            analyze_quarters(self.file)
