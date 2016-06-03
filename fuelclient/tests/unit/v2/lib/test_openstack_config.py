#    Copyright 2016 Mirantis, Inc.
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
import yaml

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestOpenstackConfigClient(test_api.BaseLibTest):

    def setUp(self):
        super(TestOpenstackConfigClient, self).setUp()

        self.version = 'v1'
        self.uri = '/api/{version}/openstack-config/'.format(
            version=self.version)

        self.client = fuelclient.get_client('openstack-config', self.version)

    def test_config_list_for_cluster(self):
        cluster_id = 1
        fake_configs = [
            utils.get_fake_openstack_config(cluster_id=cluster_id)
        ]

        uri = self.uri + '?cluster_id={0}&is_active=True'.format(cluster_id)
        m_get = self.m_request.get(uri, complete_qs=True, json=fake_configs)
        data = self.client.get_filtered(cluster_id=1)

        self.assertTrue(m_get.called)
        self.assertEqual(data[0]['cluster_id'], cluster_id)

    def test_config_list_for_node(self):
        cluster_id = 1
        fake_configs = [
            utils.get_fake_openstack_config(
                cluster_id=cluster_id, node_id=22),
        ]

        uri = self.uri + '?cluster_id={0}&node_ids=22' \
                         '&is_active=True'.format(cluster_id)
        m_get = self.m_request.get(uri, complete_qs=True, json=fake_configs)
        data = self.client.get_filtered(cluster_id=1, node_ids=[22])

        self.assertTrue(m_get.called)
        self.assertEqual(data[0]['cluster_id'], cluster_id)

    def test_config_list_for_multinode(self):
        cluster_id = 1
        fake_configs = [
            utils.get_fake_openstack_config(
                cluster_id=cluster_id, node_id=22),
            utils.get_fake_openstack_config(
                cluster_id=cluster_id, node_id=44),
        ]

        uri = self.uri + '?cluster_id={0}&node_ids=22,44' \
                         '&is_active=True'.format(cluster_id)
        m_get = self.m_request.get(uri, complete_qs=True, json=fake_configs)
        data = self.client.get_filtered(cluster_id=1, node_ids=[22, 44])

        self.assertTrue(m_get.called)
        self.assertEqual(data[0]['cluster_id'], cluster_id)

    def test_config_download(self):
        config_id = 42
        uri = self.uri + '{0}/'.format(42)
        fake_config = utils.get_fake_openstack_config(id=config_id)

        m_get = self.m_request.get(uri, json=fake_config)

        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.download(config_id, '/path/to/config')

        self.assertTrue(m_get.called)
        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        self.assertEqual(written_yaml,
                         {'configuration': fake_config['configuration']})

    def test_config_upload(self):
        cluster_id = 1
        fake_config = utils.get_fake_openstack_config(
            cluster_id=cluster_id)

        m_post = self.m_request.post(self.uri, json=[fake_config])

        m_open = mock.mock_open(read_data=yaml.safe_dump({
            'configuration': fake_config['configuration']
        }))
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True), \
                mock.patch('os.path.exists', mock.Mock(return_value=True)):
            self.client.upload('/path/to/config', cluster_id)

        self.assertTrue(m_post.called)
        body = m_post.last_request.json()
        self.assertEqual(body['cluster_id'], cluster_id)
        self.assertNotIn('node_ids', body)
        self.assertNotIn('node_role', body)

    def test_config_upload_multinode(self):
        cluster_id = 1
        fake_configs = [
            utils.get_fake_openstack_config(
                cluster_id=cluster_id, node_id=42),
            utils.get_fake_openstack_config(
                cluster_id=cluster_id, node_id=44)
        ]

        m_post = self.m_request.post(self.uri, json=fake_configs)

        m_open = mock.mock_open(read_data=yaml.safe_dump({
            'configuration': fake_configs[0]['configuration']
        }))
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True), \
                mock.patch('os.path.exists', mock.Mock(return_value=True)):
            self.client.upload(
                '/path/to/config', cluster_id, node_ids=[42, 44])

        self.assertTrue(m_post.called)
        body = m_post.last_request.json()
        self.assertEqual(body['cluster_id'], cluster_id)
        self.assertEqual(body['node_ids'], [42, 44])
        self.assertNotIn('node_role', body)

    def test_config_delete(self):
        config_id = 42
        uri = self.uri + '{0}/'.format(config_id)
        fake_config = utils.get_fake_openstack_config(id=config_id)

        m_del = self.m_request.delete(uri, json=fake_config)

        self.client.delete(config_id)
        self.assertTrue(m_del.called)
