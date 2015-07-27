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

from mock import patch
import yaml

from fuelclient.cli.serializers import Serializer
from fuelclient.tests import base

API_IN = """name: my_role
"""

API_OUT = yaml.load(API_IN)


@patch('fuelclient.client.requests')
class TestRoleActions(base.UnitTestCase):

    def test_list_roles(self, mreq):
        self.execute(['fuel', 'role', '--rel', '2'])
        role_call = mreq.get.call_args_list[-1]
        url = role_call[0][0]
        self.assertIn('/releases/2/roles/', url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_get_role(self, mopen, mreq):
        mreq.get().json.return_value = API_OUT
        self.execute(['fuel', 'role',
                      '--role', 'my_role', '--file', 'myfile.yaml',
                      '--rel', '2'])

        mopen().__enter__().write.assert_called_once_with(API_IN)

        call_args = mreq.get.call_args_list[1]
        url = call_args[0][0]
        self.assertIn('releases/2/roles/my_role', url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_create_role(self, mopen, mreq):
        mopen().__enter__().read.return_value = API_IN

        self.execute(['fuel', 'role', '--create',
                      '--file', 'myfile.yaml', '--rel', '2'])

        call_args = mreq.post.call_args_list[0]
        url = call_args[0][0]
        kwargs = call_args[1]
        self.assertIn('releases/2/roles/', url)
        self.assertEqual(
            json.loads(kwargs['data']), API_OUT)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_update_role(self, mopen, mreq):
        mopen().__enter__().read.return_value = API_IN

        self.execute(['fuel', 'role', '--update',
                      '--file', 'myfile.yaml', '--rel', '2'])

        call_args = mreq.put.call_args_list[0]
        url = call_args[0][0]
        kwargs = call_args[1]
        self.assertIn('releases/2/roles/my_role', url)
        self.assertEqual(
            json.loads(kwargs['data']), API_OUT)

    def test_delete_role(self, mreq):
        self.execute(['fuel', 'role',
                      '--delete', '--role', 'my_role', '--rel', '2'])
        role_call = mreq.delete.call_args_list[-1]
        url = role_call[0][0]
        self.assertIn('releases/2/roles/my_role', url)

    def test_formatting_for_list_roles(self, _):
        with patch('fuelclient.objects.role.Role.get_all') \
                as role_get_all:
            role_get_all.return_value = [API_OUT]
            with patch.object(Serializer, 'print_to_output') \
                    as mock_print:
                self.execute(['fuel', 'role', '--rel', '2'])

                mock_print.assert_called_once_with(
                    [API_OUT], 'name   \n-------\nmy_role')
