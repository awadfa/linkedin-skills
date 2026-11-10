# Free official-data intake: phase 1

The new `market-compare` command reads a **locally downloaded CSV**. It does not
connect to DLD, call an API, scrape websites, use credentials, or incur charges.

Download an officially published dataset manually from
https://dubailand.gov.ae/en/open-data/real-estate-data/ and review its permitted
use, coverage, column names, units, filters and update date. The CLI is schema-
agnostic: pass the actual date and numeric amount column names. It requires ISO
dates (`YYYY-MM-DD`), so if the downloaded file uses another format, prepare a
local working copy with normalized dates and preserve the original separately.

Example, using a **hypothetical** CSV saved under ignored `testing/`:

```bash
python3 scripts/real_estate_workspace.py market-compare \
  --input testing/transactions.csv \
  --date-column transaction_date --amount-column amount \
  --first-start 2026-01-01 --first-end 2026-01-31 \
  --second-start 2026-02-01 --second-end 2026-02-28 \
  --source-name "Dubai Land Department" \
  --source-url "https://dubailand.gov.ae/en/open-data/real-estate-data/" \
  --published-on 2026-03-01 --retrieved-on 2026-03-02
```

Replace all example dates, fields and source details with **real verified values**.
The output counts CSV rows and sums amounts. It does not infer that rows are unique
sales, that amounts are AED, or that periods are comparable. The result is marked
unverified and `publish_allowed: false`.

Next, a person checks the original source, scope, date, transaction types, duplicates,
units and calculation. Only then use `review-evidence` with a manually verified
claim and draft. No source = no statistic. All output stays in draft status.

Tests: `python3 -m unittest discover -s tests -p 'test_market_*.py'`.
