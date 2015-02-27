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

from fuelclient.tests import base

API_IN = """id: 2
name: my_role
"""

API_OUT = yaml.load(API_IN)


@patch('fuelclient.client.requests')
class TestRoleActions(base.UnitTestCase):

    def test_list_roles(self, mreq):
        self.execute(['fuel', 'role'])
        role_call = mreq.get.call_args_list[-1]
        url = role_call[0][0]
        self.assertIn('api/v1/roles', url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_get_role(self, mopen, mreq):
        mreq.get().json.return_value = API_OUT
        self.execute(['fuel', 'role', '--role', '3', '--file', 'myfile'])

        mopen().__enter__().write.assert_called_once_with(API_IN)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_create_role(self, mopen, mreq):
        mopen().__enter__().read.return_value = API_IN

        self.execute(['fuel', 'role', '--create', '--file', 'myfile'])

        call_args = mreq.post.call_args_list[0]
        url = call_args[0][0]
        kwargs = call_args[1]
        self.assertIn('api/v1/roles', url)
        self.assertEqual(
            json.loads(kwargs['data']), API_OUT)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_update_role(self, mopen, mreq):
        mopen().__enter__().read.return_value = API_IN

        self.execute(['fuel', 'role', '--update', '--file', 'myfile'])

        call_args = mreq.put.call_args_list[0]
        url = call_args[0][0]
        kwargs = call_args[1]
        self.assertIn('api/v1/roles', url)
        self.assertEqual(
            json.loads(kwargs['data']), API_OUT)

    def test_delete_role(self, mreq):
        self.execute(['fuel', 'role', '--delete', '--role', '3'])
        role_call = mreq.delete.call_args_list[-1]
        url = role_call[0][0]
        self.assertIn('api/v1/roles/3', url)
