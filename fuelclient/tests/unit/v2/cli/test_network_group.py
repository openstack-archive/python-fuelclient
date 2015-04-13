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
import mock

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_network_group
from fuelclient.v1.network_group import NetworkGroupClient


class TestNetworkGroupCommand(test_engine.BaseCLITest):

    def setUp(self):
        super(TestNetworkGroupCommand, self).setUp()

        get_fake_ng = fake_network_group.get_fake_network_group

        self.m_client.get_all.return_value = [
            get_fake_ng() for _ in range(10)]
        self.m_client.get_by_id.return_value = get_fake_ng()
        self.m_client.create.return_value = get_fake_ng()

    def test_network_group_list(self):
        args = 'network-group list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('network-group', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_network_group_show(self):
        args = 'network-group show 1'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('network-group', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(1)

    def test_network_group_create(self):
        meta = {'notation': 'cidr'}
        meta_str = json.dumps(meta).replace(r'"', r'\"')

        args = 'network-group create -N 8 -C 10.10.0.0/24 -g 10.10.0.1' \
               ' -V 16 -r 32 testng --meta "{0}"'.format(meta_str)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('network-group', mock.ANY)

        m_client = self.m_client
        m_client.create.assert_called_once_with(
            name='testng', group_id=8, cidr='10.10.0.0/24', vlan=16,
            release=32, gateway='10.10.0.1', meta=meta)

    def test_network_group_update(self):
        self.m_client.updatable_attributes = \
            NetworkGroupClient.updatable_attributes

        meta = {'notation': 'cidr'}
        meta_str = json.dumps(meta).replace(r'"', r'\"')

        args = 'network-group update -C 10.10.0.0/24' \
               ' --meta "{0}" 1'.format(meta_str)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('network-group', mock.ANY)

        m_client = self.m_client
        m_client.update.assert_called_once_with(
            1, cidr='10.10.0.0/24', meta=meta)

    def test_network_group_delete(self):
        args = 'network-group delete 42'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('network-group', mock.ANY)
        self.m_client.delete_by_id.assert_called_once_with(42)
