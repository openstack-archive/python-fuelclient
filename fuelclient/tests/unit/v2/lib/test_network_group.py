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

import fuelclient
from fuelclient.cli import error
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestNetworkGroupFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestNetworkGroupFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/networks/'.format(version=self.version)

        self.fake_network_group = utils.get_fake_network_group()
        self.fake_network_groups = [utils.get_fake_network_group()
                                    for i in range(10)]

        self.client = fuelclient.get_client('network-group')

    def test_network_group_list(self):
        matcher = self.m_request.get(
            self.res_uri, json=self.fake_network_groups)

        self.client.get_all()
        self.assertTrue(matcher.called)

    def test_network_group_show(self):
        expected_fields_names = (
            'id',
            'name',
            'vlan_start',
            'cidr',
            'gateway',
            'group_id',
            'meta'
        )
        net_id = 42
        uri = self.get_object_uri(self.res_uri, net_id)

        matcher = self.m_request.get(
            uri, json=self.fake_network_group)

        data = self.client.get_by_id(net_id)

        self.assertTrue(matcher.called)
        self.assertTrue(all(f in data for f
                            in expected_fields_names))

    def test_network_group_create(self):
        fake_ng = self.fake_network_group
        matcher = self.m_request.post(self.res_uri, json=fake_ng)

        self.client.create(
            name=fake_ng['name'],
            release=fake_ng['release'],
            vlan=fake_ng['vlan_start'],
            cidr=fake_ng['cidr'],
            gateway=fake_ng['gateway'],
            group_id=fake_ng['group_id'],
            meta=fake_ng['meta'],
        )

        req_data = matcher.last_request.json()

        self.assertTrue(matcher.called)

        self.assertEqual(req_data['name'], fake_ng['name'])
        self.assertEqual(req_data['release'], fake_ng['release'])
        self.assertEqual(req_data['vlan_start'], fake_ng['vlan_start'])
        self.assertEqual(req_data['meta']['notation'],
                         fake_ng['meta']['notation'])

    def test_network_group_update(self):
        net_id = 42
        uri = self.get_object_uri(self.res_uri, net_id)

        get_matcher = self.m_request.get(uri, json=self.fake_network_group)
        put_matcher = self.m_request.put(uri, json=self.fake_network_group)

        self.client.update(net_id, name='new_name')

        self.assertTrue(get_matcher.called)
        self.assertTrue(put_matcher.called)

        req_data = put_matcher.last_request.json()
        self.assertEqual('new_name', req_data['name'])

    def test_network_group_update_wrong_attribute(self):
        net_id = 42
        self.assertRaises(error.BadDataException,
                          self.client.update, net_id, vlan_start=42)

    def test_network_group_delete(self):
        env_id = 42
        uri = self.get_object_uri(self.res_uri, env_id)

        matcher = self.m_request.delete(uri, json={})

        self.client.delete_by_id(env_id)

        self.assertTrue(matcher.called)
