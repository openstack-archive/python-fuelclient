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

from fuelclient.cli.actions.user import UserAction
from fuelclient.cli.error import ArgumentException
from fuelclient.cli.serializers import Serializer
from fuelclient.tests.unit.v1 import base


class TestChangePassword(base.UnitTestCase):

    def assert_print(self, print_mock, result, msg):
        print_mock.assert_called_once_with(result, msg)

    def test_get_password_from_prompt(self):
        user_action = UserAction()
        passwd = 'secret!'
        with mock.patch('fuelclient.cli.actions.user.getpass',
                        return_value=passwd):
            user_passwd = user_action._get_password_from_prompt()

        self.assertEqual(passwd, user_passwd)

    @mock.patch('fuelclient.cli.actions.user.getpass',
                side_effect=['pwd', 'otherpwd'])
    def test_get_password_from_prompt_different_passwords(self, mgetpass):
        user_action = UserAction()
        with self.assertRaisesRegexp(
                ArgumentException, 'Passwords are not the same'):
            user_action._get_password_from_prompt()
#
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
#

    @patch.object(Serializer, 'print_to_output')
    @mock.patch('fuelclient.cli.actions.user.APIClient')
    def test_change_password(self, print_mock, mapiclient):
        user_action = UserAction()
        params = mock.Mock()
        params.newpass = None
        password = 'secret'

        with mock.patch('fuelclient.cli.actions.user.getpass',
                        return_value=password) as mgetpass:
            user_action.change_password(params)

        calls = [
            mock.call("Changing password for Fuel User.\nNew Password:"),
            mock.call("Retype new Password:"),
        ]

        mgetpass.assert_has_calls(calls)
        mapiclient.update_own_password.assert_called_once_with(password)
        msg = "\nPassword changed.\nPlease note that configuration " \
            "is not automatically updated.\nYou may want to update " \
            "/root/.config/fuel/fuel_client.yaml."

        self.assert_print(
            print_mock,
            None,
            msg)

    @mock.patch('fuelclient.cli.actions.user.APIClient')
    def test_change_password_w_newpass(self, mapiclient):
        user_action = UserAction()
        params = mock.Mock()
        params.newpass = 'secret'
        user_action.change_password(params)
        mapiclient.update_own_password.assert_called_once_with(params.newpass)
