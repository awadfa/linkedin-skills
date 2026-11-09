#!/usr/bin/env python3
"""Prepare content briefs, Clay queries or qualified prospects offline. Never send/publish."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.real_estate_workspace import content_briefs, clay_search_plan, qualify_contacts, contacts_csv
from lib.market_evidence import load_bundle, EvidenceError


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
    args = ap.parse_args(argv)
    read = lambda path: json.loads(Path(path).read_text(encoding='utf-8-sig'))
    try:
        if args.command == 'content-plan':
            notes = read(args.notes) if args.notes else []
            if not isinstance(notes, list) or any(not isinstance(x, str) for x in notes):
                raise ValueError('Notes must be a JSON array of strings.')
            result = content_briefs(args.start, args.audience, notes)
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
