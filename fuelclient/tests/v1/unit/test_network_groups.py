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

import requests_mock

from fuelclient.tests import base


@requests_mock.mock()
class TestNetworkGroupActions(base.UnitTestCase):

    def test_list_network_groups(self, mreq):
        mreq.get('/api/v1/networks/')
        self.execute(['fuel', 'network-group', '--list'])

    def test_create_network_group(self, mreq):
        mreq.post('/api/v1/networks/')
        self.execute(['fuel', 'network-group', '--create', '--cidr',
                      '10.0.0.0/24', '--name', 'test network',
                      '--node-group', '1'])

        call_data = mreq.last_request.json()
        self.assertEqual(1, call_data['group_id'])
        self.assertEqual("test network", call_data['name'])

    def test_delete_network_group(self, mreq):
        mreq.delete('/api/v1/networks/3/')
        self.execute(['fuel', 'network-group', '--delete', '--network', '3'])

    def test_network_group_duplicate_name(self, mreq):
        mreq.post('/api/v1/networks/', status_code=409)

        with self.assertRaises(SystemExit):
            self.execute(['fuel', 'network-group', '--create', '--cidr',
                          '10.0.0.0/24', '--name', 'test network',
                          '--node-group', '1'])
