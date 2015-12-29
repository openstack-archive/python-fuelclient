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

import mock
import yaml

from fuelclient.tests.unit.v1 import base

ENV_OUTPUT = {
    "status": "new",
    "is_customized": False,
    "release_id": 2,
    "ui_settings": {
        "sort": [{"roles": "asc"}],
        "sort_by_labels": [],
        "search": "",
        "filter_by_labels": {},
        "filter": {},
        "view_mode": "standard"
    },
    "is_locked": False,
    "fuel_version": "8.0",
    "net_provider": "neutron",
    "mode": "ha_compact",
    "components": [],
    "pending_release_id": None,
    "changes": [
        {"node_id": None, "name": "attributes"},
        {"node_id": None, "name": "networks"},
        {"node_id": None, "name": "vmware_attributes"}],
    "id": 6, "name": "test_not_deployed"}


MANY_VIPS_YAML = '''- id: 5
  network: 3
  node: null
  ip_addr: 192.169.1.33
  vip_name: public
  is_user_defined: false
- id: 6
  network: 3
  node: null
  ip_addr: 192.169.1.34
  vip_name: private
  is_user_defined: false
'''

ONE_VIP_YAML = '''
- id: 5
  network: 3
  node: null
  ip_addr: 192.169.1.33
  vip_name: public
  is_user_defined: false
'''


@mock.patch('fuelclient.cli.serializers.open', create=True)
@mock.patch('fuelclient.cli.actions.base.os')
class TestVIPActions(base.UnitTestCase):

    def test_env_vips_download(self, mos, mopen):
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        url = '/api/v1/clusters/1/network_configuration/ips/vips/'
        get_request = self.m_request.get(
            url,
            json=yaml.load(MANY_VIPS_YAML))
        self.execute('fuel vip --env 1 --download'.split())
        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)
        self.assertEqual(1, mopen().__enter__().write.call_count)
        self.assertEqual(
            yaml.safe_load(MANY_VIPS_YAML),
            yaml.safe_load(mopen().__enter__().write.call_args[0][0]),
        )

    def test_env_vips_download_with_network_id(self, mos, mopen):
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        url = '/api/v1/clusters/1/network_configuration/ips/vips/'
        get_request = self.m_request.get(
            url,
            json=yaml.load(MANY_VIPS_YAML))
        self.execute('fuel vip --env 1 --network 3 --download'.split())
        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)
        self.assertEqual(1, mopen().__enter__().write.call_count)
        self.assertEqual(
            yaml.safe_load(MANY_VIPS_YAML),
            yaml.safe_load(mopen().__enter__().write.call_args[0][0]),
        )

    def test_env_vips_download_with_network_role(self, mos, mopen):
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        url = '/api/v1/clusters/1/network_configuration/ips/vips/'
        get_request = self.m_request.get(
            url,
            json=yaml.load(MANY_VIPS_YAML))
        self.execute(
            'fuel vip --env 1 --network-role some/role --download'.split())
        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)
        self.assertEqual(1, mopen().__enter__().write.call_count)
        self.assertEqual(
            yaml.safe_load(MANY_VIPS_YAML),
            yaml.safe_load(mopen().__enter__().write.call_args[0][0]),
        )

    def test_env_single_vip_download(self, mos, mopen):
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        url = '/api/v1/clusters/1/network_configuration/ips/5/vips/'
        get_request = self.m_request.get(
            url,
            json=yaml.safe_load(ONE_VIP_YAML)[0]
        )
        self.execute('fuel vip --env 1 --ip 5 --download'.split())

        self.assertTrue(get_request.called)
        self.assertIn(url, get_request.last_request.url)
        self.assertEqual(1, mopen().__enter__().write.call_count)

        self.assertEqual(
            yaml.safe_load(ONE_VIP_YAML),
            yaml.safe_load(mopen().__enter__().write.call_args[0][0]),
        )

    def test_vips_upload(self, mos, mopen):
        url = '/api/v1/clusters/1/network_configuration/ips/vips/'
        mopen().__enter__().read.return_value = MANY_VIPS_YAML
        self.m_request.get('/api/v1/clusters/1/', json=ENV_OUTPUT)
        # todo(ikutukov): maybe some confirmation message should be returned?
        request_put = self.m_request.put(url, json={})
        with mock.patch('fuelclient.objects.environment.os') as env_os:
            env_os.path.exists.return_value = True
            self.execute('fuel vip --env 1 --upload vips_1.yaml'.split())
        self.assertEqual(request_put.call_count, 1)
        self.assertIn(url, request_put.last_request.url)
