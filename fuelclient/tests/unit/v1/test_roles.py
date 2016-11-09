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
import yaml

from fuelclient.cli.serializers import Serializer
from fuelclient.tests.unit.v1 import base

API_IN = """name: my_role
"""

API_OUT = yaml.load(API_IN)


class TestRoleActions(base.UnitTestCase):

    owner_id = 2

    def test_list_release_roles(self):
        url = '/api/v1/releases/{0}/roles/'.format(self.owner_id)
        cmd = 'fuel role --rel {0}'.format(self.owner_id)
        get_request = self.m_request.get(url, json=[API_OUT])

        self.execute(cmd.split())

        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)

    def test_list_cluster_roles(self):
        url = '/api/v1/clusters/{0}/roles/'.format(self.owner_id)
        cmd = 'fuel role --env {0}'.format(self.owner_id)
        get_request = self.m_request.get(url, json=[API_OUT])

        self.execute(cmd.split())

        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_get_release_role(self, mopen):
        url = '/api/v1/releases/{0}/roles/my_role/'.format(self.owner_id)
        cmd = 'fuel role --role my_role --file myfile.yaml --rel {0}'.format(
            self.owner_id)
        get_request = self.m_request.get(url, json=API_OUT)

        self.execute(cmd.split())

        mopen().__enter__().write.assert_called_once_with(API_IN)
        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_get_cluster_role(self, mopen):
        url = '/api/v1/clusters/{0}/roles/my_role/'.format(self.owner_id)
        cmd = 'fuel role --role my_role --file myfile.yaml --env {0}'.format(
            self.owner_id)
        get_request = self.m_request.get(url, json=API_OUT)

        self.execute(cmd.split())

        mopen().__enter__().write.assert_called_once_with(API_IN)
        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_create_release_role(self, mopen):
        url = '/api/v1/releases/{0}/roles/'.format(self.owner_id)
        cmd = 'fuel role --create --file myfile.yaml --rel {0}'.format(
            self.owner_id)
        mopen().__enter__().read.return_value = API_IN
        post_request = self.m_request.post(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(post_request.called)
        self.assertIn(url, post_request.last_request.url)
        self.assertEqual(
            API_OUT, post_request.last_request.json())

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_create_cluster_role(self, mopen):
        url = '/api/v1/clusters/{0}/roles/'.format(self.owner_id)
        cmd = 'fuel role --create --file myfile.yaml --env {0}'.format(
            self.owner_id)
        mopen().__enter__().read.return_value = API_IN
        post_request = self.m_request.post(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(post_request.called)
        self.assertIn(url, post_request.last_request.url)
        self.assertEqual(
            API_OUT, post_request.last_request.json())

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_update_release_role(self, mopen):
        url = '/api/v1/releases/{0}/roles/my_role/'.format(self.owner_id)
        cmd = 'fuel role --update --file myfile.yaml --rel {0}'.format(
            self.owner_id)
        mopen().__enter__().read.return_value = API_IN
        put_request = self.m_request.put(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(put_request.called)
        self.assertIn(url, put_request.last_request.url)
        self.assertEqual(
            API_OUT, put_request.last_request.json())

    @patch('fuelclient.cli.serializers.open', create=True)
    def test_update_cluster_role(self, mopen):
        url = '/api/v1/clusters/{0}/roles/my_role/'.format(self.owner_id)
        cmd = 'fuel role --update --file myfile.yaml --env {0}'.format(
            self.owner_id)
        mopen().__enter__().read.return_value = API_IN
        put_request = self.m_request.put(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(put_request.called)
        self.assertIn(url, put_request.last_request.url)
        self.assertEqual(
            API_OUT, put_request.last_request.json())

    def test_delete_release_role(self):
        url = '/api/v1/releases/{0}/roles/my_role/'.format(self.owner_id)
        cmd = 'fuel role --delete --role my_role --rel {0}'.format(
            self.owner_id)
        delete_request = self.m_request.delete(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(delete_request.called)
        self.assertIn(url, delete_request.last_request.url)

    def test_delete_cluster_role(self):
        url = '/api/v1/clusters/{0}/roles/my_role/'.format(self.owner_id)
        cmd = 'fuel role --delete --role my_role --env {0}'.format(
            self.owner_id)
        delete_request = self.m_request.delete(url, json=API_OUT)

        self.execute(cmd.split())

        self.assertTrue(delete_request.called)
        self.assertIn(url, delete_request.last_request.url)

    def test_formatting_for_list_roles(self):
        url = '/api/v1/releases/{0}/roles/'.format(self.owner_id)
        cmd = 'fuel role --rel {0}'.format(self.owner_id)
        get_request = self.m_request.get(url, json=[API_OUT])

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
