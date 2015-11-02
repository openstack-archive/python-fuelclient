# -*- coding: utf-8 -*-
#
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

import yaml

from mock import patch

from fuelclient.tests.unit.v1 import base


ENV_OUTPUT = {
    'id': 1,
    'net_provider': 'neutron',
}

FILE_INPUT = '''networks:
- name: public
- id: 1
'''

NETWORK_CONFIG_OK_OUTPUT = {
    'status': 'ready',
    'progress': 100,
}

NETWORK_CONFIG_ERROR_OUTPUT = {
    'message': 'Some error',
    'errors': [],
}


@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestNetworkActions(base.UnitTestCase):

    def test_network_download(self, mos, mopen):
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        self.m_request.get('/api/v1/clusters/1/network_configuration/neutron',
                           json=yaml.load(FILE_INPUT))
        self.execute(['fuel', 'network', '--env', '1', '--download'])
        mopen().__enter__().write.assert_called_once_with(FILE_INPUT)

    def test_network_upload(self, mos, mopen):
        mopen().__enter__().read.return_value = FILE_INPUT
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        mneutron_put = self.m_request.put(
            '/api/v1/clusters/1/network_configuration/neutron',
            json=NETWORK_CONFIG_OK_OUTPUT)
        self.execute(['fuel', 'network', '--env', '1', '--upload'])
        self.assertEqual(mneutron_put.call_count, 1)
        url = mneutron_put.request_history[0].url
        self.assertIn('clusters/1/network_configuration/neutron', url)

    def test_network_upload_with_error(self, mos, mopen):
        mopen().__enter__().read.return_value = FILE_INPUT
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        self.m_request.put(
            '/api/v1/clusters/1/network_configuration/neutron',
            status_code=400, json=NETWORK_CONFIG_ERROR_OUTPUT)

        with patch("sys.stderr") as m_stderr:
            self.assertRaises(
                SystemExit, self.execute,
                ['fuel', 'network', '--env', '1', '--upload'])

        self.assertIn("400 Client Error", m_stderr.write.call_args[0][0])
        self.assertIn(NETWORK_CONFIG_ERROR_OUTPUT['message'],
                      m_stderr.write.call_args[0][0])
