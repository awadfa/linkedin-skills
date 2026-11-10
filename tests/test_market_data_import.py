import csv
import tempfile
import unittest
from pathlib import Path
from lib.market_data_import import summarize_csv
from lib.market_evidence import EvidenceError


class MarketImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "sample.csv"
        with self.path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerows([["date", "amount"], ["2026-01-01", "100"],
                              ["2026-01-02", "200"], ["2026-02-01", "300"]])
        self.args = dict(date_column="date", amount_column="amount",
                         first_start="2026-01-01", first_end="2026-01-31",
                         second_start="2026-02-01", second_end="2026-02-28",
                         source_name="Example", source_url="https://example.org/data",
                         retrieved_on="2026-03-02", published_on="2026-03-01")

    def test_offline_summary_is_unverified(self):
        result = summarize_csv(str(self.path), **self.args)
        self.assertEqual(result["comparison"]["first"]["rows"], 2)
        self.assertEqual(result["comparison"]["second"]["amount_sum"], "300")
        self.assertEqual(result["comparison"]["row_count_change_percent"], "-50.0")
        self.assertFalse(result["publish_allowed"])

    def test_invalid_url_rejected(self):
        with self.assertRaises(EvidenceError):
            summarize_csv(str(self.path), **dict(self.args, source_url="http://example.org"))

    def test_overlap_rejected(self):
        with self.assertRaises(EvidenceError):
            summarize_csv(str(self.path), **dict(self.args, second_start="2026-01-31"))

    def test_invalid_amount_rejected(self):
        self.path.write_text("date,amount\n2026-01-01,not-a-number\n", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            summarize_csv(str(self.path), **self.args)
