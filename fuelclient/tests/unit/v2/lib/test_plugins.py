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
import json

from mock import mock

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestPluginsFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestPluginsFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/plugins/'.format(version=self.version)

        self.fake_plugins = utils.get_fake_plugins(10)

        self.client = fuelclient.get_client('plugins', self.version)

    def test_plugins_list(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_plugins)
        self.client.get_all()
        self.assertTrue(self.res_uri, matcher.called)

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


class TestPluginInstallFacade(TestPluginsFacade):

    def setUp(self):
        super(TestPluginInstallFacade, self).setUp()

        self.m_exec_result = None
        self.m_exec = mock.patch.object(fuelclient.utils, 'exec_cmd',
                                        return_value=self.m_exec_result)
        self.m_is_master = mock.patch.object(fuelclient.objects.plugins,
                                             'raise_error_if_not_master')
        self.m_meta = mock.patch.object(fuelclient.utils,
                                        'glob_and_parse_yaml',
                                        return_value=self.fake_plugins)

    def test_install_plugin(self):
        path = '/path/to/plugin.rpm'

        post_matcher = self.m_request.post(self.res_uri, json={})
        get_matcher = self.m_request.get(self.res_uri, json={})
        fake_plugin = self.fake_plugins[0]
        m_name = mock.patch.object(fuelclient.objects.plugins.PluginV2,
                                   'name_from_file',
                                   return_value=fake_plugin['name'])
        m_version = mock.patch.object(fuelclient.objects.plugins.PluginV2,
                                      'version_from_file',
                                      return_value=fake_plugin['version'])

        with m_name, m_version, self.m_is_master, self.m_meta, self.m_exec:
            self.client.install(path)

        self.assertTrue(get_matcher.called)
        self.assertTrue(post_matcher.called)
        self.assertEqual(fake_plugin,
                         json.loads(post_matcher.last_request.body))


class TestPluginRemoveFacade(TestPluginsFacade):

    def setUp(self):
        super(TestPluginRemoveFacade, self).setUp()

        self.m_exec_result = None
        self.m_exec = mock.patch.object(fuelclient.utils, 'exec_cmd',
                                        return_value=self.m_exec_result)
        self.m_is_master = mock.patch.object(fuelclient.objects.plugins,
                                             'raise_error_if_not_master')

    def test_remove_plugin(self):

        fake_plugin = self.fake_plugins[0]
        expected_uri = '/api/{version}/plugins/{id}'.format(
            version=self.version, id=fake_plugin['id'])

        del_matcher = self.m_request.delete(expected_uri, json={})
        get_matcher = self.m_request.get(self.res_uri, json=self.fake_plugins)

        with self.m_is_master, self.m_exec:
            self.client.remove(fake_plugin['name'], fake_plugin['version'])

        self.assertTrue(get_matcher.called)
        self.assertTrue(del_matcher.called)
        self.assertIsNone(del_matcher.last_request.body)
