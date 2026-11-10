# LinkedIn Activity Ledger — specification (v1)

Status: Offline JSONL append/export implementation available. No LinkedIn integration, automated capture, or backfill is claimed.
Owner: Awad. Scope: personal professional LinkedIn activity. Zero-cost by default.

## Purpose
Keep a reviewable, append-only audit trail of what was actually done on LinkedIn, where, when, to whom, and in what exact words. Enable the owner to decide whether each interaction reflects their personal voice.

## Record schema
- activity_id: stable unique identifier
- occurred_at: timestamp with timezone (or unknown)
- actor: account/person executing
- action: post | comment | reply | reaction | repost | connection_request | direct_message
- target_name, target_profile_url (when available)
- original_post_url, original_post_author, original_post_excerpt (if available and permissible)
- activity_permalink (comment/post URL if available)
- exact_text: verbatim outgoing content; null for reactions
- reaction_type: Like/Celebrate/etc., if applicable
- status: draft | approved | attempted | verified | failed | uncertain
- verification_evidence: URL or description of visible confirmation, never fabricate
- source: Work browser | user supplied | import
- campaign_or_goal: optional
- voice_review: pending | matches | revise | reject
- voice_review_notes: owner's feedback
- preferred_rewrite: optional, never replace exact_text
- recorded_at, last_reviewed_at
- dedupe_key: action + target URL + activity URL (or conservative fallback)

## Rules
1. Record every confirmed outbound interaction, including likes and comments; attempted/uncertain actions remain distinctly marked.
2. Capture exact message/comment text and target URL at execution time; do not infer text from a draft.
3. Do not claim the full historical account was backfilled. Prior known interactions can be imported as partial records, explicitly tagged 'historical/partial'.
4. Never silently overwrite or erase original content; append corrections and review outcomes.
5. Do not duplicate actions; check the ledger and LinkedIn thread before sending.
6. No unauthorized scraping, mass messaging, or bypassing platform restrictions.
7. Protect third-party personal information; minimize stored data, avoid client secrets and company-owned contact datasets.
8. Notion is the current operational log; GitHub contains schema/code, not private messages or private customer data.
9. Publishing and first-time outbound messages require owner approval under current project policy.
10. Provide weekly review grouped by: published posts, comments/replies, reactions, connection requests, DMs, voice mismatches, and verified outcomes.

## Offline implementation

Use `scripts/real_estate_workspace.py activity-log --ledger testing/activity.jsonl --input testing/activity.json` to append one user-reviewed record. Omit `--input` for a summary; use `--csv` for a Google Sheets-compatible export. These operations make no network calls. Keep actual records in ignored `testing/` or a private folder outside the repository.

The CLI enforces required identity/source/deduplication fields, timezone or explicit `unknown`, exact text, reaction type and evidence for verified actions. Other schema fields are supplied by the operator when available. A human must assess whether evidence is truthful and whether a dedupe key identifies the same action. The tool cannot verify a LinkedIn send or detect differently keyed duplicates.

Corrections append a new unique `activity_id` with `supersedes` pointing to the latest record, the same `dedupe_key`, and a nonempty `correction_reason`. Never overwrite the original. Summary/export uses only the latest revision and counts only `verified` actions as completed. Review feedback can be appended this way without replacing verbatim text. JSONL retains the full history; CSV escapes formula-leading cells without changing the stored text.

Single-writer local use only; concurrent writers are unsupported. Back up private logs separately. Notion remains the operational source for previously recorded activity; no automatic synchronization or historical import has occurred.
