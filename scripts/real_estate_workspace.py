#!/usr/bin/env python3
"""Prepare content briefs, Clay queries or qualified prospects offline. Never send/publish."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.real_estate_workspace import content_briefs, clay_search_plan, qualify_contacts, contacts_csv
from lib.activity_ledger import append_record, read_records, summary, export_csv
from lib.market_evidence import load_bundle, EvidenceError
from lib.market_data_import import summarize_csv
from lib.market_post_draft import build_market_post
from lib.quarterly_real_estate import analyze_quarters, QuarterlyDataError


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    content = sub.add_parser('content-plan')
    content.add_argument('--start', required=True, help='ISO date; dates are suggestions, not schedules')
    content.add_argument('--audience', required=True)
    content.add_argument('--notes', help='Optional local JSON array of source notes')
    clay = sub.add_parser('clay-plan')
    clay.add_argument('--domain', action='append', required=True)
    clay.add_argument('--limit', type=int, default=20)
    leads = sub.add_parser('qualify')
    leads.add_argument('--input', required=True, help='JSON contact array or Clay context with contacts')
    leads.add_argument('--existing', help='Existing JSON contact array or previous qualify result')
    leads.add_argument('--csv', action='store_true')
    evidence = sub.add_parser('review-evidence', help='Validate sourced draft; never publish')
    evidence.add_argument('--input', required=True, help='Local JSON with draft and claims')
    quarterly = sub.add_parser('quarterly-report', help='Analyze quarterly aggregate CSV without publishing')
    quarterly.add_argument('--input', required=True)
    quarterly.add_argument('--year', type=int)
    quarterly.add_argument('--transaction', default='Sales')
    post = sub.add_parser('market-post', help='Generate a source-linked review-only draft')
    post.add_argument('--input', required=True, help='JSON with draft and human-verified claims')
    post.add_argument('--audience', default='Dubai property investors')
    market = sub.add_parser('market-compare', help='Summarize a locally downloaded CSV, unverified')
    for name in ('input', 'date-column', 'amount-column', 'first-start', 'first-end', 'second-start', 'second-end', 'source-name', 'source-url', 'retrieved-on', 'published-on'):
        market.add_argument('--' + name, required=True)
    ledger = sub.add_parser('activity-log', help='Local single-writer append-only log; no network calls')
    ledger.add_argument('--ledger', required=True, help='Private JSONL path, e.g. testing/activity.jsonl')
    ledger.add_argument('--input', help='One activity JSON; omitted for read-only summary/export')
    ledger.add_argument('--csv', action='store_true')
    args = ap.parse_args(argv)
    read = lambda path: json.loads(Path(path).read_text(encoding='utf-8-sig'))
    try:
        if args.command == 'activity-log':
            if args.input and args.csv:
                raise ValueError('Append and export are separate operations.')
            if args.input:
                result = append_record(args.ledger, read(args.input))
            elif args.csv:
                print(export_csv(read_records(args.ledger)), end='')
                return 0
            else:
                result = summary(read_records(args.ledger))
        elif args.command == 'content-plan':
            notes = read(args.notes) if args.notes else []
            if not isinstance(notes, list) or any(not isinstance(x, str) for x in notes):
                raise ValueError('Notes must be a JSON array of strings.')
            result = content_briefs(args.start, args.audience, notes)
        elif args.command == 'market-compare':
            result = summarize_csv(args.input, date_column=args.date_column, amount_column=args.amount_column,
                                   first_start=args.first_start, first_end=args.first_end,
                                   second_start=args.second_start, second_end=args.second_end,
                                   source_name=args.source_name, source_url=args.source_url,
                                   retrieved_on=args.retrieved_on, published_on=args.published_on)
        elif args.command == 'quarterly-report':
            result = analyze_quarters(args.input, transaction=args.transaction, year=args.year)
        elif args.command == 'market-post':
            payload = read(args.input)
            result = build_market_post(payload['draft'], payload['claims'], audience=args.audience)
        elif args.command == 'review-evidence':
            result = load_bundle(args.input)
        elif args.command == 'clay-plan':
            result = clay_search_plan(args.domain, args.limit)
        else:
            data = read(args.input)
            existing = read(args.existing) if args.existing else []
            if isinstance(data, dict):
                data = data['contacts']
            if isinstance(existing, dict):
                existing = existing.get('contacts', []) + existing.get('existing', [])
            if not isinstance(data, list) or not isinstance(existing, list):
                raise ValueError('Contacts and existing history must be arrays.')
            result = qualify_contacts(data, existing)
            if args.csv:
                print(contacts_csv(result['contacts']), end='')
                return 0
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, EvidenceError) as exc:
        print('Invalid input: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
