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

from six import moves

from fuelclient.tests.unit.v2.cli import test_engine


class TestGraphActions(test_engine.BaseCLITest):

    def _test_cmd(self, method, cmd_line, expected_kwargs):
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        self.m_client.__getattr__(method).return_value = 'graph.yaml'
        self.exec_command('graph {0} {1}'.format(method, cmd_line))
        self.m_get_client.assert_called_once_with('graph', mock.ANY)
        self.m_client.__getattr__(method).assert_called_once_with(
            **expected_kwargs)

    def test_upload(self):
        self._test_cmd('upload', '--env 1 --file new_graph.yaml', dict(
            graph_type=None,
            file_path='new_graph.yaml',
            cluster_id=1,
            release_id=None,
            plugin_id=None,
        ))
        self._test_cmd('upload', '--release 1 --file new_graph.yaml', dict(
            graph_type=None,
            file_path='new_graph.yaml',
            cluster_id=None,
            release_id=1,
            plugin_id=None,
        ))
        self._test_cmd('upload', '--plugin 1 --file new_graph.yaml', dict(
            graph_type=None,
            file_path='new_graph.yaml',
            cluster_id=None,
            release_id=None,
            plugin_id=1,
        ))
        self._test_cmd('upload', '--file new_graph.yaml', dict(
            graph_type=None,
            file_path='new_graph.yaml',
            cluster_id=None,
            release_id=None,
            plugin_id=None,
        ))

    def test_execute(self):
        self._test_cmd(
            'execute',
            '--env 1 --type custom_graph --nodes 1 2 3',
            dict(
                env_id=1,
                graph_type='custom_graph',
                nodes=[1, 2, 3]
            )
        )
