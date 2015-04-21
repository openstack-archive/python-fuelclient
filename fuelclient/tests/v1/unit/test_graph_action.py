# -*- coding: utf-8 -*-

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


import io
import os

import mock
import requests_mock

from fuelclient.cli.actions import graph
from fuelclient.tests import base


GRAPH_API_OUTPUT = "digraph G { A -> B -> C }"
TASKS_API_OUTPUT = [
    {'id': 'primary-controller'},
    {'id': 'sync-time'},
]


class TestGraphAction(base.UnitTestCase):

    def setUp(self):
        super(TestGraphAction, self).setUp()
        self.requests_mock = requests_mock.mock()
        self.requests_mock.start()
        self.m_tasks_api = self.requests_mock.get(
            '/api/v1/clusters/1/deployment_tasks',
            json=TASKS_API_OUTPUT)
        self.m_graph_api = self.requests_mock.get(
            '/api/v1/clusters/1/deploy_tasks/graph.gv',
            text=GRAPH_API_OUTPUT)

        self.m_full_path = mock.patch.object(graph.GraphAction,
                                             'full_path_directory').start()
        self.m_full_path.return_value = '/path'

    def tearDown(self):
        super(TestGraphAction, self).tearDown()
        self.requests_mock.stop()
        self.m_full_path.stop()

    def test_download_all_tasks(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1', '--download']
            )

        querystring = self.m_graph_api.last_request.qs
        for task in TASKS_API_OUTPUT:
            self.assertIn(task['id'], querystring['tasks'][0])
        self.assertIn(GRAPH_API_OUTPUT, m_stdout.getvalue())

    def test_download_selected_tasks(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1',
                 '--tasks', 'task-a', 'task-b']
            )

        querystring = self.m_graph_api.last_request.qs
        self.assertIn('task-a', querystring['tasks'][0])
        self.assertIn('task-b', querystring['tasks'][0])
        self.assertIn(GRAPH_API_OUTPUT, m_stdout.getvalue())

    def test_download_with_skip(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1',
                 '--skip', 'sync-time', 'task-b']
            )
        querystring = self.m_graph_api.last_request.qs
        self.assertIn('primary-controller', querystring['tasks'][0])
        self.assertNotIn('sync-time', querystring['tasks'][0])
        self.assertNotIn('task-b', querystring['tasks'][0])
        self.assertIn(GRAPH_API_OUTPUT, m_stdout.getvalue())

    def test_download_with_end_and_start(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1',
                 '--start', 'task-a', '--end', 'task-b']
            )

        tasks_qs = self.m_tasks_api.last_request.qs
        self.assertEqual('task-a', tasks_qs['start'][0])
        self.assertEqual('task-b', tasks_qs['end'][0])

        graph_qs = self.m_graph_api.last_request.qs
        for task in TASKS_API_OUTPUT:
            self.assertIn(task['id'], graph_qs['tasks'][0])
        self.assertIn(GRAPH_API_OUTPUT, m_stdout.getvalue())

    def test_download_only_parents(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1',
                 '--parents-for', 'task-z']
            )
        querystring = self.m_graph_api.last_request.qs
        self.assertEqual('task-z', querystring['parents_for'][0])
        self.assertIn(GRAPH_API_OUTPUT, m_stdout.getvalue())

    def test_download_with_removed(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1',
                 '--remove', 'skipped']
            )
        querystring = self.m_graph_api.last_request.qs
        self.assertEqual('skipped', querystring['remove'][0])
        self.assertIn(GRAPH_API_OUTPUT, m_stdout.getvalue())

    def test_params_saved_in_dotfile(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as m_stdout:
            self.execute(
                ['fuel', 'graph', '--download', '--env', '1',
                 '--parents-for', 'task-z',
                 '--skip', 'task-a']
            )
        saved_params = ("# params:\n"
                        "# - start: None\n"
                        "# - end: None\n"
                        "# - skip: ['task-a']\n"
                        "# - tasks: []\n"
                        "# - parents-for: task-z\n"
                        "# - remove: []\n")
        self.assertIn(saved_params + GRAPH_API_OUTPUT, m_stdout.getvalue())

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    @mock.patch('fuelclient.cli.actions.graph.render_graph')
    @mock.patch('fuelclient.cli.actions.graph.os.access')
    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    def test_render(self, m_exists, m_access, m_render, m_open):
        graph_data = 'some-dot-data'
        m_exists.return_value = True
        m_open().__enter__().read.return_value = graph_data

        self.execute(
            ['fuel', 'graph', '--render', 'graph.gv']
        )

        m_open.assert_called_with('graph.gv', 'r')
        m_render.assert_called_once_with(graph_data, '/path/graph.gv.png')

    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    def test_render_no_file(self, m_exists):
        m_exists.return_value = False
        with self.assertRaises(SystemExit):
            self.execute(
                ['fuel', 'graph', '--render', 'graph.gv']
            )

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    @mock.patch('fuelclient.cli.actions.graph.render_graph')
    @mock.patch('fuelclient.cli.actions.graph.os.access')
    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    def test_render_with_output_path(self, m_exists, m_access, m_render,
                                     m_open):
        output_dir = '/output/dir'
        graph_data = 'some-dot-data'
        m_exists.return_value = True
        m_open().__enter__().read.return_value = graph_data
        self.m_full_path.return_value = output_dir

        self.execute(
            ['fuel', 'graph', '--render', 'graph.gv', '--dir', output_dir]
        )

        self.m_full_path.assert_called_once_with(output_dir, '')
        m_render.assert_called_once_with(graph_data,
                                         '/output/dir/graph.gv.png')

    @mock.patch('fuelclient.cli.actions.graph.os.access')
    @mock.patch('fuelclient.cli.actions.graph.render_graph')
    def test_render_from_stdin(self, m_render, m_access):
        graph_data = u'graph data'

        with mock.patch('sys.stdin', new=io.StringIO(graph_data)):
            self.execute(
                ['fuel', 'graph', '--render', '-', ]
            )

        m_render.assert_called_once_with(graph_data, '/path/graph.gv.png')

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    @mock.patch('fuelclient.cli.actions.graph.os.access')
    def test_render_no_access_to_output(self, m_access, m_exists, m_open):
        m_exists.return_value = True
        m_access.return_value = False
        output_dir = '/output/dir'
        self.m_full_path.return_value = output_dir

        with self.assertRaises(SystemExit):
            self.execute(
                ['fuel', 'graph', '--render', 'graph.gv', '--dir', output_dir]
            )
        m_access.assert_called_once_with(output_dir, os.W_OK)
