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

from fuelclient import client
from fuelclient.tests.unit.v1 import base
from keystoneclient.v2_0 import endpoints
from keystoneclient.v2_0 import services


class TestEndpoint(base.UnitTestCase):

    def setUp(self):
        fake_services = [{'type': 'ostf', 'enabled': True,
                          'id': '8022ba1deb954c358168a84334bd69c3',
                          'name': 'ostf', 'description': 'OSTF'},
                         {'type': 'identity', 'enabled': True,
                          'id': '832897e705d74c289d9b2250b8013740',
                          'name': 'keystone',
                          'description': 'OpenStack Identity Service'},
                         {'type': 'fuel', 'enabled': True,
                          'id': 'b192638664804529b455cf2a1aacf661',
                          'name': 'nailgun',
                          'description': 'Nailgun API'}]

        fake_endpoints = [{'adminurl': 'http://127.0.0.1:35357/v2.0/v2.0',
                           'region': 'RegionOne',
                           'enabled': True,
                           'internalurl': 'http://127.0.0.1:5000/v2.0/v2.0',
                           'service_id': '832897e705d74c289d9b2250b8013740',
                           'id': 'bc231214ba63458e927f9163e9bd291e',
                           'publicurl': 'http://127.0.0.1:5000/v2.0/v2.0'},
                          {'adminurl': 'http://127.0.0.1:8003/api',
                           'region': 'RegionOne', 'enabled': True,
                           'internalurl': 'http://127.0.0.1:8003/api',
                           'service_id': 'b192638664804529b455cf2a1aacf661',
                           'id': 'e6c36dd455274e4092c6f959795a9cd0',
                           'publicurl': 'http://127.0.0.1:8003/api'},
                          {'adminurl': 'http://127.0.0.1:8003/ostf',
                           'region': 'RegionOne', 'enabled': True,
                           'internalurl': 'http://127.0.0.1:8003/ostf',
                           'service_id': '8022ba1deb954c358168a84334bd69c3',
                           'id': '7c0ab0939231438a83a5b930b88dc7b2',
                           'publicurl': 'http://127.0.0.1:8003/ostf'}]

        super(TestEndpoint, self).setUp()
        self.keystone_client_patcher = mock.patch('fuelclient.client.Client.'
                                                  'keystone_client')
        self.keystone_client_mock = self.keystone_client_patcher.start()
        self.keystone_client_mock.services.list.return_value = [
            services.Service(self, res, loaded=True) for res in fake_services]
        self.keystone_client_mock.endpoints.list.return_value = [
            endpoints.Endpoint(self, res, loaded=True)
            for res in fake_endpoints]

        self.addCleanup(self.keystone_client_patcher.stop)

    def test_return_endpoint(self):
        cl = client.APIClient
        ostf_root = cl._get_endpoint_url('ostf')
        api_root = cl._get_endpoint_url('nailgun')

        self.assertEqual('http://127.0.0.1:8003/ostf', ostf_root)
        self.assertEqual('http://127.0.0.1:8003/api', api_root)
