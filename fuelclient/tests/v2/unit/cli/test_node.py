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

from fuelclient.tests.utils import fake_node
from fuelclient.tests.v2.unit.cli import test_engine


class TestNodeCommand(test_engine.BaseCLITest):
    """Tests for fuel2 node * commands."""

    def setUp(self):
        super(TestNodeCommand, self).setUp()

        self.m_client.get_all.return_value = [fake_node.get_fake_node()
                                              for i in range(10)]
        self.m_client.get_by_id.return_value = fake_node.get_fake_node()

    def test_node_list(self):
        args = 'node list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(environment_id=None)

    def test_node_list_with_env(self):
        env_id = 42
        args = 'node list --env {env}'.format(env=env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(environment_id=env_id)

    def test_node_show(self):
        node_id = 42
        args = 'node show {node_id}'.format(node_id=node_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(node_id)

    def test_node_vms_conf_list(self):
        node_id = 42
        args = 'node list-vms-conf {node_id}'.format(node_id=node_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_node_vms_conf.assert_called_once_with(node_id)

    def test_node_vms_conf_create(self):
        vms_conf = """{"id":2} {"id":3}"""
        config = [{'id': 2},
                  {'id': 3}]

        node_id = 42

        args = "node create-vms-conf {0} --conf {1}".format(
            node_id,
            vms_conf)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.node_vms_create.assert_called_once_with(node_id, config)

    def test_node_set_hostname(self):
        node_id = 42
        hostname = 'test-name'

        self.m_client.set_hostname.return_value = \
            fake_node.get_fake_node(node_id=node_id,
                                    hostname=hostname)

        args = 'node set-hostname {node_id} {hostname}'\
            .format(node_id=node_id, hostname=hostname)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_hostname.assert_called_once_with(node_id, hostname)
