# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

import json
import mock
import yaml

from fuelclient.cli import error
from fuelclient.tests.unit.v2.cli import test_engine


class TestSnapshotCommand(test_engine.BaseCLITest):

    @mock.patch('json.dump')
    def test_snapshot_config_download_json(self, m_dump):
        args = 'snapshot get-default-config -f json -d /tmp'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/snapshot_conf.json'

        self.m_client.get_default_config.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.snapshot.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('snapshot', mock.ANY)
        self.m_client.get_default_config.assert_called_once_with()

    @mock.patch('yaml.safe_dump')
    def test_snapshot_config_download_yaml(self, m_safe_dump):
        args = 'snapshot get-default-config -f yaml -d /tmp'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/snapshot_conf.yaml'

        self.m_client.get_default_config.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.snapshot.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('snapshot', mock.ANY)
        self.m_client.get_default_config.assert_called_once_with()

    def test_snapshot_create(self):
        args = 'snapshot create'
        test_data = {}
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('snapshot', mock.ANY)
        self.m_client.create_snapshot.assert_called_once_with(test_data)

    @mock.patch('fuelclient.utils.file_exists', mock.Mock(return_value=True))
    def test_snapshot_create_w_config_json(self):
        args = 'snapshot create -c /tmp/snapshot_conf.json'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/snapshot_conf.json'

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.snapshot.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('snapshot', mock.ANY)
        self.m_client.create_snapshot.assert_called_once_with(test_data)

    @mock.patch('fuelclient.utils.file_exists', mock.Mock(return_value=True))
    def test_snapshot_create_w_config_yaml(self):
        args = 'snapshot create -c /tmp/snapshot_conf.yaml'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/snapshot_conf.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(test_data))
        with mock.patch('fuelclient.commands.snapshot.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('snapshot', mock.ANY)
        self.m_client.create_snapshot.assert_called_once_with(test_data)

    def test_snapshot_get_link(self):
        task_id = 45
        args = 'snapshot get-link {}'.format(task_id)
        test_data = {'id': task_id,
                     'name': 'dump',
                     'status': 'ready',
                     'message': 'fake_message'}

        self.m_client.get_by_id.return_value = test_data

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('snapshot', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(task_id)

    @mock.patch('sys.stderr')
    def test_snapshot_get_link_fail(self, mocked_stderr):
        task_id = 45
        args = 'snapshot get-link {}'.format(task_id)
        test_data = {'id': task_id,
                     'name': 'not_dump_name',
                     'status': 'ready',
                     'message': 'fake_message'}

        self.m_client.get_by_id.return_value = test_data

        self.assertRaises(error.ActionException, self.exec_command, args)
        self.assertIn('Task with id {} is not a snapshot generation '
                      'task'.format(task_id),
                      mocked_stderr.write.call_args_list[0][0][0])
