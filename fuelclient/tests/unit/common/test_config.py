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

import os
import sys

import fixtures
import mock

from fuelclient.cli import error
from fuelclient import fuelclient_settings
from fuelclient.tests.unit.v1 import base


class TestSettings(base.UnitTestCase):

    def setUp(self):
        super(TestSettings, self).setUp()

        self.useFixture(fixtures.MockPatchObject(fuelclient_settings,
                                                 '_SETTINGS',
                                                 None))

    @mock.patch('os.makedirs')
    @mock.patch('shutil.copy')
    @mock.patch('os.chmod')
    @mock.patch('os.path.exists')
    def test_config_generation(self, m_exists, m_chmod, m_copy, m_makedirs):
        project_dir = os.path.dirname(fuelclient_settings.__file__)

        expected_fmode = 0o600
        expected_dmode = 0o700
        expected_default = os.path.join(project_dir,
                                        'fuel_client.yaml')
        expected_path = os.path.expanduser('~/.config/fuel/fuel_client.yaml')
        conf_home = os.path.expanduser('~/.config/')
        conf_dir = os.path.dirname(expected_path)

        m_exists.return_value = False
        f_confdir = fixtures.EnvironmentVariable('XDG_CONFIG_HOME', conf_home)
        f_settings = fixtures.EnvironmentVariable('FUELCLIENT_CUSTOM_SETTINGS')

        self.useFixture(f_confdir)
        self.useFixture(f_settings)

        fuelclient_settings.get_settings()

        m_makedirs.assert_called_once_with(conf_dir, expected_dmode)
        m_copy.assert_called_once_with(expected_default, expected_path)
        m_chmod.assert_called_once_with(expected_path, expected_fmode)

    @mock.patch('os.makedirs')
    @mock.patch('os.path.exists')
    def test_config_generation_write_error(self, m_exists, m_makedirs):
        m_exists.return_value = False
        m_makedirs.side_effect = OSError('[Errno 13] Permission denied')

        f_settings = fixtures.EnvironmentVariable('FUELCLIENT_CUSTOM_SETTINGS')
        self.useFixture(f_settings)

        self.assertRaises(error.SettingsException,
                          fuelclient_settings.get_settings)

    @mock.patch('six.print_')
    def test_deprecated_option_produces_warning(self, m_print):
        expected_warings = [mock.call('DEPRECATION WARNING: LISTEN_PORT '
                                      'parameter was deprecated and will not '
                                      'be supported in the next version of '
                                      'python-fuelclient.', end='',
                                      file=sys.stderr),
                            mock.call(' Please replace this '
                                      'parameter with SERVER_PORT',
                                      file=sys.stderr)]

        m = mock.mock_open(read_data='LISTEN_PORT: 9000')
        with mock.patch('fuelclient.fuelclient_settings.open', m):
            fuelclient_settings.get_settings()

        m_print.assert_has_calls(expected_warings, any_order=False)

    @mock.patch('six.print_')
    def test_both_deprecated_and_new_options_produce_warning(self, m_print):
        expected_waring = ('WARNING: configuration contains both '
                           'LISTEN_PORT and SERVER_PORT options set. Since '
                           'LISTEN_PORT was deprecated, only the value of '
                           'SERVER_PORT will be used.')

        m = mock.mock_open(read_data='LISTEN_PORT: 9000\nSERVER_PORT: 9000')
        with mock.patch('fuelclient.fuelclient_settings.open', m):
            fuelclient_settings.get_settings()

        m_print.assert_has_calls([mock.call(expected_waring, file=sys.stderr)])

    @mock.patch('six.print_')
    def test_set_deprecated_option_overwrites_unset_new_option(self, m_print):
        m = mock.mock_open(read_data='KEYSTONE_PASS: "admin"\n'
                                     'OS_PASSWORD:\n')
        with mock.patch('fuelclient.fuelclient_settings.open', m):
            settings = fuelclient_settings.get_settings()

        self.assertEqual('admin', settings.OS_PASSWORD)
        self.assertNotIn('OS_PASSWORD', settings.config)

    def test_fallback_to_deprecated_option(self):
        m = mock.mock_open(read_data='LISTEN_PORT: 9000')
        with mock.patch('fuelclient.fuelclient_settings.open', m):
            settings = fuelclient_settings.get_settings()

        self.assertEqual(9000, settings.LISTEN_PORT)

    def test_update_from_cli_params(self):
        test_config_text = ('SERVER_ADDRESS: "127.0.0.1"\n'
                            'SERVER_PORT: "8000"\n'
                            'OS_USERNAME: "admin"\n'
                            'OS_PASSWORD:\n'
                            'OS_TENANT_NAME:\n')

        test_parsed_args = mock.Mock(os_password='test_password',
                                     server_port="3000",
                                     os_username=None)
        del test_parsed_args.server_address
        del test_parsed_args.os_tenant_name

        m = mock.mock_open(read_data=test_config_text)
        with mock.patch('fuelclient.fuelclient_settings.open', m):
            settings = fuelclient_settings.get_settings()

        settings.update_from_command_line_options(test_parsed_args)

        self.assertEqual('3000', settings.SERVER_PORT)
        self.assertEqual('test_password', settings.OS_PASSWORD)
        self.assertEqual('admin', settings.OS_USERNAME)
