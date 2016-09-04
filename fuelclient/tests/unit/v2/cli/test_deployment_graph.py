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
import six
import yaml

from fuelclient.cli import error
from fuelclient.tests.unit.v2.cli import test_engine

TASKS_YAML = '''- id: custom-task-1
  type: puppet
  parameters:
    param: value
- id: custom-task-2
  type: puppet
  parameters:
    param: value
'''

GRAPH_YAML = '''tasks:
  - id: custom-task-1
    type: puppet
    parameters:
      param: value
  - id: custom-task-2
    type: puppet
    parameters:
      param: value
node_filter: $.pending_deletion
'''

GRAPH_METADATA_YAML = '''
node_filter: $.pending_addition
on_success:
  node_attributes:
     status: provisioned
'''


class TestGraphActions(test_engine.BaseCLITest):
    @mock.patch('fuelclient.commands.graph.os')
    def _test_cmd(self, method, cmd_line, expected_kwargs, os_m):
        os_m.exists.return_value = True
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        m_open = mock.mock_open(read_data=TASKS_YAML)
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True):
            self.exec_command('graph {0} {1}'.format(method, cmd_line))
            self.m_get_client.assert_called_once_with('graph', mock.ANY)
            self.m_client.__getattr__(method).assert_called_once_with(
                **expected_kwargs)

    def test_upload(self):
        self._test_cmd(
            'upload', '--env 1 --file new_tasks.yaml -t test', dict(
                data=yaml.load(TASKS_YAML),
                related_model='clusters',
                related_id=1,
                graph_type='test'
            )
        )
        self._test_cmd(
            'upload', '--release 1 --file new_tasks.yaml -t test', dict(
                data=yaml.load(TASKS_YAML),
                related_model='releases',
                related_id=1,
                graph_type='test'
            )
        )
        self._test_cmd(
            'upload', '--plugin 1 --file new_tasks.yaml -t test', dict(
                data=yaml.load(TASKS_YAML),
                related_model='plugins',
                related_id=1,
                graph_type='test'
            )
        )
        self._test_cmd(
            'upload',
            '--plugin 1 --file tasks.yaml --type custom_type',
            dict(
                data=yaml.load(TASKS_YAML),
                related_model='plugins',
                related_id=1,
                graph_type='custom_type'
            )
        )

    @mock.patch('fuelclient.commands.graph.os')
    def test_graph_upload_from_file(self, os_m):
        os_m.path.exists.return_value = True
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        m_open = mock.mock_open(read_data=GRAPH_YAML)
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True):
            self.exec_command(
                'graph upload --env 1 --file new_graph.yaml -t custom'
            )
            self.m_get_client.assert_called_once_with('graph', mock.ANY)
            self.m_client.upload.assert_called_once_with(
                data=yaml.load(GRAPH_YAML),
                related_model='clusters',
                related_id=1,
                graph_type='custom'
            )

    @mock.patch('fuelclient.commands.graph.os')
    @mock.patch('fuelclient.commands.graph.iterfiles')
    @mock.patch('fuelclient.commands.graph.Serializer')
    def test_graph_upload_from_dir(self, serializers_m, iterfiles_m, os_m):
        tasks = yaml.load(TASKS_YAML)
        graph_data = yaml.load(GRAPH_METADATA_YAML)
        os_m.path.exists.return_value = True
        os_m.path.isdir.return_value = True
        serializers_m().read_from_full_path.side_effect = [graph_data, tasks]
        iterfiles_m.return_value = ['tasks.yaml']

        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        m_open = mock.mock_open(read_data=GRAPH_YAML)
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True):
            self.exec_command(
                'graph upload --release 1 --dir /graph/provision -t provision'
            )
            self.m_get_client.assert_called_once_with('graph', mock.ANY)
            self.m_client.upload.assert_called_once_with(
                data=dict(graph_data, tasks=tasks),
                related_model='releases',
                related_id=1,
                graph_type='provision'
            )

    @mock.patch('fuelclient.commands.graph.os')
    @mock.patch('fuelclient.commands.graph.iterfiles')
    def test_graph_upload_from_dir_fail(self, iterfiles_m, os_m):
        os_m.path.isdir.return_value = True
        os_m.path.exists.side_effect = [True, False]
        iterfiles_m.return_value = []
        args = 'graph upload --release 1 --dir /graph/provision -t provision'

        self.assertRaisesRegexp(error.ActionException,
                                "Nothing to upload",
                                self.exec_command, args)

    @mock.patch('sys.stderr')
    def test_upload_fail(self, mocked_stderr):
        cmd = 'graph upload --file new_graph.yaml -t test'
        self.assertRaises(SystemExit, self.exec_command, cmd)
        self.assertIn('-e/--env -r/--release -p/--plugin',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_execute(self):
        self._test_cmd(
            'execute',
            '--env 1 --type custom_graph another_custom_graph --nodes 1 2 3',
            dict(
                env_id=1,
                graph_types=['custom_graph', 'another_custom_graph'],
                nodes=[1, 2, 3],
                task_names=None,
                dry_run=False,
                noop_run=False,
                force=False
            )
        )

    def test_execute_w_dry_run(self):
        self._test_cmd(
            'execute',
            '--env 1 --type custom_graph another_custom_graph '
            '--nodes 1 2 3 --dry-run',
            dict(
                env_id=1,
                graph_types=['custom_graph', 'another_custom_graph'],
                nodes=[1, 2, 3],
                task_names=None,
                dry_run=True,
                noop_run=False,
                force=False
            )
        )

    def test_execute_w_force(self):
        self._test_cmd(
            'execute',
            '--env 1 --force',
            dict(
                env_id=1,
                graph_types=None,
                nodes=None,
                task_names=None,
                dry_run=False,
                noop_run=False,
                force=True
            )
        )

    def test_execute_w_task_names(self):
        self._test_cmd(
            'execute',
            '--env 1 --task-names task1 task2',
            dict(
                env_id=1,
                graph_types=None,
                nodes=None,
                task_names=['task1', 'task2'],
                dry_run=False,
                noop_run=False,
                force=False
            )
        )

    def test_execute_w_noop_run(self):
        self._test_cmd(
            'execute',
            '--env 1 --type custom_graph another_custom_graph '
            '--nodes 1 2 3 --noop',
            dict(
                env_id=1,
                graph_types=['custom_graph', 'another_custom_graph'],
                nodes=[1, 2, 3],
                task_names=None,
                dry_run=False,
                noop_run=True,
                force=False
            )
        )

    def test_download(self):
        self.m_client.download.return_value = yaml.safe_load(TASKS_YAML)

        self._test_cmd(
            'download',
            '--env 1 --all --file existing_graph.yaml --type custom_graph',
            dict(
                env_id=1,
                level='all',
                graph_type='custom_graph'
            )
        )

    def test_list(self):
        with mock.patch('sys.stdout', new=six.moves.cStringIO()) as m_stdout:
            self.m_get_client.reset_mock()
            self.m_client.get_filtered.reset_mock()
            self.m_client.list.return_value = [
                {
                    'name': 'updated-graph-name',
                    'tasks': [{
                        'id': 'test-task2',
                        'type': 'puppet',
                        'task_name': 'test-task2',
                        'version': '2.0.0'
                    }],
                    'relations': [{
                        'model': 'cluster',
                        'model_id': 370,
                        'type': 'custom-graph'
                    }],
                    'id': 1
                }
            ]
            self.exec_command('graph list --env 1')
            self.m_get_client.assert_called_once_with('graph', mock.ANY)
            self.m_client.list.assert_called_once_with(env_id=1)

            self.assertIn('1', m_stdout.getvalue())
            self.assertIn('updated-graph-name', m_stdout.getvalue())
            self.assertIn('custom-graph', m_stdout.getvalue())
            self.assertIn('test-task2', m_stdout.getvalue())
