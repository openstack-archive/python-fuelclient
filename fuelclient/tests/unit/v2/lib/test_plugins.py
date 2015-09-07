# -*- coding: utf-8 -*-
#
#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api


class TestPluginsFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestPluginsFacade, self).setUp()

        self.version = 'v1'
        self.client = fuelclient.get_client('plugins', self.version)

    def test_sync_plugins(self):
        expected_uri = '/api/{version}/plugins/sync/'.format(
            version=self.version
        )
        matcher = self.m_request.post(expected_uri, json={})
        self.client.sync(None)
        self.assertTrue(matcher.called)
        self.assertIsNone(matcher.last_request.body)

    def test_sync_plugins_empty_ids(self):
        expected_uri = '/api/{version}/plugins/sync/'.format(
            version=self.version
        )
        matcher = self.m_request.post(expected_uri, json={})
        self.client.sync([])
        self.assertTrue(matcher.called)
        self.assertEqual([], matcher.last_request.json()['ids'])

    def test_sync_specified_plugins(self):
        expected_uri = '/api/{version}/plugins/sync/'.format(
            version=self.version
        )
        ids = [1, 2]
        matcher = self.m_request.post(expected_uri, json={})
        self.client.sync(ids=ids)
        self.assertTrue(matcher.called)
        self.assertEqual(ids, matcher.last_request.json()['ids'])
