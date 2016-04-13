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
import mock
import yaml

from fuelclient.tests.unit.v1 import base
from fuelclient.tests import utils


class TestOpenstackConfigActions(base.UnitTestCase):

    def setUp(self):
        super(TestOpenstackConfigActions, self).setUp()

        self.config = utils.get_fake_openstack_config()

    def test_config_download(self):
        m_get = self.m_request.get(
            '/api/v1/openstack-config/42/', json=self.config)
        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.execute(['fuel', 'openstack-config',
                          '--config-id', '42', '--download',
                          '--file', 'config.yaml'])

        self.assertTrue(m_get.called)
        content = m_open().write.mock_calls[0][1][0]
        content = yaml.safe_load(content)
        self.assertEqual(self.config['configuration'],
                         content['configuration'])

    @mock.patch('sys.stderr')
    def test_config_download_fail(self, mocked_stderr):
        self.assertRaises(
            SystemExit,
            self.execute, ['fuel', 'openstack-config', '--download',
                           '--config-id', '1'])
        mocked_stderr.write.assert_called_once_with(
            '"--config-id" and "--file" required!\n')
        mocked_stderr.reset_mock()

        self.assertRaises(
            SystemExit,
            self.execute, ['fuel', 'openstack-config', '--download',
                           '--file', 'config.yaml'])
        mocked_stderr.write.assert_called_once_with(
            '"--config-id" and "--file" required!\n')

    def test_config_upload(self):
        m_post = self.m_request.post(
            '/api/v1/openstack-config/', json=[self.config])
        m_open = mock.mock_open(read_data=yaml.safe_dump(
            {'configuration': self.config['configuration']}))
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            with mock.patch('fuelclient.objects.openstack_config.os'):
                self.execute(['fuel', 'openstack-config', '--env', '1',
                              '--upload', '--file', 'config.yaml'])
                self.assertTrue(m_post.called)

        req = json.loads(m_post.last_request.text)
        self.assertEqual(req['cluster_id'], 1)

    def test_config_upload_multinode(self):
        configs = [utils.get_fake_openstack_config(node_id=node_id)
                   for node_id in [1, 2, 3]]

        m_post = self.m_request.post(
            '/api/v1/openstack-config/', json=configs)

        m_open = mock.mock_open(read_data=yaml.safe_dump(
            {'configuration': self.config['configuration']}))
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            with mock.patch('fuelclient.objects.openstack_config.os'):
                self.execute(['fuel', 'openstack-config', '--env', '1',
                              '--node', '1,2,3',
                              '--upload', '--file', 'config.yaml'])
                self.assertTrue(m_post.called)

        req = json.loads(m_post.last_request.text)
        self.assertEqual(req['node_ids'], [1, 2, 3])
        self.assertEqual(req['cluster_id'], 1)

    @mock.patch('sys.stderr')
    def test_config_upload_fail(self, mocked_stderr):
        self.assertRaises(
            SystemExit,
            self.execute, ['fuel', 'openstack-config', '--env', '1',
                           '--upload'])
        mocked_stderr.write.assert_called_once_with(
            '"--env" and "--file" required!\n')
        mocked_stderr.reset_mock()

        self.assertRaises(
            SystemExit,
            self.execute, ['fuel', 'openstack-config', '--upload',
                           '--file', 'config.yaml'])
        mocked_stderr.write.assert_called_once_with(
            '"--env" and "--file" required!\n')

    def test_config_list(self):
        m_get = self.m_request.get(
            '/api/v1/openstack-config/?cluster_id=84', json=[
                utils.get_fake_openstack_config(id=1, cluster_id=32),
                utils.get_fake_openstack_config(id=2, cluster_id=64)
            ])
        self.execute(['fuel', 'openstack-config', '--env', '84', '--list'])
        self.assertTrue(m_get.called)

    def test_config_list_w_filters(self):
        m_get = self.m_request.get(
            '/api/v1/openstack-config/?cluster_id=84&node_role=controller',
            json=[utils.get_fake_openstack_config(id=1, cluster_id=32)])
        self.execute(['fuel', 'openstack-config', '--env', '84',
                      '--role', 'controller', '--list'])
        self.assertTrue(m_get.called)

        m_get = self.m_request.get(
            '/api/v1/openstack-config/?cluster_id=84&node_ids=42', json=[
                utils.get_fake_openstack_config(id=1, cluster_id=32),
            ])
        self.execute(['fuel', 'openstack-config', '--env', '84',
                      '--node', '42', '--list'])
        self.assertTrue(m_get.called)

    def test_config_list_multinode(self):
        m_get = self.m_request.get(
            '/api/v1/openstack-config/?cluster_id=84&node_ids=1,2,3',
            json=[utils.get_fake_openstack_config(
                id=1, cluster_id=32, node_id=1)])

        self.execute(['fuel', 'openstack-config', '--env', '84',
                      '--node', '1,2,3', '--list'])
        self.assertTrue(m_get.called)

    @mock.patch('sys.stderr')
    def test_config_list_fail(self, m_stderr):
        self.assertRaises(
            SystemExit,
            self.execute, ['fuel', 'openstack-config', '--list'])
        m_stderr.write.assert_called_once_with(
            '"--env" required!\n')

    def test_config_delete(self):
        m_del = self.m_request.delete(
            '/api/v1/openstack-config/42/', json={})
        self.execute(['fuel', 'openstack-config',
                      '--config-id', '42', '--delete'])
        self.assertTrue(m_del.called)

    def test_config_execute(self):
        m_put = self.m_request.put('/api/v1/openstack-config/execute/',
                                   json={'status': 'ready'})
        self.execute(['fuel', 'openstack-config', '--env', '42', '--execute'])
        self.assertTrue(m_put.called)
        self.assertEqual({"cluster_id": 42, "force": False},
                         json.loads(m_put.last_request.text))

    def test_config_execute_multinode(self):
        m_put = self.m_request.put('/api/v1/openstack-config/execute/',
                                   json={'status': 'ready'})

        self.execute(['fuel', 'openstack-config', '--env', '42',
                      '--node', '1,2,3', '--execute'])
        self.assertTrue(m_put.called)
        self.assertEqual(
            {"cluster_id": 42, "force": False, "node_ids": [1, 2, 3]},
            json.loads(m_put.last_request.text))

    def test_config_force_execute(self):
        m_put = self.m_request.put('/api/v1/openstack-config/execute/',
                                   json={'status': 'ready'})
        self.execute(['fuel', 'openstack-config', '--env', '42', '--execute',
                      '--force'])
        self.assertTrue(m_put.called)
        self.assertEqual({"cluster_id": 42, "force": True},
                         json.loads(m_put.last_request.text))

    def test_config_execute_fail(self):
        message = 'Some error'
        m_put = self.m_request.put(
            '/api/v1/openstack-config/execute/',
            json={'status': 'error', 'message': message})

        with mock.patch("sys.stdout") as m_stdout:
            self.execute(['fuel', 'openstack-config',
                          '--env', '42', '--execute'])
        self.assertTrue(m_put.called)
        self.assertIn(message, m_stdout.write.call_args_list[0][0][0])
