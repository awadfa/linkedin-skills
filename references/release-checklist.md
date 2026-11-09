# Zero-cost release verification checklist

**Status:** development branch only. Do not merge or publish until tests pass.

## Run locally (no third-party services or paid API calls)

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/real_estate_workspace.py --help
python3 scripts/real_estate_workspace.py content-plan --start 2026-11-10 --audience "Dubai investors"
```

Verify the marketplace copy independently:

```bash
cd .codex-marketplace/linkedin-skills
python3 scripts/real_estate_workspace.py --help
cd ../..
```

For market comparison, prepare a **local, non-sensitive** sample CSV with ISO dates,
and follow `references/market-data-intake.md`. Compare output totals by hand.
For market-post, use a **fictional** test bundle with `verified_by_human: true`
only in tests; do not mark real claims verified unless checked against originals.
Test that missing verification is rejected.

## Required before merge

- [ ] Run complete Python unittest suite and record exact passing test count
- [ ] Confirm original DLD CSV source, download permissions and actual column names
- [ ] Check source period, units, transaction types, duplicate handling
- [ ] Confirm every published market number has reviewed evidence
- [ ] Confirm zero-cost profile and no HTTP, posting, outreach or scheduling calls
- [ ] Review any changes to original upstream posting instructions
- [ ] Get explicit owner approval to merge or publish

**Never upload private prospect lists, client phone numbers, authentication tokens
or company-owned data to the GitHub repository.**

Current environment limitation: connected GitHub permits editing the development
branch but does not itself execute Python tests. Local clone attempt failed due to
DNS/network restrictions; no test success is claimed.
