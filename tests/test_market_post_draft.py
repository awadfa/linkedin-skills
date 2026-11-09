import unittest
from lib.market_evidence import EvidenceError
from lib.market_post_draft import build_market_post


class MarketPostTests(unittest.TestCase):
    def setUp(self):
        self.claim = {
            "statement": "Illustrative transaction comparison",
            "source_name": "Example source",
            "source_url": "https://example.org/data",
            "published_on": "2026-03-01",
            "period_start": "2026-01-01",
            "period_end": "2026-02-28",
            "retrieved_on": "2026-03-02",
            "claim_type": "official_fact",
            "verified_by_human": True,
        }

    def test_review_only_and_citations(self):
        result = build_market_post("A draft to review.", [self.claim])
        self.assertFalse(result["publish_allowed"])
        self.assertFalse(result["scheduled"])
        self.assertEqual(result["messages_sent"], 0)
        self.assertEqual(result["citations_for_manual_review"][0]["source_url"], "https://example.org/data")

    def test_unverified_claim_rejected(self):
        with self.assertRaises(EvidenceError):
            build_market_post("Draft", [dict(self.claim, verified_by_human=False)])

    def test_missing_claim_rejected(self):
        with self.assertRaises(EvidenceError):
            build_market_post("Draft", [])

    def test_missing_audience_rejected(self):
        with self.assertRaises(EvidenceError):
            build_market_post("Draft", [self.claim], audience=" ")
