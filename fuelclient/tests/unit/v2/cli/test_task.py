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
import os
import yaml

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests import utils
from fuelclient.v1.deployment_history import DeploymentHistoryClient


class TestTaskCommand(test_engine.BaseCLITest):

    def setUp(self):
        super(TestTaskCommand, self).setUp()

        self.m_client.get_all.return_value = [utils.get_fake_task()
                                              for _ in range(10)]
        self.m_client.get_by_id.return_value = utils.get_fake_task()
        self.current_path = os.path.join(os.path.abspath(os.curdir))

    def test_task_list(self):
        args = 'task list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_task_list_w_parameters(self):
        env_id = 45
        statuses = ['ready', 'error']
        names = ['provision', 'dump']
        args = 'task list -e {env_id} -t {statuses} -n {names}'.format(
            env_id=env_id,
            statuses=' '.join(statuses),
            names=' '.join(names))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_all.assert_called_once_with(cluster_id=env_id,
                                                      statuses=statuses,
                                                      transaction_types=names)

    @mock.patch('sys.stderr')
    def test_task_list_w_wrong_parameters(self, mocked_stderr):
        statuses = ['ready', 'wrong_status']
        args = 'task list -t {statuses}'.format(statuses=' '.join(statuses))
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-t/--statuses: invalid choice',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_task_show(self):
        task_id = 42
        args = 'task show {task_id}'.format(task_id=task_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(task_id)

    def test_task_delete(self):
        task_id = 42
        args = 'task delete {task_id}'.format(task_id=task_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.delete_by_id.assert_called_once_with(task_id, False)

    def test_task_delete_force(self):
        task_id = 42
        args = 'task delete --force {task_id}'.format(task_id=task_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.delete_by_id.assert_called_once_with(task_id, True)

    def test_task_history_show(self):
        task_id = 42
        args = 'task history show {task_id} '.format(task_id=task_id)

        self.m_client.get_all.return_value = \
            utils.get_fake_deployment_history()
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('deployment_history',
                                                  mock.ANY)
        self.m_client.get_all.assert_called_once_with(transaction_id=task_id,
                                                      nodes=None,
                                                      statuses=None,
                                                      tasks_names=None,
                                                      include_summary=False,
                                                      show_parameters=False)

    def test_task_history_show_include_summary(self):
        task_id = 42
        args = 'task history show {task_id} '.format(task_id=task_id)
        args += '--include-summary '

        self.m_client.get_all.return_value = \
            utils.get_fake_deployment_history(include_summary=True)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('deployment_history',
                                                  mock.ANY)
        self.m_client.get_all.assert_called_once_with(transaction_id=task_id,
                                                      nodes=None,
                                                      statuses=None,
                                                      tasks_names=None,
                                                      include_summary=True,
                                                      show_parameters=False)

    def test_task_history_parameters(self):
        task_id = 42
        args = 'task history show {task_id} ' \
               '--tasks-names task1 task2 ' \
               '--statuses ready error --nodes 1 2 ' \
               '--show-parameters'.format(task_id=task_id)

        self.m_client.get_all.return_value = \
            utils.get_fake_deployment_history()
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('deployment_history',
                                                  mock.ANY)
        self.m_client.get_all.assert_called_once_with(
            transaction_id=task_id, nodes=['1', '2'],
            statuses=['ready', 'error'], tasks_names=['task1', 'task2'],
            include_summary=False,
            show_parameters=True)

    def _test_cmd(self, cmd, method, cmd_line, client,
                  return_data, expected_file_path, expected_kwargs):
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        self.m_client.__getattr__(method).return_value =\
            yaml.safe_load(return_data)
        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.exec_command('task {0} {1} {2}'.format(cmd, method,
                                                        cmd_line))

        m_open.assert_called_once_with(expected_file_path, 'w')
        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        expected_yaml = yaml.safe_load(return_data)
        self.assertEqual(written_yaml, expected_yaml)

        self.m_get_client.assert_called_once_with(client, mock.ANY)
        self.m_client.__getattr__(method).assert_called_once_with(
            **expected_kwargs)

    def test_task_deployment_info_download(self):
        self._test_cmd('deployment-info', 'download', '1 ',
                       'deployment-info',
                       utils.get_fake_yaml_deployment_info(),
                       "{0}/deployment_info_1.yaml".format(
                           self.current_path),
                       dict(transaction_id=1))

    def test_task_cluster_settings_download(self):
        self._test_cmd('settings', 'download', '1 --file settings.yaml',
                       'cluster-settings',
                       utils.get_fake_yaml_cluster_settings(),
                       'settings.yaml',
                       dict(transaction_id=1))

    def test_task_network_configuration_download(self):
        self._test_cmd('network-configuration', 'download', '1',
                       'network-configuration',
                       utils.get_fake_yaml_network_conf(),
                       "{0}/network_configuration_1.yaml".format(
                           self.current_path),
                       dict(transaction_id=1))


class TestDeploymentTasksAction(test_engine.BaseCLITest):

    @mock.patch('cliff.formatters.table.TableFormatter.emit_list')
    def test_show_tasks_history_with_parameters(self, m_formatter):
        tasks_after_facade = utils.get_fake_deployment_history_w_params()

        expected_fields = ('task_name', 'task_parameters', 'status_by_node')
        expected_data = [
            [
                'controller-remaining-tasks',

                'parameters: {puppet_manifest: /etc/puppet/modules/osnailyfact'
                'er/modular/globals/globals.pp,\n  puppet_modules: /etc/'
                'puppet/modules, timeout: 3600}\nrole: [controller]\ntype: '
                'puppet\nversion: 2.0.0\n',

                '1 - ready - 2016-03-25T17:22:10 - 2016-03-25T17:22:30\n'
                '2 - ready - 2016-03-25T17:22:10 - 2016-03-25T17:22:30'
            ],
            [
                'pending-task',

                'parameters: {puppet_manifest: /etc/puppet/modules/osnailyfact'
                'er/modular/globals/globals.pp,\n  puppet_modules: /etc/puppet'
                '/modules, timeout: 3600}\nrole: [controller]\ntype: '
                'puppet\nversion: 2.0.0\n',

                '1 - pending - not started - not ended\n'
                '2 - pending - not started - not ended'
            ],
            [
                'ironic-compute',
                'parameters: {puppet_manifest: /etc/puppet/modules/osnailyfact'
                'er/modular/globals/globals.pp,\n  puppet_modules: /etc/'
                'puppet/modules, timeout: 3600}\nrole: [controller]\ntype: '
                'puppet\nversion: 2.0.0\n',

                '1 - skipped - 2016-03-25T17:23:37 - 2016-03-25T17:23:37\n'
                '2 - skipped - 2016-03-25T17:23:37 - 2016-03-25T17:23:37'
            ]
        ]
        self.m_client.get_all.return_value = tasks_after_facade
        self.m_client.tasks_records_keys = \
            DeploymentHistoryClient.tasks_records_keys
        self.m_client.history_records_keys = \
            DeploymentHistoryClient.history_records_keys

        self.exec_command(
            ' '.join((
                'task history show', '1',
                '--nodes', '1 2',
                '--statuses', 'ready',
                '--tasks-names', 'taskname1 taskname2',
                '--show-parameters'
            ))
        )

        self.m_client.get_all.assert_called_with(
            nodes=['1', '2'],
            statuses=['ready'],
            tasks_names=['taskname1', 'taskname2'],
            transaction_id=1,
            include_summary=False,
            show_parameters=True)

        m_formatter.assert_called_once_with(expected_fields,
                                            expected_data,
                                            mock.ANY,
                                            mock.ANY)
