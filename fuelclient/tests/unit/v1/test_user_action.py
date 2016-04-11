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

    @mock.patch('fuelclient.cli.serializers.Serializer.print_to_output')
    @mock.patch('fuelclient.cli.actions.user.fuelclient_settings')
    @mock.patch('fuelclient.cli.actions.user.APIClient')
    def test_change_password(self, mapiclient, settings_mock, print_mock):
        user_action = UserAction()
        params = mock.Mock()
        params.newpass = None
        password = 'secret'
        conf_file = '/tmp/fuel_client.yaml'
        settings_mock.get_settings.return_value = mock.Mock(
            user_settings=conf_file)

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
            "{0}.".format(conf_file)

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
