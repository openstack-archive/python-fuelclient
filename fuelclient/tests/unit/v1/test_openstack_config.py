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
import yaml

from fuelclient.tests.unit.v1 import base
from fuelclient.tests import utils


@mock.patch('fuelclient.cli.serializers.open', create=True)
class TestOpenstackConfigActions(base.UnitTestCase):

    def setUp(self):
        super(TestOpenstackConfigActions, self).setUp()

        self.config = utils.get_fake_openstack_config()

    def test_config_download(self, mopen):
        m_get = self.m_request.get(
            '/api/v1/openstack-config/42/', json=self.config)
        self.execute(['fuel', 'openstack-config',
                      '--config-id', '42', '--download',
                      '--file', 'config.yaml'])

        self.assertTrue(m_get.called)
        content = mopen().__enter__().write.call_args[0][0]
        content = yaml.safe_load(content)
        self.assertEqual(self.config['configuration'],
                         content['configuration'])

    def test_config_upload(self, mopen):
        mopen().__enter__().read.return_value = yaml.safe_dump(
            {'configuration': self.config['configuration']})
        m_post = self.m_request.post(
            '/api/v1/openstack-config/', json=self.config)
        with mock.patch('fuelclient.objects.openstack_config.os'):
            self.execute(['fuel', 'openstack-config', '--env', '1', '--upload',
                          '--file', 'config.yaml'])
        self.assertTrue(m_post.called)

    def test_config_list(self, mopen):
        m_get = self.m_request.get(
            '/api/v1/openstack-config/?cluster_id=84', json=[])
        self.execute(['fuel', 'openstack-config', '--env', '84', '--list'])
        self.assertTrue(m_get.called)

    def test_config_delete(self, mopen):
        m_del = self.m_request.delete(
            '/api/v1/openstack-config/42/', json={})
        self.execute(['fuel', 'openstack-config',
                      '--config-id', '42', '--delete'])
        self.assertTrue(m_del.called)

    def test_config_execute(self, mopen):
        m_put = self.m_request.put(
            '/api/v1/openstack-config/execute/',
            json={'status': 'ready'})
        self.execute(['fuel', 'openstack-config', '--env', '42', '--execute'])
        self.assertTrue(m_put.called)
