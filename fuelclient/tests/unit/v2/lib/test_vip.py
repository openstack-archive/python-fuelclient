# -*- coding: utf-8 -*-
#
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
from fuelclient.tests.unit.v1.test_vip_action import MANY_VIPS_YAML
from fuelclient.tests.unit.v2.lib import test_api


class TestVipFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestVipFacade, self).setUp()

        self.version = 'v1'
        self.env_id = 42
        self.res_uri = (
            '/api/{version}/clusters/{env_id}'
            '/network_configuration/ips/vips/'.format(
                version=self.version, env_id=self.env_id))

        self.client = fuelclient.get_client('vip', self.version)

    def test_vip_upload(self):
        expected_body = yaml.load(MANY_VIPS_YAML)
        matcher = self.m_request.put(self.res_uri, json=expected_body)

        m_open = mock.mock_open(read_data=MANY_VIPS_YAML)
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            with mock.patch('fuelclient.objects.environment.os') as env_os:
                env_os.path.exists.return_value = True
                self.client.upload(self.env_id, 'vips_1.yaml')

        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())

    def test_vip_download(self):
        expected_body = yaml.load(MANY_VIPS_YAML)
        matcher = self.m_request.get(self.res_uri, json=expected_body)

        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.download(self.env_id)

        self.assertTrue(matcher.called)

        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        expected_yaml = yaml.safe_load(MANY_VIPS_YAML)
        self.assertEqual(written_yaml, expected_yaml)

    def test_vip_create(self):
        vip_kwargs = {'ip_addr': '127.0.0.1', 'vip_name': 'test', 'network': 1,
                      'vip_namespace': 'test-namespace'}
        request_post = self.m_request.post(self.res_uri, json={})
        self.client.create(self.env_id, **vip_kwargs)
        self.assertTrue(request_post.called)
        self.assertEqual(request_post.last_request.json(), vip_kwargs)
