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

from fuelclient.tests.unit.v2.cli import test_engine


class TestVIPActions(test_engine.BaseCLITest):

    def _test_cmd(self, method, cmd_line, expected_kwargs):
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        self.m_client.__getattr__(method).return_value = 'vips_1.yaml'
        self.exec_command('vip {0} {1}'.format(method, cmd_line))
        self.m_get_client.assert_called_once_with('vip', mock.ANY)
        self.m_client.__getattr__(method).assert_called_once_with(
            **expected_kwargs)

    def test_vip_create(self):
        expected = {
            "env_id": 1,
            "ip_addr": '127.0.0.1',
            "network": 1,
            "vip_name": 'test',
            "vip_namespace": 'test-namespace'
        }
        cmd_line = (
            '--env {0} --network {1} --address {2} --name {3} --namespace {4}'
            .format(expected['env_id'], expected['network'],
                    expected['ip_addr'], expected['vip_name'],
                    expected['vip_namespace'])
        )
        self._test_cmd('create', cmd_line, expected)

    def test_vip_download(self):
        self._test_cmd('download', '--env 1', dict(
            env_id=1,
            file_path=None,
            ip_addr_id=None,
            network_id=None,
            network_role=None))

    def test_vip_download_with_network_id(self):
        self._test_cmd('download', '--env 1 --network 3', dict(
            env_id=1,
            file_path=None,
            ip_addr_id=None,
            network_id=3,
            network_role=None))

    def test_vip_download_with_network_role(self):
        self._test_cmd('download', '--env 1 --network-role some/role', dict(
            env_id=1,
            file_path=None,
            ip_addr_id=None,
            network_id=None,
            network_role='some/role'))

    def test_single_vip_download(self):
        self._test_cmd('download', '--env 1 --ip-address-id 5', dict(
            env_id=1,
            file_path=None,
            ip_addr_id=5,
            network_id=None,
            network_role=None))

    def test_vip_upload(self):
        self._test_cmd('upload', '--env 1 --file vips_1.yaml', dict(
            env_id=1,
            file_path='vips_1.yaml'))
