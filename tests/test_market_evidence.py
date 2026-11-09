import unittest
from lib.market_evidence import EvidenceError, validate_claim, percent_change, review_bundle


def sample(**changes):
    record = dict(statement="Sales rose by 10%", source_name="Official data provider",
                  source_url="https://example.gov.ae/data", published_on="2026-11-01",
                  period_start="2026-10-01", period_end="2026-10-31",
                  retrieved_on="2026-11-09", claim_type="official_fact",
                  verified_by_human=True)
    record.update(changes)
    return record


class MarketEvidenceTests(unittest.TestCase):
    def test_complete_verified_record_is_accepted(self):
        self.assertFalse(review_bundle("Draft", [sample()])["publish_allowed"])

    def test_missing_source_is_rejected(self):
        with self.assertRaises(EvidenceError):
            validate_claim(sample(source_url=""))

    def test_no_human_verification_is_rejected(self):
        with self.assertRaises(EvidenceError):
            validate_claim(sample(verified_by_human=False))

    def test_insecure_url_is_rejected(self):
        with self.assertRaises(EvidenceError):
            validate_claim(sample(source_url="http://example.com"))

    def test_invalid_period_is_rejected(self):
        with self.assertRaises(EvidenceError):
            validate_claim(sample(period_start="2026-12-01"))

    def test_analysis_requires_method(self):
        with self.assertRaises(EvidenceError):
            validate_claim(sample(claim_type="analysis"))
        self.assertEqual(validate_claim(sample(claim_type="analysis", methodology="Compare months"))["methodology"], "Compare months")

    def test_percent_change(self):
        self.assertEqual(percent_change("100", "115"), "15.00")
        with self.assertRaises(EvidenceError):
            percent_change("0", "100")

    def test_draft_cannot_be_approved_by_code(self):
        with self.assertRaises(EvidenceError):
            review_bundle("Draft", [])
