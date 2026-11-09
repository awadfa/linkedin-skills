import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from lib.real_estate_workspace import (content_briefs, clay_search_plan,
                                       qualify_contacts, contacts_csv)
from lib.workspace_policy import guarded_session, WorkspacePolicyError, zero_cost_mode

ROOT = Path(__file__).resolve().parents[1]


def person(**overrides):
    return dict({'name': 'Example Agent', 'latest_experience_company': 'Example Agency',
                 'latest_experience_title': 'Football Agent',
                 'url': 'https://uk.linkedin.com/in/example-agent/?trk=foo'}, **overrides)


class RealEstateWorkspace(unittest.TestCase):
    def test_default_blocks_services_even_when_credentials_exist(self):
        from lib import backend_selector
        with patch.dict(os.environ, {'PUBLORA_API_KEY': 'test', 'LINKEDIN_PLATFORM_ID': 'test',
                                    'PIXFARO_TOKEN': 'test', 'APIFY_TOKEN': 'test',
                                    'LINKEDIN_SKILLS_CUSTOM_POSTER': 'unexpected'}, clear=True), \
             patch('requests.sessions.Session.request') as request, \
             patch('subprocess.run') as run:
            self.assertTrue(zero_cost_mode())
            self.assertEqual(backend_selector.active_backend(), 'manual')
            self.assertEqual(backend_selector.image_backend(), 'manual')
            self.assertIsNone(backend_selector.fetch_post('https://www.linkedin.com/in/example'))
            self.assertEqual(backend_selector.publish('post', 'review me', 'target')['mode'], 'manual')
            with self.assertRaises(WorkspacePolicyError):
                guarded_session().post('https://api.example.com', json={'test': True})
            request.assert_not_called()
            run.assert_not_called()

    def test_direct_clients_use_the_guarded_transport(self):
        from lib.apify_client import ApifyClient
        from lib.publora_client import PubloraClient
        from lib.pixfaro_client import PixfaroClient
        with patch.dict(os.environ, {}, clear=True), patch('requests.sessions.Session.request') as request:
            for client in (ApifyClient(token='test'), PubloraClient(api_key='test'), PixfaroClient(api_key='test')):
                with self.assertRaises(WorkspacePolicyError):
                    client._session.get('https://api.example.com')
            request.assert_not_called()

    def test_unknown_profile_is_closed(self):
        with patch.dict(os.environ, {'LINKEDIN_SKILLS_PROFILE': 'typo'}):
            self.assertTrue(zero_cost_mode())

    def test_briefs_are_unscheduled_and_do_not_invent_posts(self):
        result = content_briefs('2026-11-09', 'International advisers')
        self.assertEqual(len(result['posts']), 3)
        self.assertEqual(result['posts'][-1]['date'], '2026-11-13')
        self.assertFalse(result['scheduled'])
        self.assertTrue(all(p['review_required'] and not p['draft'] for p in result['posts']))

    def test_clay_plan_is_only_a_bounded_read_query(self):
        result = clay_search_plan(['uniquesg.com', 'uniquesg.com'])
        self.assertFalse(result['executed'])
        self.assertEqual(result['arguments']['companyIdentifiers'], ['uniquesg.com'])
        self.assertIn('is_current = true', result['arguments']['dslQuery'])
        for domains, limit in [(['x.com" or true'], 20), ([], 20), (['example.com'], 0), (['example.com'], True)]:
            with self.assertRaises(ValueError):
                clay_search_plan(domains, limit)

    def test_canonical_duplicates_and_existing_outreach_never_reenter(self):
        history = [person(status='Message sent')]
        result = qualify_contacts([person(url='https://www.linkedin.com/in/example-agent'),
                                   person(name='Second', url='https://www.linkedin.com/in/second'),
                                   person(name='Second', url='https://nl.linkedin.com/in/second/')], history)
        self.assertEqual([r['name'] for r in result['contacts']], ['Second'])
        self.assertEqual(len(result['excluded']), 2)
        self.assertEqual(result['existing'][0]['status'], 'Message sent')
        again = qualify_contacts([person()], result['existing'] + result['contacts'])
        self.assertEqual(again['contacts'], [])

    def test_invalid_history_fails_instead_of_being_lost(self):
        with self.assertRaises(ValueError):
            qualify_contacts([person()], [person(status='pending-ish')])

    def test_unverified_email_removed_and_formula_escaped(self):
        result = qualify_contacts([person(name='=HYPERLINK("bad")', email='guess@example.com')])
        self.assertEqual(result['contacts'][0]['email'], '')
        self.assertIn("'=HYPERLINK", contacts_csv(result['contacts']))

    def test_source_review_retains_professional_email_without_delivery_claim(self):
        result = qualify_contacts([person(email='agent@example.com', email_verified=True,
                                           email_source_url='https://example.com/team')])
        self.assertEqual(result['contacts'][0]['email'], 'agent@example.com')
        self.assertIn('delivery untested', result['contacts'][0]['email_verification'])
        again = qualify_contacts([], result['contacts'])
        self.assertEqual(again['existing'][0]['email'], 'agent@example.com')

    def test_malformed_record_is_rejected(self):
        with self.assertRaises(ValueError):
            qualify_contacts(['not a contact'])

    def test_cli_works_without_site_packages(self):
        run = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts/real_estate_workspace.py'),
                              'clay-plan', '--domain', 'example.com'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertFalse(json.loads(run.stdout)['executed'])

    def test_cli_rejects_send_operation(self):
        run = subprocess.run([sys.executable, str(ROOT / 'scripts/real_estate_workspace.py'), 'publish'],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)


if __name__ == '__main__':
    unittest.main()
