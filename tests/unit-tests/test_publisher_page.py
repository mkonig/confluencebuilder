# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from collections import defaultdict
from sphinxcontrib.confluencebuilder.publisher import CB_PROP_KEY
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import autocleanup_publisher
from tests.lib import mock_confluence_instance
from tests.lib import prepare_conf_publisher
import unittest


class TestConfluencePublisherPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf_publisher()
        cls.config.confluence_space_key = 'MOCK'

        cls.std_space_connect_rsp = {
            'id': 1,
            'key': 'MOCK',
            'name': 'Mock Space',
            'type': 'global',
        }

    def test_publisher_page_store_page_id_allow_watch(self):
        """validate publisher will store a page by id (watch)"""
        #
        # Verify that a publisher can update an existing page by an
        # identifier value. Instance will be configured to watch content,
        # so any page updates should not trigger an watch event.

        config = self.config.clone()
        config.confluence_watch = True

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page id fetch
            expected_page_id = 7456
            mocked_version = 28

            page_fetch_rsp = {
                'id': str(expected_page_id),
                'title': 'mock page',
                'type': 'page',
                'version': {
                    'number': str(mocked_version),
                },
            }
            daemon.register_get_rsp(200, page_fetch_rsp)

            # prepare response for properties fetch
            scb_fetch_props_rsp = {
                'id': '1234',
                'key': CB_PROP_KEY,
                'value': {},
                'version': {
                    'number': '1',
                },
            }
            daemon.register_get_rsp(200, scb_fetch_props_rsp)  # initial
            daemon.register_get_rsp(200, scb_fetch_props_rsp)  # re-fetch

            # prepare response for update event
            daemon.register_put_rsp(200, dict(page_fetch_rsp))

            # prepare response for updated properties
            scb_updated_props_rsp = {
                'id': '1234',
                'key': CB_PROP_KEY,
                'value': {},
                'version': {
                    'number': '2',
                },
            }
            daemon.register_put_rsp(200, scb_updated_props_rsp)

            # perform page update request
            data = defaultdict(str)
            data['content'] = 'dummy page data'
            page_id = publisher.store_page_by_id(
                'dummy-name', expected_page_id, data)

            # check expected page id returned
            self.assertEqual(page_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = f'/rest/api/content/{expected_page_id}?'
            self.assertTrue(req_path.startswith(expected_request))

            # check that an update request is processed
            update_req = daemon.pop_put_request()
            self.assertIsNotNone(update_req)

            # check that the property request on the page was done
            props_fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(props_fetch_req)

            props_fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(props_fetch_req)

            # check that the page property (e.g. hash update) was made
            update_req = daemon.pop_put_request()
            self.assertIsNotNone(update_req)
            req_path, _ = update_req
            self.assertTrue(req_path.endswith(CB_PROP_KEY))

            # verify that no other request was made
            daemon.check_unhandled_requests()

    def test_publisher_page_store_page_id_default(self):
        """validate publisher will store a page by id (default)"""
        #
        # Verify that a publisher can update an existing page by an
        # identifier value. By default, the update request will ensure
        # the user configures to not watch the page.

        with mock_confluence_instance(self.config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(self.config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page id fetch
            expected_page_id = 4568
            mocked_version = 45

            page_fetch_rsp = {
                'id': str(expected_page_id),
                'title': 'mock page',
                'type': 'page',
                'version': {
                    'number': str(mocked_version),
                },
            }
            daemon.register_get_rsp(200, page_fetch_rsp)

            # prepare response for properties fetch
            scb_fetch_props_rsp = {
                'id': '1234',
                'key': CB_PROP_KEY,
                'value': {},
                'version': {
                    'number': '1',
                },
            }
            daemon.register_get_rsp(200, scb_fetch_props_rsp)  # initial
            daemon.register_get_rsp(200, scb_fetch_props_rsp)  # re-fetch

            # prepare response for update event
            daemon.register_put_rsp(200, dict(page_fetch_rsp))

            # prepare response for updated properties
            scb_updated_props_rsp = {
                'id': '1234',
                'key': CB_PROP_KEY,
                'value': {},
                'version': {
                    'number': '2',
                },
            }
            daemon.register_put_rsp(200, scb_updated_props_rsp)

            # prepare response for unwatch event
            daemon.register_delete_rsp(200)

            # perform page update request
            data = defaultdict(str)
            data['content'] = 'dummy page data'
            page_id = publisher.store_page_by_id(
                'dummy-name', expected_page_id, data)

            # check expected page id returned
            self.assertEqual(page_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = f'/rest/api/content/{expected_page_id}?'
            self.assertTrue(req_path.startswith(expected_request))

            # check that an update request is processed
            update_req = daemon.pop_put_request()
            self.assertIsNotNone(update_req)

            # check that the property request on the page was done
            props_fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(props_fetch_req)

            props_fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(props_fetch_req)

            # check that the page property (e.g. hash update) was made
            update_req = daemon.pop_put_request()
            self.assertIsNotNone(update_req)
            req_path, _ = update_req
            self.assertTrue(req_path.endswith(CB_PROP_KEY))

            # check that the page is unwatched
            unwatch_req = daemon.pop_delete_request()
            self.assertIsNotNone(unwatch_req)
            req_path, _ = unwatch_req
            ereq = f'/rest/api/user/watch/content/{expected_page_id}'
            self.assertEqual(req_path, ereq)

            # verify that no other request was made
            daemon.check_unhandled_requests()

    def test_publisher_page_store_page_id_dryrun(self):
        """validate publisher suppress store a page by id with dryrun"""
        #
        # Verify that a publisher will handle a id-page update request
        # properly when the dryrun flag is set.

        config = self.config.clone()
        config.confluence_publish_dryrun = True

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page id fetch
            expected_page_id = 2

            page_rsp = {
                'id': expected_page_id,
                'title': 'mock page',
                'type': 'page',
            }
            daemon.register_get_rsp(200, page_rsp)

            page_id = publisher.store_page_by_id(
                'dummy-name', expected_page_id, {})

            # check expected page id returned
            self.assertEqual(page_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = f'/rest/api/content/{expected_page_id}?'
            self.assertTrue(req_path.startswith(expected_request))

            # verify that no update request was made
            daemon.check_unhandled_requests()
