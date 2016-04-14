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

import yaml

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestTaskAdditionalInfoFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestTaskAdditionalInfoFacade, self).setUp()

        self.version = 'v1'
        self.task_id = 42
        self.res_uri = (
            '/api/{version}/transactions/{task_id}/'.format(
                version=self.version, task_id=self.task_id))

    def _test_info_download(self, client_name, yaml_data, uri):
        client = fuelclient.get_client(client_name, self.version)
        expected_body = yaml.load(yaml_data)
        matcher = self.m_request.get("{0}{1}".format(self.res_uri, uri),
                                     json=expected_body)
        result = client.download(self.task_id)

        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, result)

    def test_network_configuration_download(self):
        self._test_info_download('network-configuration',
                                 utils.get_fake_yaml_network_conf(),
                                 'network_configuration')

    def test_cluster_settings_download(self):
        self._test_info_download('cluster-settings',
                                 utils.get_fake_yaml_cluster_settings(),
                                 'settings')

    def test_deployment_info_download(self):
        self._test_info_download('deployment-info',
                                 utils.get_fake_yaml_deployment_info(),
                                 'deployment_info')
