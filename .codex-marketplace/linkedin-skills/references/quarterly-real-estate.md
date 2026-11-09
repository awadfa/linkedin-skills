# Data Dubai quarterly transaction statistics

This input is **quarterly aggregated statistics**, not individual sale records.
Expected CSV columns: `Year`, `Quarter_Number`, `Title`, `Type`,
`Description`, `Value`. Example categories: Sales / Mortgages / Other,
Units / Building / Land / Villa, Number / Value.

Download the public CSV separately; do not commit downloaded data or any
private customer records. The source page is the Data Dubai 'Real Estate
Transactions' dataset. Its publisher, metadata, currency, and reporting
coverage must be independently checked before public use.

```bash
python3 scripts/real_estate_workspace.py quarterly-report \
  --input "Real_Estate_Transactions_2026-11-09.csv" \
  --year 2026 --transaction Sales
```

The command sums property-type categories **separately for Number and Value**,
rejects duplicate keys, negative measures, and non-integer counts, and never
combines Sales with Mortgages. It returns `publish_allowed: false` and leaves
currency unconfirmed. Before turning the output into LinkedIn content, review
source definitions, update date, periods and units, and manually verify claims.

Example observed in the user's downloaded CSV (research-only, unverified units):
2026 Q1 Sales 47,987 / 176,368,526,215 raw units; Q2 38,264 /
109,473,394,355; Q3 37,490 / 92,817,721,733. These are **sums of
reported categories**, not independently audited DLD transaction totals.
