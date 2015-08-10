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

import json
import yaml

from mock import patch

from fuelclient.tests import base


ENV_OUTPUT = {
    'id': 1,
    'net_provider': 'neutron',
}

FILE_INPUT = '''networks:
- name: public
- id: 1
'''

NETWORK_CONFIG_ERROR_OUTPUT = {
    'status': 'error',
    'message': 'Some error',
}


@patch('fuelclient.client.requests')
@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestNetworkActions(base.UnitTestCase):

    def test_network_download(self, mos, mopen, mrequests):
        mrequests.get().json.side_effect = [ENV_OUTPUT, yaml.load(FILE_INPUT)]
        self.execute(['fuel', 'network', '--env', '1', '--download'])
        mopen().__enter__().write.assert_called_once_with(FILE_INPUT)

    def test_network_upload(self, mos, mopen, mrequests):
        mopen().__enter__().read.return_value = FILE_INPUT
        mrequests.get().json.return_value = ENV_OUTPUT
        self.execute(['fuel', 'network', '--env', '1', '--upload', 'smth'])
        self.assertEqual(mrequests.put.call_count, 1)
        call_args = mrequests.put.call_args_list[0]
        url = call_args[0][0]
        kwargs = call_args[1]
        self.assertIn('clusters/1/network_configuration/neutron', url)
        self.assertEqual(
            json.loads(kwargs['data']), yaml.load(FILE_INPUT))

    def test_network_upload_with_error(self, mos, mopen, mrequests):
        mopen().__enter__().read.return_value = FILE_INPUT
        mrequests.get().json.return_value = ENV_OUTPUT
        mrequests.put().json.return_value = NETWORK_CONFIG_ERROR_OUTPUT
        with patch('sys.stdout') as fake_out:
            self.execute(['fuel', 'network', '--env', '1', '--upload', 'smth'])
            call_args = fake_out.write.call_args_list[0]
            self.assertIn('Error uploading configuration', call_args[0][0])
            self.assertIn(
                NETWORK_CONFIG_ERROR_OUTPUT['message'], call_args[0][0]
            )
