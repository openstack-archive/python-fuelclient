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
from fuelclient.tests.unit.v2.lib import test_api

NETWORK_CONF = '''---
  vips:
    vrouter_pub:
      network_role: "public/vip"
      ipaddr: "10.109.3.2"
      namespace: "vrouter"
      is_user_defined: false
      vendor_specific:
        iptables_rules:
          ns_start:
            - "iptables -t nat -A POSTROUTING -o <%INT%> -j MASQUERADE"
'''


class TestNetworkConfigurationFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestNetworkConfigurationFacade, self).setUp()

        self.version = 'v1'
        self.task_id = 42
        self.res_uri = (
            '/api/{version}/transactions/{task_id}'
            '/network_configuration'.format(
                version=self.version, task_id=self.task_id))

        self.client = fuelclient.get_client('network-configuration',
                                            self.version)

    def test_network_configuration_download(self):
        expected_body = yaml.load(NETWORK_CONF)
        matcher = self.m_request.get(self.res_uri, json=expected_body)

        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.download(self.task_id)

        self.assertTrue(matcher.called)

        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        expected_yaml = yaml.safe_load(NETWORK_CONF)
        self.assertEqual(written_yaml, expected_yaml)
