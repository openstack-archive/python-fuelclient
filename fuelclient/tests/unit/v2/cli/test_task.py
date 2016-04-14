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
import yaml

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests import utils


class TestTaskCommand(test_engine.BaseCLITest):

    def setUp(self):
        super(TestTaskCommand, self).setUp()

        self.m_client.get_all.return_value = [utils.get_fake_task()
                                              for i in range(10)]
        self.m_client.get_by_id.return_value = utils.get_fake_task()

    def test_task_list(self):
        args = 'task list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_task_show(self):
        task_id = 42
        args = 'task show {task_id}'.format(task_id=task_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(task_id)

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
                                                      statuses=None)

    def _test_cmd(self, cmd, method, cmd_line, client,
                  return_data, expected_kwargs):
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        self.m_client.__getattr__(method).return_value =\
            yaml.safe_load(return_data)
        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.exec_command('task {0} {1} {2}'.format(cmd, method,
                                                        cmd_line))

        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        expected_yaml = yaml.safe_load(return_data)
        self.assertEqual(written_yaml, expected_yaml)

        self.m_get_client.assert_called_once_with(client, mock.ANY)
        self.m_client.__getattr__(method).assert_called_once_with(
            **expected_kwargs)

    def test_task_deployment_info_download(self):
        self._test_cmd('deployment-info', 'download', '1',
                       'deployment-info',
                       utils.get_fake_yaml_deployment_info(),
                       dict(transaction_id=1))

    def test_task_cluster_settings_download(self):
        self._test_cmd('settings', 'download', '1',
                       'cluster-settings',
                       utils.get_fake_yaml_cluster_settings(),
                       dict(transaction_id=1))

    def test_task_network_configuration_download(self):
        self._test_cmd('network-configuration', 'download', '1',
                       'network-configuration',
                       utils.get_fake_yaml_network_conf(),
                       dict(transaction_id=1))
