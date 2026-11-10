"""Offline, append-only activity records. This module never contacts LinkedIn."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

ACTIONS = {'post', 'comment', 'reply', 'reaction', 'repost', 'connection_request', 'direct_message'}
STATUSES = {'draft', 'approved', 'attempted', 'verified', 'failed', 'uncertain'}


def read_records(path):
    file = Path(path)
    return [json.loads(line) for line in file.read_text(encoding='utf-8').splitlines() if line.strip()] if file.exists() else []


def append_record(path, record):
    """Single-writer local log. Corrections are new records, never replacements."""
    if not isinstance(record, dict):
        raise ValueError('Activity must be an object.')
    row = dict(record)
    for key in ('activity_id', 'actor', 'source', 'dedupe_key'):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError('Required nonempty field: ' + key)
    if row.get('action') not in ACTIONS or row.get('status') not in STATUSES:
        raise ValueError('Unknown action or status.')
    occurred = row.get('occurred_at')
    if occurred != 'unknown':
        try:
            timestamp = datetime.fromisoformat(occurred.replace('Z', '+00:00'))
            if timestamp.utcoffset() is None:
                raise ValueError('Timestamp requires timezone.')
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError('occurred_at requires timezone or unknown.') from exc
    if row['action'] == 'reaction':
        if row.get('exact_text') is not None or not row.get('reaction_type'):
            raise ValueError('Reactions require reaction_type and null exact_text.')
    elif not isinstance(row.get('exact_text'), str) or not row['exact_text'].strip():
        raise ValueError('Preserve exact outgoing text.')
    if row['status'] == 'verified' and not str(row.get('verification_evidence') or '').strip():
        raise ValueError('Verified actions require evidence.')
    prior = read_records(path)
    if any(r['activity_id'] == row['activity_id'] for r in prior):
        raise ValueError('Duplicate activity_id.')
    correction = row.get('supersedes')
    if correction:
        previous = next((r for r in prior if r['activity_id'] == correction), None)
        if not previous or previous['dedupe_key'] != row['dedupe_key']:
            raise ValueError('Corrections must reference the same existing activity.')
        if not str(row.get('correction_reason') or '').strip():
            raise ValueError('Corrections require a reason.')
        if any(r.get('supersedes') == correction for r in prior):
            raise ValueError('Correct the latest record, not an older revision.')
    elif any(r['dedupe_key'] == row['dedupe_key'] for r in prior):
        raise ValueError('Duplicate activity; append an explicit correction.')
    row['recorded_at'] = datetime.now(timezone.utc).isoformat()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    return row


def latest_records(records):
    superseded = {r.get('supersedes') for r in records}
    return [r for r in records if r['activity_id'] not in superseded]


def summary(records):
    rows = latest_records(records)
    return {'records': len(records), 'current_activities': len(rows),
            'verified_by_action': {action: sum(r['action'] == action and r['status'] == 'verified' for r in rows)
                                   for action in sorted(ACTIONS)},
            'unconfirmed': sum(r['status'] in {'attempted', 'uncertain'} for r in rows)}


def export_csv(records):
    rows = latest_records(records)
    fields = sorted({key for row in rows for key in row})
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        safe = {}
        for key, value in row.items():
            text = '' if value is None else str(value)
            safe[key] = "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text
        writer.writerow(safe)
    return out.getvalue()
