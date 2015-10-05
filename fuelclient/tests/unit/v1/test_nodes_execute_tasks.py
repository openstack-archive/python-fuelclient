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

from mock import patch
import requests_mock as rm

from fuelclient.tests.unit.v1 import base
from fuelclient.tests.utils import fake_node


class TestNodeExecuteTasksAction(base.UnitTestCase):

    def setUp(self):
        super(TestNodeExecuteTasksAction, self).setUp()
        self.tasks = ['netconfig', 'hiera', 'install']

        node_patch = patch('fuelclient.objects.node.Node.get_fresh_data')
        m_fresh_data = node_patch.start()
        m_fresh_data.return_value = fake_node.get_fake_node()
        self.addCleanup(node_patch.stop)

    def test_execute_provided_list_of_tasks(self):
        put = self.m_request.put(rm.ANY, json={'id': 43})

        self.execute(['fuel', 'node', '--node', '1,2', '--tasks'] + self.tasks)
        self.assertEqual(put.last_request.json(), self.tasks)

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_skipped_tasks(self, get_tasks):
        get_tasks.return_value = [{'id': t} for t in self.tasks]
        put = self.m_request.put(rm.ANY, json={'id': 43})

        self.execute(
            ['fuel', 'node', '--node', '1,2', '--skip'] + self.tasks[:2])

        self.assertEqual(put.last_request.json(), self.tasks[2:])

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_included_tasks(self, get_tasks):
        get_tasks.return_value = [{'id': t} for t in self.tasks]
        put = self.m_request.put(rm.ANY, json={'id': 43})

        self.execute(
            ['fuel', 'node', '--node', '1', '--start', 'netconfig',
             '--tasks', 'hiera'])
        self.assertEqual(put.last_request.json(), self.tasks)
        get_tasks.assert_called_once_with(
            start='netconfig', end=None, include=['hiera'])

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_dont_fail_on_empty_tasks(self, get_tasks):
        get_tasks.return_value = []
        self.execute(
            ['fuel', 'node', '--node', '1', '--start', 'netconfig'])

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_end_param(self, get_tasks):
        put = self.m_request.put(rm.ANY, json={'id': 43})

        get_tasks.return_value = [{'id': t} for t in self.tasks[:2]]
        self.execute(
            ['fuel', 'node', '--node', '1,2', '--end', self.tasks[-2]])
        self.assertEqual(put.last_request.json(), self.tasks[:2])
        get_tasks.assert_called_once_with(
            end=self.tasks[-2], start=None, include=None)

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_skip_with_end_param(self, get_tasks):
        get_tasks.return_value = [{'id': t} for t in self.tasks]
        put = self.m_request.put(rm.ANY, json={'id': 43})
        self.execute(
            ['fuel', 'node', '--node', '1,2',
             '--end', self.tasks[-1], '--skip'] + self.tasks[:2])

        self.assertEqual(put.last_request.json(), self.tasks[2:])
        get_tasks.assert_called_once_with(
            end=self.tasks[-1], start=None, include=None)

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_start_with_end_param(self, get_tasks):
        """end will be included."""
        put = self.m_request.put(rm.ANY, json={'id': 43})
        start = 1
        end = 2
        get_tasks.return_value = [{'id': t} for t in self.tasks[start:end + 1]]
        self.execute(
            ['fuel', 'node', '--node', '1,2', '--start', self.tasks[start],
             '--end', self.tasks[end]])

        self.assertEqual(put.last_request.json(), self.tasks[start:end + 1])
        get_tasks.assert_called_once_with(
            end=self.tasks[2], start=self.tasks[1], include=None)

    @patch('fuelclient.objects.environment.Environment.get_deployment_tasks')
    def test_start_param(self, get_tasks):
        put = self.m_request.put(rm.ANY, json={'id': 43})
        get_tasks.return_value = [{'id': t} for t in self.tasks[1:]]
        self.execute(
            ['fuel', 'node', '--node', '1,2', '--start', self.tasks[1]])

        self.assertEqual(put.last_request.json(), self.tasks[1:])
        get_tasks.assert_called_once_with(
            start=self.tasks[1], end=None, include=None)
