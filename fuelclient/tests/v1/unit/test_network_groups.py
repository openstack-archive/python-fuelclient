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

from fuelclient.tests import base


@mock.patch('fuelclient.client.requests')
class TestNetworkGroupActions(base.UnitTestCase):

    def test_list_network_groups(self, mreq):
        self.execute(['fuel', 'network-group', '--list'])
        call_args = mreq.get.call_args_list[-1]
        url = call_args[0][0]
        self.assertIn('networks/', url)

    def test_create_network_group(self, mreq):
        self.execute(['fuel', 'network-group', '--create', '--cidr',
                      '10.0.0.0/24', '--name', 'test network',
                      '--group', '1'])

        call_args = mreq.post.call_args_list[0]
        call_data = call_args[-1]['data']
        url = call_args[0][0]
        self.assertIn('"group_id": 1', call_data)
        self.assertIn('"name": "test network"', call_data)
        self.assertIn('networks/', url)

    def test_delete_network_group(self, mreq):
        self.execute(['fuel', 'network-group', '--delete', '--network', '3'])
        call_args = mreq.delete.call_args_list[-1]
        url = call_args[0][0]
        self.assertIn('networks/3', url)
