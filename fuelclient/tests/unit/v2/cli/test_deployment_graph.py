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
            '--plugin 1 --file tasks.yaml --graph-type custom_type',
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
            '--env 1 --graph-types graph1 graph2 --nodes 1 2 3',
            dict(
                env_id=1,
                graph_types=['graph1', 'graph2'],
                nodes=[1, 2, 3],
                task_names=None,
                dry_run=False,
                noop_run=False,
                force=False,
                debug=False,
                subgraphs=None
            )
        )

    def test_execute_w_dry_run(self):
        self._test_cmd(
            'execute',
            '--env 1 --graph-types graph1 graph2 --nodes 1 2 3 --dry-run',
            dict(
                env_id=1,
                graph_types=['graph1', 'graph2'],
                nodes=[1, 2, 3],
                task_names=None,
                dry_run=True,
                noop_run=False,
                force=False,
                debug=False,
                subgraphs=None
            )
        )

    def test_execute_w_force(self):
        self._test_cmd(
            'execute',
            '--env 1 --graph-types graph1 --force',
            dict(
                env_id=1,
                graph_types=['graph1'],
                nodes=None,
                task_names=None,
                dry_run=False,
                noop_run=False,
                force=True,
                debug=False,
                subgraphs=None
            )
        )

    def test_execute_w_task_names(self):
        self._test_cmd(
            'execute',
            '--env 1 --graph-types graph1 --task-names task1 task2',
            dict(
                env_id=1,
                graph_types=['graph1'],
                nodes=None,
                task_names=['task1', 'task2'],
                dry_run=False,
                noop_run=False,
                force=False,
                debug=False,
                subgraphs=None
            )
        )

    def test_execute_w_noop_run(self):
        self._test_cmd(
            'execute',
            '--env 1 --graph-types graph1 graph2 --nodes 1 2 3 --noop',
            dict(
                env_id=1,
                graph_types=['graph1', 'graph2'],
                nodes=[1, 2, 3],
                task_names=None,
                dry_run=False,
                noop_run=True,
                force=False,
                debug=False,
                subgraphs=None
            )
        )

    def test_execute_w_trace(self):
        self._test_cmd(
            'execute',
            '--env 1 --graph-types graph1 --trace',
            dict(
                env_id=1,
                graph_types=['graph1'],
                nodes=None,
                task_names=None,
                dry_run=False,
                noop_run=False,
                force=False,
                debug=True,
                subgraphs=None
            )
        )

    def test_execute_w_dry_run_subgraph(self):
        self._test_cmd(
            'execute',
            '--env 1 --graph-types custom_graph --nodes 1 2 3 '
            '--dry-run --subgraphs primary-database/1,3:keystone-db/1-2,5'
            ' openstack-controller',
            dict(
                env_id=1,
                force=False,
                graph_types=['custom_graph'],
                nodes=[1, 2, 3],
                noop_run=False,
                dry_run=True,
                subgraphs=['primary-database/1,3:keystone-db/1-2,5',
                           'openstack-controller'],
                task_names=None,
                debug=False
            )
        )

    def test_execute_with_json_output(self):
        self.m_client.execute.return_value = mock.MagicMock(
            data={'id': 1}
        )
        with mock.patch('sys.stdout') as stdout_mock:
            self.exec_command(
                'graph execute --env 1 --graph-types graph1 --format=json'
            )
        stdout_mock.write.assert_called_with('{\n    "id": 1\n}\n')

    def test_download(self):
        self.m_client.download.return_value = yaml.safe_load(TASKS_YAML)

        self._test_cmd(
            'download',
            '--env 1 --all --file existing_graph.yaml -t custom_graph',
            dict(
                env_id=1,
                level='all',
                graph_type='custom_graph'
            )
        )

    @mock.patch('json.dumps')
    def test_download_json(self, m_dumps):
        env_id = 1
        graph_data = [{'id': 1}]
        args = 'graph download --env {0} --all --format json'.format(env_id)
        expected_path = '/tmp/all_graph_{0}.json'.format(env_id)

        self.m_client.download.return_value = graph_data

        m_open = mock.mock_open()
        with mock.patch('os.path.abspath', return_value='/tmp'):
            with mock.patch(
                    'fuelclient.cli.serializers.open', m_open, create=True):
                self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dumps.assert_called_once_with(graph_data, indent=4)
        self.m_get_client.assert_called_once_with('graph', mock.ANY)

    @mock.patch('sys.stderr')
    def test_download_fail(self, mocked_stderr):
        cmd = 'graph download --env 1'
        self.assertRaises(SystemExit, self.exec_command, cmd)
        self.assertIn('-a/--all -c/--cluster -p/--plugins -r/--release',
                      mocked_stderr.write.call_args_list[-1][0][0])

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
            self.exec_command(
                'graph list --env 1 --release --plugins --cluster')
            self.m_get_client.assert_called_once_with('graph', mock.ANY)

            self.assertIn('1', m_stdout.getvalue())
            self.assertIn('updated-graph-name', m_stdout.getvalue())
            self.assertIn('custom-graph', m_stdout.getvalue())
            self.assertIn('test-task2', m_stdout.getvalue())

            self.exec_command('graph list --release')
            self.exec_command('graph list --plugins')
            self.exec_command('graph list --cluster')
            self.exec_command('graph list')

            self.m_client.list.assert_has_calls([
                mock.call(env_id=1, filters=['release', 'plugin', 'cluster']),
                mock.call(env_id=None, filters=['release']),
                mock.call(env_id=None, filters=['plugin']),
                mock.call(env_id=None, filters=['cluster']),
                mock.call(env_id=None, filters=None)
            ])

    def test_delete(self):
        self._test_cmd(
            'delete',
            '--env 1 --graph-type custom_graph',
            dict(
                graph_type='custom_graph',
                related_id=1,
                related_model='clusters'
            )
        )
