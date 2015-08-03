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

from mock import patch
import requests_mock
import yaml

from fuelclient.cli.serializers import Serializer
from fuelclient.tests import base

API_IN = """name: my_role
"""

API_OUT = yaml.load(API_IN)


@requests_mock.mock()
class TestRoleActions(base.UnitTestCase):

    release_id = 2

    def test_list_roles(self, mreq):
        url = '/api/v1/releases/{0}/roles/'.format(self.release_id)
        cmd = 'fuel role --rel {0}'.format(self.release_id)
        get_request = mreq.get(url, json=[API_OUT])

        self.execute(cmd.split())

        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_get_role(self, mreq, mopen):
        url = '/api/v1/releases/{0}/roles/my_role/'.format(self.release_id)
        cmd = 'fuel role --role my_role --file myfile.yaml --rel {0}'.format(
            self.release_id)
        get_request = mreq.get(url, json=API_OUT)

        self.execute(cmd.split())

        mopen().__enter__().write.assert_called_once_with(API_IN)
        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_create_role(self, mreq, mopen):
        url = '/api/v1/releases/{0}/roles/'.format(self.release_id)
        cmd = 'fuel role --create --file myfile.yaml --rel {0}'.format(
            self.release_id)
        mopen().__enter__().read.return_value = API_IN
        post_request = mreq.post(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(post_request.called)
        self.assertIn(url, post_request.last_request.url)
        self.assertEqual(
            API_OUT, post_request.last_request.json())

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_update_role(self, mreq, mopen):
        url = '/api/v1/releases/{0}/roles/my_role/'.format(self.release_id)
        cmd = 'fuel role --update --file myfile.yaml --rel {0}'.format(
            self.release_id)
        mopen().__enter__().read.return_value = API_IN
        put_request = mreq.put(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(put_request.called)
        self.assertIn(url, put_request.last_request.url)
        self.assertEqual(
            API_OUT, put_request.last_request.json())

    def test_delete_role(self, mreq):
        url = '/api/v1/releases/{0}/roles/my_role/'.format(self.release_id)
        cmd = 'fuel role --delete --role my_role --rel {0}'.format(
            self.release_id)
        delete_request = mreq.delete(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(delete_request.called)
        self.assertIn(url, delete_request.last_request.url)

    def test_formatting_for_list_roles(self, mreq):
        url = '/api/v1/releases/{0}/roles/'.format(self.release_id)
        cmd = 'fuel role --rel {0}'.format(self.release_id)
        get_request = mreq.get(url, json=[API_OUT])

        with patch.object(Serializer, 'print_to_output') as mock_print:
            with patch('fuelclient.cli.actions.role.format_table') \
                    as format_table_mock:
                self.execute(cmd.split())

                self.assertTrue(get_request.called)
                self.assertIn(url, get_request.last_request.url)

                format_table_mock.assert_called_once_with(
                    [API_OUT], acceptable_keys=('name',))
                mock_print.assert_called_once_with(
                    [API_OUT], format_table_mock.return_value)
