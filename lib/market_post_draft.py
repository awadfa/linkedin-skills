"""Build a review-only LinkedIn draft from a human-verified evidence bundle.

No network, AI API, publication, scheduling or outreach.
"""
from __future__ import annotations
from .market_evidence import EvidenceError, review_bundle


def build_market_post(draft: str, claims: list[dict], *, audience: str = "Dubai property investors") -> dict:
    reviewed = review_bundle(draft, claims)
    if not isinstance(audience, str) or not audience.strip():
        raise EvidenceError("Audience is required.")
    citations = []
    for claim in reviewed["evidence"]:
        entry = {
            "statement": claim["statement"],
            "source_name": claim["source_name"],
            "source_url": claim["source_url"],
            "period": f'{claim["period_start"]} to {claim["period_end"]}',
            "claim_type": claim["claim_type"],
        }
        if "methodology" in claim:
            entry["methodology"] = claim["methodology"]
        citations.append(entry)
    return {
        "status": "REVIEW ONLY — not approved for publishing",
        "audience": audience.strip(),
        "draft": reviewed["draft"],
        "citations_for_manual_review": citations,
        "checks": [
            "Check each number and quoted statement against its original source.",
            "Confirm the draft does not imply guaranteed returns or investment advice.",
            "Check voice, dates, scope, units and any external references.",
            "Obtain explicit approval before manually publishing on LinkedIn.",
        ],
        "publish_allowed": False,
        "scheduled": False,
        "messages_sent": 0,
    }
