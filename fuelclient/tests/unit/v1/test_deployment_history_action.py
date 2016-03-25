# -*- coding: utf-8 -*-

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

from mock import patch

from fuelclient.cli.actions import DeploymentTasksAction
from fuelclient.cli.formatting import format_table
from fuelclient.cli.serializers import Serializer
from fuelclient.tests.unit.v1 import base


HISTORY_API_OUTPUT = [
    {
        "status": "ready",
        "time_start": "2016-03-25T17:22:10.687135",
        "time_end": "2016-03-25T17:22:30.830701",
        "node_id": "1",
        "deployment_graph_task_name": "controller_remaining_tasks"
    },
    {
        "status": "skipped",
        "time_start": "2016-03-25T17:23:37.313212",
        "time_end": "2016-03-25T17:23:37.313234",
        "node_id": "2",
        "deployment_graph_task_name": "ironic-compute"
    }
]


class TestDeploymentTasksAction(base.UnitTestCase):

    def assert_print_table(self, print_mock, tasks):
        print_mock.assert_called_once_with(
            tasks, format_table(
                tasks,
                acceptable_keys=DeploymentTasksAction.acceptable_keys))

    @patch.object(Serializer, 'print_to_output')
    def test_show_full_history(self, print_mock):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?nodes=&statuses=',
            json=HISTORY_API_OUTPUT)

        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1']
        )

        self.assert_print_table(print_mock, HISTORY_API_OUTPUT)

    def test_show_history_for_special_nodes(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?nodes=1,2&statuses=',
            json={})

        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--node-id', '1,2']
        )

        self.assertEqual(self.m_history_api.call_count, 1)

    def test_show_history_with_special_statuses(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/'
            '?nodes=&statuses=ready,skipped',
            json={})
        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--status', 'ready,skipped']
        )
        self.assertEqual(self.m_history_api.call_count, 1)

    def test_show_history_with_special_statuses_for_special_nodes(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/'
            '?nodes=1,2&statuses=ready,skipped',
            json={})
        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--status', 'ready,skipped', '--node', '1,2']
        )
        self.assertEqual(self.m_history_api.call_count, 1)
