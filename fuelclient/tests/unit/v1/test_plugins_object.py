# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

from fuelclient.cli import error
from fuelclient.objects.plugins import BasePlugin
from fuelclient.objects.plugins import Plugins
from fuelclient.objects.plugins import PluginV1
from fuelclient.objects.plugins import PluginV2
from fuelclient.tests.unit.v1 import base


class TestBasePlugin(base.UnitTestCase):

    def setUp(self):
        super(TestBasePlugin, self).setUp()
        self.plugin = BasePlugin

    def test_get_plugin(self):
        with mock.patch.object(self.plugin, 'get_all_data') as get_mock:
            get_mock.return_value = [
                {'name': 'name1', 'version': '1.0.0'},
                {'name': 'name2', 'version': '1.0.1'},
                {'name': 'name2', 'version': '1.0.0'}]
            self.assertEqual(self.plugin._get_plugin('name2', '1.0.0'),
                             {'name': 'name2', 'version': '1.0.0'})


class TestPluginsObject(base.UnitTestCase):

    def setUp(self):
        super(TestPluginsObject, self).setUp()
        self.plugin = Plugins
        self.name = 'plugin_name'
        self.version = 'plugin_version'
        self.path_v1 = '/tmp/plugin_name-1.2.0.fp'
        self.path_v2 = '/tmp/plugin_name-1.2-1.2.0-1.noarch.rpm'

    @mock.patch.object(BasePlugin.connection, 'post_upload_file_raw')
    def test_install(self, post_mock):
        self.plugin().install(self.path_v1)
        post_mock.assert_called_once_with('plugins/upload', self.path_v1,
                                          data={'force': False})

    @mock.patch.object(BasePlugin.connection, 'post_upload_file_raw')
    def test_install_with_force(self, post_mock):
        self.plugin().install(self.path_v1, force=True)
        post_mock.assert_called_once_with('plugins/upload', self.path_v1,
                                          data={'force': True})

    @mock.patch.object(BasePlugin.connection, 'delete_request')
    @mock.patch.object(BasePlugin, '_get_plugin', return_value={'id': 123})
    def test_remove(self, get_mock, del_mock):
        self.plugin().remove(self.name, self.version)
        get_mock.assert_called_once_with(self.name, self.version)
        del_mock.assert_called_once_with('plugins/123')

    @mock.patch.object(BasePlugin.connection, 'post_request')
    def test_sync(self, post_mock):
        self.plugin().sync()
        post_mock.assert_called_once_with('plugins/sync', data=None)

    @mock.patch.object(BasePlugin.connection, 'post_request')
    def test_sync_with_specific_plugins(self, post_mock):
        self.plugin().sync(plugin_ids=[1, 2])
        data = {'ids': [1, 2]}
        post_mock.assert_called_once_with('plugins/sync', data=data)

    def test_get_obj(self):
        plugin = self.plugin()
        self.assertEqual(plugin._get_obj(self.path_v1), PluginV1)
        self.assertEqual(plugin._get_obj(self.path_v2), PluginV2)
        with self.assertRaisesRegexp(
                error.BadDataException,
                "Plugin 'file-name.ext' has unsupported format 'ext'."):
            plugin._get_obj('file-name.ext')
