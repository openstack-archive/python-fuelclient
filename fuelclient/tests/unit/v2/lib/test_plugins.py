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

import mock
import os
import tempfile

import fuelclient
from fuelclient.objects.plugins import BasePlugin
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestPluginsFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestPluginsFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/plugins'.format(version=self.version)

        self.fake_plugins = utils.get_fake_plugins(10)

        self.client = fuelclient.get_client('plugins', self.version)

    def test_plugins_list(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_plugins)
        self.client.get_all()
        self.assertTrue(self.res_uri, matcher.called)

    def test_install_plugin(self):
        expected_uri = '/api/{version}/plugins/upload'.format(
            version=self.version
        )
        matcher = self.m_request.post(expected_uri, json={})
        path = tempfile.mkstemp(suffix='.fp')[1]
        self.client.install(path)
        self.assertTrue(matcher.called)

        body = ' '.join(matcher.last_request.body.decode().split())

        uploaded = 'Content-Disposition: form-data; name="uploaded"; ' \
                   'filename="{0}"'.format(os.path.basename(path))
        self.assertTrue(uploaded in body)

        force = 'Content-Disposition: form-data; name="force" False'
        self.assertTrue(force in body)

    def test_install_plugin_with_force(self):
        expected_uri = '/api/{version}/plugins/upload'.format(
            version=self.version
        )
        matcher = self.m_request.post(expected_uri, json={})
        path = tempfile.mkstemp(suffix='.fp')[1]
        self.client.install(path, force=True)
        self.assertTrue(matcher.called)

        body = ' '.join(matcher.last_request.body.decode().split())

        uploaded = 'Content-Disposition: form-data; name="uploaded"; ' \
                   'filename="{0}"'.format(os.path.basename(path))
        self.assertTrue(uploaded in body)

        force = 'Content-Disposition: form-data; name="force" True'
        self.assertTrue(force in body)

    def test_remove_plugin(self):
        plugin = self.fake_plugins[3]
        expected_uri = '/api/{version}/plugins/{id}'.format(
            version=self.version, id=plugin['id']
        )
        matcher = self.m_request.delete(expected_uri, json={})
        with mock.patch.object(
                BasePlugin, '_get_plugin', return_value={'id': plugin['id']}):
            self.client.remove(plugin['name'], plugin['version'])
        self.assertTrue(matcher.called)
        self.assertIsNone(matcher.last_request.body)

    def test_sync_plugins(self):
        expected_uri = '/api/{version}/plugins/sync'.format(
            version=self.version
        )
        matcher = self.m_request.post(expected_uri, json={})
        self.client.sync(None)
        self.assertTrue(matcher.called)
        self.assertIsNone(matcher.last_request.body)

    def test_sync_plugins_empty_ids(self):
        expected_uri = '/api/{version}/plugins/sync'.format(
            version=self.version
        )
        matcher = self.m_request.post(expected_uri, json={})
        self.client.sync([])
        self.assertTrue(matcher.called)
        self.assertEqual([], matcher.last_request.json()['ids'])

    def test_sync_specified_plugins(self):
        expected_uri = '/api/{version}/plugins/sync'.format(
            version=self.version
        )
        ids = [1, 2]
        matcher = self.m_request.post(expected_uri, json={})
        self.client.sync(ids=ids)
        self.assertTrue(matcher.called)
        self.assertEqual(ids, matcher.last_request.json()['ids'])
