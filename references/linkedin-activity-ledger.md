# LinkedIn Activity Ledger — specification (v1)

Status: SPECIFICATION ONLY. No LinkedIn integration, automated capture, or backfill is claimed.
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

## First implementation milestone
Create a Notion activity log using the fields above, have Work capture each action immediately, then build a read-only export/review view. Start with the previously verified Michael Francis comment and 20 reactions as *partial historical entries*, without inventing missing URLs.
