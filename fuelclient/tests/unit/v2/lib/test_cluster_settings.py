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

CLUSTER_SETTINGS = '''---
  editable:
    service_user:
      name:
        type: "hidden"
        value: "fuel"
      sudo:
        type: "hidden"
        value: "ALL=(ALL) NOPASSWD: ALL"
      homedir:
        type: "hidden"
        value: "/var/lib/fuel"
'''


class TestClusterSettingsFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestClusterSettingsFacade, self).setUp()

        self.version = 'v1'
        self.task_id = 42
        self.res_uri = (
            '/api/{version}/transactions/{task_id}/settings'.format(
                version=self.version, task_id=self.task_id))

        self.client = fuelclient.get_client('cluster-settings',
                                            self.version)

    def test_network_configuration_download(self):
        expected_body = yaml.load(CLUSTER_SETTINGS)
        matcher = self.m_request.get(self.res_uri, json=expected_body)

        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.download(self.task_id)

        self.assertTrue(matcher.called)

        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        expected_yaml = yaml.safe_load(CLUSTER_SETTINGS)
        self.assertEqual(written_yaml, expected_yaml)
