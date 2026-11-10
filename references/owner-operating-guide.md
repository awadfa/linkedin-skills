# Owner operation and clean handoff

This fork prepares real-estate content and professional relationship research. It does not promise leads, returns, referrals or sales. Cost policy: zero dollars. No automatic LinkedIn publishing or outreach. Keep the default `awad` profile; legacy integrations are outside this operating procedure.

## Work in order

1. Review the current Notion relationship log before using any prospect list. Deduplicate by exact profile, existing thread and agency. Reconfirm role and identity; quarantine ambiguous profiles. Public affiliation is not proof of investment intent or referral authority.
2. Prepare a specific content brief or an individual introduction. Use accurate owner facts and sourced claims. Do not invent clients, partnerships, returns or expertise. Have the owner review content before publishing. A daily content idea is not a scheduled post.
3. Execute only through a supported, manually reviewed platform interaction covered by the owner's explicit approval. A bounded approval applies only to its stated date, recipients/actions and maximum; it does not roll over to another day. Never accept fees, meetings or commercial obligations without separate authorization.
4. Log the exact text, destination, time and visible result immediately. Drafts, attempts and uncertain results are not sends. For unavailable history, mark unknown; do not reconstruct imaginary evidence.
5. Review replies for real requirements and potential referral relationships. Close irrelevant service offers politely. A prospect with no response is not an opportunity; qualify a requirement before passing a negotiation to the owner.

## Platform limits and Clay

If free personalized invitation notes are exhausted, stop that action. Do not buy credits, activate a trial, bypass limits, withdraw invitations to resend, or submit a different form of outreach merely to reach a count. Continue research, drafts, record review and reply triage within existing authorization. Recheck availability only when returning to the task; no background retry or timer is configured. A note limit does not establish that every messaging capability is unavailable.

Clay planning is offline and free. Before any connected Clay execution, check its tool's cost and authorization. Unknown cost means stop that operation. No paid enrichment, guessed email addresses, private company datasets or scraping. Contact data stays private and outside git.

## Run locally

From a clean checkout, install Python 3 and create a virtual environment. Dependencies are free; no service credentials are necessary for offline preparation.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/real_estate_workspace.py content-plan --start 2026-11-11 --audience "International property advisers"
.venv/bin/python scripts/real_estate_workspace.py clay-plan --domain example.org --limit 20
.venv/bin/python scripts/selftest.py --offline
```

The date and domain are examples, not a publication schedule or a real prospect search. Windows users can use `.venv\Scripts\python.exe` instead of `.venv/bin/python`. Do not run live API checks or model evaluations as part of the zero-cost workflow.

For activity recording, see [the ledger](linkedin-activity-ledger.md). For contact qualification and CSV export, see [the workspace workflow](real-estate-workspace.md). For source-based property analysis, see [market evidence](market-evidence.md). Keep output in ignored `testing/`; never push filled voice templates, prospect lists, browser sessions or message exports.

## Completion and review gates

- Verify a development branch can be written without changing `main`.
- Pass offline tests, secret checks, references and generated-package synchronization.
- Keep prospect decisions and actual outreach outcomes distinct; unresolved identities remain on hold.
- Keep the operational activity trail in Notion. The local ledger is optional and does not silently import or sync it.
- Review the Pull Request. Only the owner can authorize merging or publishing a release.

The system can be ready for operation while individual prospect verification and relationship development remain ongoing. A count of 20 is a maximum for an authorized outreach round, not a reason to force contact.

## Final step: prepare for another owner

Share the clean code branch and this guide only after the owner's review. Do not send the current Notion workspace, filled templates, private logs, contacts, API keys or session cookies. No message to another person is sent by this guide.

The recipient should create their own fork, work on a development branch, and first run only offline checks. This repository contains Awad-specific public example references; it is not automatically personalized for a new owner. Before real use, replace the owner identity, biography, signature, company facts, voice examples and market focus in the workspace and personal-brand references with truthful information. Preserve upstream MIT attribution. Never impersonate Awad or assume his approval transfers to another account.

The recipient needs their own supported account connections and their own explicit approval policy. Use private, independently authorized data. Paid providers and automatic execution remain disabled. Do not copy credentials or third-party contact histories between owners.
