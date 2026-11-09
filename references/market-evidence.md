# Evidence-first real estate publishing

**Rule: No source = no statistic.** All numerical market claims must have an original source, direct HTTPS URL, publication date, coverage period, retrieval date, and human verification. Clearly separate official facts, third-party facts, and your own analysis. Analysis requires a reproducible methodology. For percentages, preserve underlying numerator/denominator or previous/current figures in the research notes.

Use official Dubai Land Department data as a preferred original source for transaction figures. Other research, including market reports, can add context but must be clearly attributed. Check the source's usage terms before reproducing any content.

The module `lib/market_evidence.py` validates the completeness of a claim's audit trail, not its factual accuracy. It performs **no network requests**, subscriptions, scraping, email reading, publishing or scheduling. Human verification is an explicit assertion, not automated fact-checking. Never mark it true unless a person actually inspected the original data.

Example local file `testing/evidence.json` (keep real research and drafts uncommitted):

```json
{
  "draft": "Example draft for review only.",
  "claims": [{
    "statement": "Example statement (replace with verified facts)",
    "source_name": "Original publisher",
    "source_url": "https://example.gov.ae/data",
    "published_on": "2026-11-01",
    "period_start": "2026-10-01",
    "period_end": "2026-10-31",
    "retrieved_on": "2026-11-09",
    "claim_type": "official_fact",
    "verified_by_human": false
  }]
}
```

Set `verified_by_human` to true **only after reviewing the original source**. The example intentionally fails validation until that happens.

```python
from lib.market_evidence import load_bundle
result = load_bundle("testing/evidence.json")
# Result is always Draft - human review required; publish_allowed is always False.
```

Before drafting, verify the data and its date; if unavailable, omit numerical claims. Cite the original source in the LinkedIn draft and retain this evidence bundle for review. The next phase may add approved free data ingestion, but it must not treat a URL or a downloaded document as automatically verified.
