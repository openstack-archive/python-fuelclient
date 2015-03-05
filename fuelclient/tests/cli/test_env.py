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

from fuelclient.tests.cli import test_v2_engine
from fuelclient.v1 import environment


class TestEnvCommand(test_v2_engine.BaseCLITest):

    def test_env_list(self):
        args = 'env list'.split()
        self.exec_v2_command(*args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_env_show(self):
        args = 'env show 42'.split()
        self.exec_v2_command(*args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(42)

    def test_env_create(self):
        args = 'env create -r 1 -m ha_compact -n neutron -nst gre env42'
        self.exec_v2_command(*args.split())

        self.m_get_client.assert_called_once_with('environment', mock.ANY)

        m_client = self.m_client
        m_client.create.assert_called_once_with(name='env42',
                                                release_id=1,
                                                network_provider='neutron',
                                                deployment_mode='ha_compact',
                                                net_segment_type='gre')

    def test_env_delete(self):
        args = 'env delete 42'.split()
        self.exec_v2_command(*args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.delete_by_id.assert_called_once_with(42)

    def test_env_deploy(self):
        args = 'env deploy 42'.split()
        self.exec_v2_command(*args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.deploy_changes.assert_called_once_with(42)

    def test_env_add_nodes(self):
        args = 'env add nodes -e 42 -n 24,25 -r compute,cinder'
        self.exec_v2_command(*args.split())

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.add_nodes.assert_called_once_with(environment_id=42,
                                                        nodes=[24, 25],
                                                        roles=['compute',
                                                               'cinder'])

    def test_env_update(self):
        self.m_client._updatable_attributes = \
            environment.EnvironmentClient._updatable_attributes

        args = 'env update 42 -m ha_compact -n test_name'
        self.exec_v2_command(*args.split())

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.update.assert_called_once_with(environment_id=42,
                                                     name='test_name',
                                                     mode='ha_compact')

    def test_env_upgrade(self):
        args = 'env upgrade 10 15'.split()
        self.exec_v2_command(*args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.upgrade.assert_called_once_with(10, 15)
