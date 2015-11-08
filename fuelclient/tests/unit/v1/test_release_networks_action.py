# -*- coding: utf-8 -*-
#
#    Copyright 2014 Mirantis, Inc.
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
import requests_mock as rm

from fuelclient.tests.unit.v1 import base


API_INPUT = {'config': 'neutron'}
API_OUTPUT = 'config: neutron\n'


@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestReleaseNetworkActions(base.UnitTestCase):

    def test_release_network_download(self, mos, mopen):
        self.m_request.get(rm.ANY, json=API_INPUT)
        self.execute(['fuel', 'rel', '--rel', '1', '--network', '--download'])
        mopen().__enter__().write.assert_called_once_with(API_OUTPUT)

    def test_release_network_upload(self, mos, mopen):
        mopen().__enter__().read.return_value = API_OUTPUT
        put = self.m_request.put('/api/v1/releases/1/networks', json={})
        self.execute(['fuel', 'rel', '--rel', '1', '--network', '--upload'])

        self.assertTrue(put.called)
        self.assertEqual(put.last_request.json(), API_INPUT)
