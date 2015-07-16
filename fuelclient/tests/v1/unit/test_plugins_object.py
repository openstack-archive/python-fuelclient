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

from mock import MagicMock
from mock import patch

from fuelclient.cli import error
from fuelclient.objects.plugins import Plugins
from fuelclient.objects.plugins import PluginV1
from fuelclient.objects.plugins import PluginV2
from fuelclient.tests import base


@patch('fuelclient.objects.plugins.raise_error_if_not_master')
class TestPluginV1(base.UnitTestCase):

    fake_meta = """
    name: 'plugin_name'
    version: 'version'
    """

    def setUp(self):
        super(TestPluginV1, self).setUp()
        self.plugin = PluginV1
        self.path = '/tmp/plugin/path'
        self.name = 'plugin_name'
        self.version = 'version'

    @patch('fuelclient.objects.plugins.tarfile')
    def test_install(self, tar_mock, master_only_mock):
        tar_obj = MagicMock()
        tar_mock.open.return_value = tar_obj

        self.plugin.install(self.path)

        master_only_mock.assert_called_once_with()
        tar_obj.extractall.assert_called_once_with('/var/www/nailgun/plugins/')
        tar_obj.close.assert_called_once_with()

    @patch('fuelclient.objects.plugins.shutil.rmtree')
    def test_remove(self, rmtree_mock, master_only_mock):
        self.plugin.remove(self.name, self.version)

        master_only_mock.assert_called_once_with()
        rmtree_mock.assert_called_once_with(
            '/var/www/nailgun/plugins/plugin_name-version')

    def test_update(self, _):
        self.assertRaisesRegexp(
            error.BadDataException,
            'Update action is not supported for old plugins with '
            'package version "1.0.0", you can install your plugin '
            'or use newer plugin format.',
            self.plugin.update, 'some_string')

    def test_downgrade(self, _):
        self.assertRaisesRegexp(
            error.BadDataException,
            'Downgrade action is not supported for old plugins with '
            'package version "1.0.0", you can install your plugin '
            'or use newer plugin format.',
            self.plugin.downgrade, 'some_string')

    def mock_tar(self, tar_mock):
        tar_obj = MagicMock()
        tar_mock.open.return_value = tar_obj
        tar_file = MagicMock()
        tar_obj.getnames.return_value = ['metadata.yaml']
        tar_obj.extractfile.return_value = tar_file
        tar_file.read.return_value = self.fake_meta

    @patch('fuelclient.objects.plugins.tarfile')
    def test_name_from_file(self, tar_mock, _):
        self.mock_tar(tar_mock)

        self.assertEqual(
            self.plugin.name_from_file(self.path),
            self.name)

    @patch('fuelclient.objects.plugins.tarfile')
    def test_version_from_file(self, tar_mock, _):
        self.mock_tar(tar_mock)

        self.assertEqual(
            self.plugin.version_from_file(self.path),
            self.version)


@patch('fuelclient.objects.plugins.raise_error_if_not_master')
class TestPluginV2(base.UnitTestCase):

    def setUp(self):
        super(TestPluginV2, self).setUp()
        self.plugin = PluginV2
        self.path = '/tmp/plugin/path'
        self.name = 'plugin_name'
        self.version = '1.2.3'

    @patch('fuelclient.objects.plugins.utils.exec_cmd')
    def test_install(self, exec_mock, master_only_mock):
        self.plugin.install(self.path)

        exec_mock.assert_called_once_with('yum -y install /tmp/plugin/path')
        master_only_mock.assert_called_once_with()

    @patch('fuelclient.objects.plugins.utils.exec_cmd')
    def test_install_w_force(self, exec_mock, master_only_mock):
        self.plugin.install(self.path, force=True)

        exec_mock.assert_called_once_with(
            'yum -y install /tmp/plugin/path'
            ' || yum -y reinstall /tmp/plugin/path')
        master_only_mock.assert_called_once_with()

    @patch('fuelclient.objects.plugins.utils.exec_cmd')
    def test_remove(self, exec_mock, master_only_mock):
        self.plugin.remove(self.name, self.version)

        exec_mock.assert_called_once_with('yum -y remove plugin_name-1.2')
        master_only_mock.assert_called_once_with()

    @patch('fuelclient.objects.plugins.utils.exec_cmd')
    def test_update(self, exec_mock, master_only_mock):
        self.plugin.update(self.path)

        exec_mock.assert_called_once_with('yum -y update /tmp/plugin/path')
        master_only_mock.assert_called_once_with()

    @patch('fuelclient.objects.plugins.utils.exec_cmd')
    def test_downgrade(self, exec_mock, master_only_mock):
        self.plugin.downgrade(self.path)

        exec_mock.assert_called_once_with('yum -y downgrade /tmp/plugin/path')
        master_only_mock.assert_called_once_with()

    @patch('fuelclient.objects.plugins.utils.exec_cmd_iterator',
           return_value=['plugin_name-1.2'])
    def test_name_from_file(self, exec_mock, _):
        self.assertEqual(
            self.plugin.name_from_file(self.path),
            self.name)

        exec_mock.assert_called_once_with(
            "rpm -qp --queryformat '%{name}' /tmp/plugin/path")

    @patch('fuelclient.objects.plugins.utils.exec_cmd_iterator',
           return_value=['1.2.3'])
    def test_version_from_file(self, exec_mock, _):
        self.assertEqual(
            self.plugin.version_from_file(self.path),
            self.version)

        exec_mock.assert_called_once_with(
            "rpm -qp --queryformat '%{version}' /tmp/plugin/path")


class TestPluginsObject(base.UnitTestCase):

    def setUp(self):
        super(TestPluginsObject, self).setUp()
        self.plugin = Plugins
        self.path = '/tmp/plugin/path'
        self.name = 'plugin_name'
        self.version = 'version'

    def mock_make_obj_by_file(self, make_obj_by_file_mock):
        plugin_obj = MagicMock()
        plugin_obj.name_from_file.return_value = 'retrieved_name'
        plugin_obj.version_from_file.return_value = 'retrieved_version'
        make_obj_by_file_mock.return_value = plugin_obj

        return plugin_obj

    @patch('fuelclient.utils.glob_and_parse_yaml',
           return_value=[
               {'name': 'name1', 'version': 'version1'},
               {'name': 'name2', 'version': 'version2'},
               {'name': 'name3', 'version': 'version3'}])
    @patch.object(Plugins, 'update_or_create')
    def test_register(self, up_or_create_mock, glob_parse_mock):
        self.plugin.register('name3', 'version3')
        glob_parse_mock.assert_called_once_with(
            '/var/www/nailgun/plugins/*/metadata.yaml')
        up_or_create_mock.assert_called_once_with(
            {'name': 'name3', 'version': 'version3'},
            force=False)

    @patch('fuelclient.utils.glob_and_parse_yaml', return_value=[])
    def test_register_raises_error(self, glob_parse_mock):
        self.assertRaisesRegexp(
            error.BadDataException,
            'Plugin name3 with version version3 does '
            'not exist, install it and try again',
            self.plugin.register, 'name3', 'version3')

        glob_parse_mock.assert_called_once_with(
            '/var/www/nailgun/plugins/*/metadata.yaml')

    @patch.object(Plugins, 'get_plugin', return_value={'id': 123})
    @patch.object(Plugins.connection, 'delete_request')
    def test_unregister(self, del_mock, get_mock):
        self.plugin.unregister(self.name, self.version)
        get_mock.assert_called_once_with(self.name, self.version)
        del_mock.assert_called_once_with('plugins/123')

    @patch.object(Plugins, 'sync')
    @patch.object(Plugins, 'register')
    @patch.object(Plugins, 'make_obj_by_file')
    def test_install(self, make_obj_by_file_mock, register_mock, sync_mock):
        plugin_obj = self.mock_make_obj_by_file(make_obj_by_file_mock)
        register_mock.return_value = {'id': 1}
        self.plugin.install(self.path)

        plugin_obj.install.assert_called_once_with(self.path, force=False)
        register_mock.assert_called_once_with(
            'retrieved_name', 'retrieved_version', force=False)
        sync_mock.assert_called_once_with(plugin_ids=[1])

    @patch.object(Plugins, 'unregister')
    @patch.object(Plugins, 'make_obj_by_name')
    def test_remove(self, make_obj_by_name_mock, unregister_mock):
        plugin_obj = MagicMock()
        make_obj_by_name_mock.return_value = plugin_obj

        self.plugin.remove(self.name, self.version)

        plugin_obj.remove.assert_called_once_with(self.name, self.version)
        unregister_mock.assert_called_once_with(self.name, self.version)

    @patch.object(Plugins.connection, 'post_request')
    def test_sync(self, post_mock):
        self.plugin.sync()
        post_mock.assert_called_once_with(
            api='plugins/sync/', data=None)

    @patch.object(Plugins.connection, 'post_request')
    def test_sync_with_specific_plugins(self, post_mock):
        self.plugin.sync(plugin_ids=[1, 2])
        data = {'ids': [1, 2]}
        post_mock.assert_called_once_with(
            api='plugins/sync/', data=data)

    @patch.object(Plugins, 'register')
    @patch.object(Plugins, 'make_obj_by_file')
    def test_update(self, make_obj_by_file_mock, register_mock):
        plugin_obj = self.mock_make_obj_by_file(make_obj_by_file_mock)

        self.plugin.update(self.path)

        plugin_obj.update.assert_called_once_with(self.path)
        register_mock.assert_called_once_with(
            'retrieved_name', 'retrieved_version')

    @patch.object(Plugins, 'register')
    @patch.object(Plugins, 'make_obj_by_file')
    def test_downgrade(self, make_obj_by_file_mock, register_mock):
        plugin_obj = self.mock_make_obj_by_file(make_obj_by_file_mock)

        self.plugin.downgrade(self.path)

        plugin_obj.downgrade.assert_called_once_with(self.path)
        register_mock.assert_called_once_with(
            'retrieved_name', 'retrieved_version')

    @patch.object(Plugins, 'get_plugin')
    def test_make_obj_by_name_v1(self, get_mock):
        plugins = [{'package_version': '1.0.0'},
                   {'package_version': '1.0.1'},
                   {'package_version': '1.99.99'}]

        for plugin in plugins:
            get_mock.return_value = plugin
            self.assertEqual(
                self.plugin.make_obj_by_name(self.name, self.version),
                PluginV1)

    @patch.object(Plugins, 'get_plugin')
    def test_make_obj_by_name_v2(self, get_mock):
        plugins = [{'package_version': '2.0.0'},
                   {'package_version': '2.0.1'},
                   {'package_version': '3.0.0'}]

        for plugin in plugins:
            get_mock.return_value = plugin
            self.assertEqual(
                self.plugin.make_obj_by_name(self.name, self.version),
                PluginV2)

    @patch.object(Plugins, 'get_plugin')
    def test_make_obj_by_name_v2_raises_error(self, get_mock):
        get_mock.return_value = {'package_version': '0.0.1'}

        self.assertRaisesRegexp(
            error.BadDataException,
            'Plugin plugin_name==version has '
            'unsupported package version 0.0.1',
            self.plugin.make_obj_by_name, self.name, self.version)

    def test_make_obj_by_file_v1(self):
        self.assertEqual(
            self.plugin.make_obj_by_file('file-name-1.2.3.fp'),
            PluginV1)

    def test_make_obj_by_file_v2(self):
        self.assertEqual(
            self.plugin.make_obj_by_file('file-name-1.2-1.2.3-0.noarch.rpm'),
            PluginV2)

    def test_make_obj_by_file_raises_error(self):
        self.assertRaisesRegexp(
            error.BadDataException,
            'Plugin file-name.ext has unsupported format .ext',
            self.plugin.make_obj_by_file, 'file-name.ext')

    @patch.object(Plugins, 'get_plugin_for_update', return_value={'id': 99})
    @patch.object(Plugins.connection, 'put_request', return_value={'id': 99})
    def test_update_or_create_updates(self, put_mock, get_for_update_mock):
        meta = {'id': 99, 'version': '1.0.0', 'package_version': '2.0.0'}
        self.plugin.update_or_create(meta)
        put_mock.assert_called_once_with('plugins/99', meta)

    @patch.object(Plugins, 'get_plugin_for_update', return_value=None)
    @patch.object(Plugins.connection, 'post_request_raw',
                  return_value=MagicMock(status_code=201))
    @patch.object(Plugins.connection, 'put_request')
    def test_update_or_create_creates(
            self, put_mock, post_mock, get_for_update_mock):
        meta = {'id': 99, 'version': '1.0.0', 'package_version': '2.0.0'}
        self.plugin.update_or_create(meta)
        post_mock.assert_called_once_with('plugins/', meta)
        get_for_update_mock.assert_called_once_with(meta)
        self.assertFalse(put_mock.called)

    @patch.object(Plugins, 'get_plugin_for_update', return_value=None)
    @patch.object(Plugins.connection, 'post_request_raw',
                  return_value=MagicMock(
                      status_code=409,
                      **{'json.return_value': {'id': 99}}))
    @patch.object(Plugins.connection, 'put_request', return_value='put_return')
    def test_update_or_create_updates_with_force(
            self, put_mock, post_mock, get_for_update_mock):
        meta = {'id': 99, 'version': '1.0.0', 'package_version': '2.0.0'}
        self.assertEqual(
            self.plugin.update_or_create(meta, force=True),
            'put_return')
        post_mock.assert_called_once_with('plugins/', meta)
        get_for_update_mock.assert_called_once_with(meta)
        put_mock.assert_called_once_with('plugins/99', meta)

    @patch.object(Plugins, 'get_all_data')
    def test_get_plugin_for_update(self, get_mock):
        plugin_to_be_found = {'name': 'name', 'version': '2.2.0',
                              'package_version': '2.0.0'}

        get_mock.return_value = [
            # Different major version
            {'name': 'name', 'version': '2.3.0',
             'package_version': '2.0.0'},
            {'name': 'name', 'version': '2.1.0',
             'package_version': '2.0.0'},
            # Different name
            {'name': 'different_name', 'version': '2.2.99',
             'package_version': '2.0.0'},
            # Package version is not updatable
            {'name': 'name', 'version': '2.2.100',
             'package_version': '1.0.0'},
            plugin_to_be_found]

        self.assertEqual(
            self.plugin.get_plugin_for_update(
                {'name': 'name',
                 'version': '2.2.99',
                 'package_version': '2.0.0'}),
            plugin_to_be_found)

        # Required plugin has not updatable package version
        self.assertIsNone(self.plugin.get_plugin_for_update(
            {'name': 'name', 'version': '2.2.99', 'package_version': '1.0.0'}))

        # Plugin does not exist
        self.assertIsNone(self.plugin.get_plugin_for_update(
            {'name': 'name2', 'version': '2.2.9', 'package_version': '2.0.0'}))

    def test_is_updatable(self):
        for updatable in ['2.0.0', '2.0.1', '99.99.99']:
            self.assertTrue(self.plugin.is_updatable(updatable))

        for is_not_updatable in ['0.0.1', '1.0.0', '1.99.99']:
            self.assertFalse(self.plugin.is_updatable(is_not_updatable))

    @patch.object(Plugins, 'get_all_data',
                  return_value=[{'name': 'name1', 'version': '1.0.0'},
                                {'name': 'name2', 'version': '1.0.1'},
                                {'name': 'name2', 'version': '1.0.0'}])
    def test_get_plugin(self, get_mock):
        self.assertEqual(self.plugin.get_plugin('name2', '1.0.0'),
                         {'name': 'name2', 'version': '1.0.0'})
        get_mock.assert_called_once_with()
