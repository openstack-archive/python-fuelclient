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

from fuelclient.cli.formatting import format_table
from fuelclient.cli.serializers import Serializer
from fuelclient.tests.unit.v1 import base
from fuelclient.tests import utils
from fuelclient.v1.deployment_history import DeploymentHistoryClient

GROUPED_TASKS_DATA = [
    {
        'task_name': 'controller_remaining_tasks',

        'status_by_node': [
            {
                'time_start': '2016-03-25T17:22:10.687135',
                'task_name': 'controller_remaining_tasks',
                'status': 'ready',
                'time_end': '2016-03-25T17:22:30.830701',
                'node_id': '1'
            },
            {
                'time_start': '2016-03-25T17:22:10.687135',
                'task_name': 'controller_remaining_tasks',
                'status': 'ready',
                'time_end': '2016-03-25T17:22:30.830701',
                'node_id': '2'
            }],

        'task_parameters': {
            'type': 'puppet',
            'role': ['controller'],
            'id': 'controller_remaining_tasks',
            'version': '2.0.0',
            'parameters': {
                'timeout': 3600,
                'puppet_modules': '/etc/puppet/modules',
                'puppet_manifest': '/etc/puppet/modules'
                                   '/osnailyfacter/modular'
                                   '/globals/globals.pp'
            },
        }
    }
]


class TestDeploymentTasksAction(base.UnitTestCase):

    @patch.object(Serializer, 'print_to_output')
    def test_show_full_history(self, print_mock):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?'
            'nodes=&'
            'statuses=&'
            'tasks_names=',
            json=utils.get_fake_deployment_history())

        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1']
        )

        print_mock.assert_called_once_with(
            utils.get_fake_deployment_history(convert_legacy_fields=True),
            format_table(
                utils.get_fake_deployment_history(convert_legacy_fields=True),
                acceptable_keys=DeploymentHistoryClient.history_records_keys))

    @patch.object(Serializer, 'print_to_output')
    def test_show_tasks_history(self, print_mock):
        tasks_after_facade = [{
            'task_parameters': 'parameters: {puppet_manifest: /etc/puppet'
                               '/modules/osnailyfacter/modular/globals/'
                               'globals.pp,\n  puppet_modules: /etc/'
                               'puppet/modules, timeout: 3600}\nrole: '
                               '[controller]\ntype: puppet\nversion: '
                               '2.0.0\n',
            'task_name': u'controller_remaining_tasks',
            'status_by_node': '1 ready 2016-03-25T17:22:10 - '
                              '2016-03-25T17:22:30\n2 ready 2016-03-25T17'
                              ':22:10 - 2016-03-25T17:22:30'
        }]

        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?'
            'nodes=&'
            'statuses=&'
            'tasks_names=controller_remaining_tasks',
            json=utils.get_fake_deployment_history(add_task_data=True))

        self.execute(
            ['fuel', 'deployment-tasks',
             '--tid', '1',
             '--task-name', 'controller_remaining_tasks']
        )

        print_mock.assert_called_once_with(
            tasks_after_facade,
            format_table(
                tasks_after_facade,
                acceptable_keys=DeploymentHistoryClient.tasks_records_keys))

    def test_show_history_for_special_nodes(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?'
            'nodes=1,2&'
            'statuses=&'
            'tasks_names=',
            json={})

        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--node-id', '1,2']
        )

        self.assertEqual(self.m_history_api.call_count, 1)

    def test_show_history_for_special_tasks(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?'
            'nodes=&'
            'statuses=&'
            'tasks_names=test1,test2',
            json={})

        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--task-name', 'test1,test2']
        )

        self.assertEqual(self.m_history_api.call_count, 1)

    def test_show_history_with_special_statuses(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?'
            'nodes=&'
            'statuses=ready,skipped&'
            'tasks_names=',
            json={})
        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--status', 'ready,skipped']
        )
        self.assertEqual(self.m_history_api.call_count, 1)

    def test_show_history_for_special_statuses_nodes_and_tasks(self):
        self.m_history_api = self.m_request.get(
            '/api/v1/transactions/1/deployment_history/?'
            'nodes=1,2&'
            'statuses=ready,skipped&'
            'tasks_names=test1,test2',
            json={})
        self.execute(
            ['fuel', 'deployment-tasks', '--tid', '1',
             '--status', 'ready,skipped', '--node', '1,2',
             '--task-name', 'test1,test2']
        )
        self.assertEqual(self.m_history_api.call_count, 1)
