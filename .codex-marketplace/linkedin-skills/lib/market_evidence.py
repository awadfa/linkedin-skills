"""Offline evidence register for real-estate LinkedIn drafts.

No network access. The author must supply and verify the original source.
A claim without valid evidence is rejected rather than silently published.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
import json


class EvidenceError(ValueError):
    pass


def _https_url(value: str) -> str:
    if not isinstance(value, str):
        raise EvidenceError("Source URL must be text.")
    try:
        url = urlsplit(value)
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise EvidenceError("Source must be a public HTTPS URL.")
    except ValueError as exc:
        raise EvidenceError("Invalid source URL.") from exc
    return value


def _date(value: str, field: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"{field} must be an ISO date.") from exc


def validate_claim(claim: dict) -> dict:
    """Validate a manually researched claim and retain its audit trail.

    Validation checks completeness, NOT whether the external claim is true.
    """
    if not isinstance(claim, dict):
        raise EvidenceError("Claim must be an object.")
    required = ("statement", "source_name", "source_url", "published_on",
                "period_start", "period_end", "retrieved_on", "claim_type")
    for field in required:
        if not isinstance(claim.get(field), str) or not claim[field].strip():
            raise EvidenceError(f"Missing {field}.")
    if claim["claim_type"] not in ("official_fact", "third_party_fact", "analysis"):
        raise EvidenceError("Unknown claim_type.")
    result = {key: claim[key].strip() for key in required}
    result["source_url"] = _https_url(result["source_url"])
    for field in ("published_on", "period_start", "period_end", "retrieved_on"):
        result[field] = _date(result[field], field)
    if result["period_start"] > result["period_end"]:
        raise EvidenceError("Period start is after period end.")
    if result["published_on"] > result["retrieved_on"]:
        raise EvidenceError("Source publication is after retrieval.")
    if claim["claim_type"] == "analysis":
        method = claim.get("methodology")
        if not isinstance(method, str) or not method.strip():
            raise EvidenceError("Analysis requires methodology.")
        result["methodology"] = method.strip()
    result["verified_by_human"] = claim.get("verified_by_human") is True
    if not result["verified_by_human"]:
        raise EvidenceError("Source requires explicit human verification.")
    return result


def percent_change(previous: str, current: str) -> str:
    """Calculate (current - previous) / previous * 100, without rounding claims."""
    try:
        old, new = Decimal(str(previous)), Decimal(str(current))
        if not old.is_finite() or not new.is_finite() or old <= 0 or new < 0:
            raise EvidenceError("Previous must be positive and current nonnegative.")
        return str((new - old) / old * 100)
    except (InvalidOperation, TypeError) as exc:
        raise EvidenceError("Invalid numeric input.") from exc


def review_bundle(draft: str, claims: list[dict]) -> dict:
    """Fail closed for data-bearing drafts; no sending or publishing."""
    if not isinstance(draft, str) or not draft.strip():
        raise EvidenceError("Draft is required.")
    if not isinstance(claims, list) or not claims:
        raise EvidenceError("At least one source-backed claim is required.")
    evidence = [validate_claim(item) for item in claims]
    return {"status": "Draft - human review required", "publish_allowed": False,
            "draft": draft, "evidence": evidence,
            "notice": "Completeness checks only; verify values against the linked originals."}


def load_bundle(path: str) -> dict:
    with open(path, encoding="utf-8") as stream:
        payload = json.load(stream)
    return review_bundle(payload["draft"], payload["claims"])
