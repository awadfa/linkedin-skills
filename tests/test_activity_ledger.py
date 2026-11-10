import tempfile
import unittest
from pathlib import Path
from lib.activity_ledger import append_record, read_records, summary, export_csv


class ActivityLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'activity.jsonl'
        self.row = dict(activity_id='example-1', actor='Example owner', source='user supplied',
                        dedupe_key='example-comment', occurred_at='2026-11-10T12:00:00+00:00',
                        action='comment', status='attempted', exact_text='A fictional comment.')

    def test_unconfirmed_is_not_counted_as_sent(self):
        append_record(self.path, self.row)
        self.assertEqual(summary(read_records(self.path))['verified_by_action']['comment'], 0)
        self.assertEqual(summary(read_records(self.path))['unconfirmed'], 1)

    def test_verification_needs_evidence_and_timezone(self):
        for changes in ({'status': 'verified'}, {'occurred_at': '2026-11-10T12:00:00'}):
            with self.assertRaises(ValueError):
                append_record(self.path, dict(self.row, **changes))
        self.assertFalse(self.path.exists())

    def test_duplicate_rejected_without_changing_file(self):
        append_record(self.path, self.row)
        before = self.path.read_bytes()
        for change in ({}, {'activity_id': 'other'}):
            with self.assertRaises(ValueError):
                append_record(self.path, dict(self.row, **change))
        self.assertEqual(before, self.path.read_bytes())

    def test_correction_preserves_text_and_counts_once(self):
        append_record(self.path, self.row)
        correction = dict(self.row, activity_id='example-2', supersedes='example-1',
                          correction_reason='Visible confirmation obtained', status='verified',
                          verification_evidence='Owner supplied confirmation')
        append_record(self.path, correction)
        records = read_records(self.path)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['status'], 'attempted')
        self.assertEqual(summary(records)['verified_by_action']['comment'], 1)
        with self.assertRaises(ValueError):
            append_record(self.path, dict(correction, activity_id='example-3'))

    def test_export_formula_escape_does_not_mutate_original(self):
        append_record(self.path, dict(self.row, exact_text='=example'))
        records = read_records(self.path)
        self.assertIn("'=example", export_csv(records))
        self.assertEqual(records[0]['exact_text'], '=example')

    def test_reaction_requires_type_and_no_text(self):
        with self.assertRaises(ValueError):
            append_record(self.path, dict(self.row, action='reaction'))
        append_record(self.path, dict(self.row, action='reaction', exact_text=None, reaction_type='Like'))
