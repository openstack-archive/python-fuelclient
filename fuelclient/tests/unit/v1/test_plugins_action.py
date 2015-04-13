# -*- coding: utf-8 -*-
#
#    Copyright 2014 Mirantis, Inc.
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

from mock import patch

from fuelclient.tests import base

from fuelclient.cli.actions import PluginAction
from fuelclient.cli import error
from fuelclient.cli.formatting import format_table
from fuelclient.cli.serializers import Serializer
from fuelclient.objects.plugins import Plugins


plugin_data = {
    'id': 1,
    'name': 'plugin_name',
    'version': '1.0.0',
    'package_version': '1.0.0'
}


class TestPluginsActions(base.UnitTestCase):

    def setUp(self):
        super(TestPluginsActions, self).setUp()
        self.file_name = '/tmp/path/plugin.fp'
        self.attr_name = 'plugin_name==version'
        self.name = 'plugin_name'
        self.version = 'version'

    def exec_plugins(self, actions):
        plugins_cmd = ['fuel', 'plugins']
        plugins_cmd.extend(actions)
        self.execute(plugins_cmd)

    def assert_print_table(self, print_mock, plugins):
        print_mock.assert_called_once_with(
            plugins, format_table(
                plugins,
                acceptable_keys=PluginAction.acceptable_keys))

    def assert_print(self, print_mock, result, msg):
        print_mock.assert_called_once_with(result, msg)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'get_all_data')
    def test_list_default(self, get_mock, print_mock):
        plugins = [plugin_data, plugin_data]
        get_mock.return_value = plugins

        self.exec_plugins([])

        get_mock.assert_called_once_with()
        self.assert_print_table(print_mock, plugins)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'get_all_data')
    def test_list(self, get_mock, print_mock):
        plugins = [plugin_data, plugin_data]
        get_mock.return_value = plugins

        self.exec_plugins(['--list'])

        get_mock.assert_called_once_with()
        self.assert_print_table(print_mock, plugins)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(PluginAction, 'check_file')
    @patch.object(Plugins, 'install', return_value='some_result')
    def test_install(self, install_mock, check_mock, print_mock):
        self.exec_plugins(['--install', self.file_name])
        self.assert_print(
            print_mock,
            'some_result',
            'Plugin /tmp/path/plugin.fp was successfully installed.')
        install_mock.assert_called_once_with(self.file_name, force=False)
        check_mock.assert_called_once_with(self.file_name)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'remove', return_value='some_result')
    def test_remove(self, remove_mock, print_mock):
        self.exec_plugins(['--remove', self.attr_name])
        self.assert_print(
            print_mock,
            'some_result',
            'Plugin plugin_name==version was successfully removed.')
        remove_mock.assert_called_once_with(self.name, self.version)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(PluginAction, 'check_file')
    @patch.object(Plugins, 'update', return_value='some_result')
    def test_update(self, update_mock, check_mock, print_mock):
        self.exec_plugins(['--update', self.file_name])
        self.assert_print(
            print_mock,
            'some_result',
            'Plugin /tmp/path/plugin.fp was successfully updated.')
        update_mock.assert_called_once_with(self.file_name)
        check_mock.assert_called_once_with(self.file_name)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(PluginAction, 'check_file')
    @patch.object(Plugins, 'downgrade', return_value='some_result')
    def test_downgrade(self, downgrade_mock, check_mock, print_mock):
        self.exec_plugins(['--downgrade', self.file_name])
        self.assert_print(
            print_mock,
            'some_result',
            'Plugin /tmp/path/plugin.fp was successfully downgraded.')
        downgrade_mock.assert_called_once_with(self.file_name)
        check_mock.assert_called_once_with(self.file_name)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'sync')
    def test_sync(self, sync_mock, print_mock):
        self.exec_plugins(['--sync'])
        self.assert_print(
            print_mock,
            None,
            'Plugins were successfully synchronized.')
        sync_mock.assert_called_once()

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'sync')
    def test_sync_with_specific_plugins(self, sync_mock, print_mock):
        self.exec_plugins(['--sync', '--plugin-id=1,2,3'])
        self.assert_print(
            print_mock,
            None,
            'Plugins were successfully synchronized.')
        sync_mock.assert_called_once_with(plugin_ids=[1, 2, 3])

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'register', return_value='some_result')
    def test_register(self, register_mock, print_mock):
        self.exec_plugins(['--register', 'plugin_name==version'])
        self.assert_print(
            print_mock,
            'some_result',
            'Plugin plugin_name==version was successfully registered.')
        register_mock.assert_called_once_with(
            self.name, self.version, force=False)

    @patch.object(Serializer, 'print_to_output')
    @patch.object(Plugins, 'unregister', return_value='some_result')
    def test_unregister(self, unregister_mock, print_mock):
        self.exec_plugins(['--unregister', 'plugin_name==version'])
        self.assert_print(
            print_mock,
            'some_result',
            'Plugin plugin_name==version was successfully unregistered.')
        unregister_mock.assert_called_once_with(self.name, self.version)

    def test_parse_name_version(self):
        plugin = PluginAction()
        self.assertEqual(
            plugin.parse_name_version('name==version'),
            ['name', 'version'])

    def test_parse_name_version_raises_error(self):
        plugin = PluginAction()
        self.assertRaisesRegexp(
            error.ArgumentException,
            'Syntax: fuel plugins <action> fuel_plugin==1.0.0',
            plugin.parse_name_version, 'some_string')

    @patch('fuelclient.utils.file_exists', return_value=True)
    def test_check_file(self, _):
        plugin = PluginAction()
        plugin.check_file(self.file_name)

    @patch('fuelclient.utils.file_exists', return_value=False)
    def test_check_file_raises_error(self, _):
        plugin = PluginAction()
        self.assertRaisesRegexp(
            error.ArgumentException,
            'File "/tmp/path/plugin.fp" does not exists',
            plugin.check_file, self.file_name)
