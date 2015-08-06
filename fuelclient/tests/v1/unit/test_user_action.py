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
from fuelclient.tests import base


class TestChangePassword(base.UnitTestCase):

    def test_get_password_from_prompt(self):
        user_action = UserAction()
        passwd = 'secret!'
        with mock.patch('fuelclient.cli.actions.user.getpass',
                        return_value=passwd):
            user_passwd = user_action._get_password_from_prompt()

        self.assertEqual(passwd, user_passwd)

    def test_get_password_from_prompt_different_passwords(self):
        user_action = UserAction()
        with mock.patch('fuelclient.cli.actions.user.getpass',
                        side_effect=['pwd', 'otherpwd']):
            with self.assertRaisesRegexp(
                    ArgumentException, 'Passwords are not the same'):
                user_action._get_password_from_prompt()
