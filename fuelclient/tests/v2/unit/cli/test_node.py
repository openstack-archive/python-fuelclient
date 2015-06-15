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

from fuelclient.tests.v2.unit.cli import test_engine
from fuelclient import utils


class TestNodeCommand(test_engine.BaseCLITest):
    """Tests for fuel2 node * commands."""

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

    def test_node_vms_list(self):
        node_id = 42
        args = 'node vms-list {node_id}'.format(node_id=node_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_node_vms_list.assert_called_once_with(node_id)

    def test_node_vms_create(self):
        config = [{'opt1': 'val1', 'opt2': 'val2'},
                  {'opt3': 'val3', 'opt4': 'val4'}]

        def file_exists(file_path):
            return True

        def parse_json_file(file_path):
            return config

        utils.file_exists = file_exists
        utils.parse_json_file = parse_json_file

        node_id = 42
        config_file_path = '/some/path'

        args = "node vms-create {0} --conf {1}".format(
            node_id,
            config_file_path)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.node_vms_create.assert_called_once_with(node_id, config)
