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

import shlex
import sys

import mock
from oslotest import base as oslo_base

import fuelclient
from fuelclient.commands import environment as env
from fuelclient.commands import node as node
from fuelclient import main as main_mod
from fuelclient.tests import utils


class BaseCLITest(oslo_base.BaseTestCase):
    """Base class for testing the new CLI

    It mocks the whole API layer in order to be sure the
    tests test only the stuff which is responsible for
    the command line application. That allows to find bugs
    more precisely and not confuse them with the bugs in the
    API wrapper.

    """
    def setUp(self):
        super(BaseCLITest, self).setUp()

        self._get_client_patcher = mock.patch.object(fuelclient, 'get_client')
        self.m_get_client = self._get_client_patcher.start()

        self.m_client = mock.MagicMock()
        self.m_get_client.return_value = self.m_client
        self.addCleanup(self._get_client_patcher.stop)

    def exec_command(self, command=''):
        """Executes fuelclient with the specified arguments."""
        argv = shlex.split(command)
        if '--debug' not in argv:
            argv = ['--debug'] + argv

        return main_mod.main(argv=argv)

    def exec_command_interactive(self, commands):
        """Executes specified commands in one sesstion of interactive mode

        Starts Fuel Client's interactive console and passes
        supplied commands there.

        :param commands: The list of commands to execute in the
                         Fuel Client's console.
        :type commands:  list of str

        """
        with mock.patch.object(sys, 'stdin') as m_stdin:
            m_stdin.readline.side_effect = commands
            self.exec_command()

    @mock.patch('cliff.app.App.run_subcommand')
    def test_command_non_interactive(self, m_run_command):
        args = ['help']
        self.exec_command(*args)
        m_run_command.assert_called_once_with(args)

    @mock.patch('cliff.commandmanager.CommandManager.find_command')
    def test_command_interactive(self, m_find_command):
        commands = ['quit']

        self.exec_command_interactive(commands)
        m_find_command.assert_called_once_with(commands)

    @mock.patch('cliff.formatters.table.TableFormatter.emit_list')
    def test_lister_sorting(self, m_emit_list):
        cmd = 'env list -s status release_id'

        raw_data = [{'id': 43,
                     'status': 'STATUS 2',
                     'name': 'Test env 2',
                     'release_id': 2},

                    {'id': 42,
                     'status': 'STATUS 1',
                     'name': 'Test env 1',
                     'release_id': 2},

                    {'id': 44,
                     'status': 'STATUS 2',
                     'name': 'Test env 3',
                     'release_id': 1}]

        expected_order = [1, 2, 0]
        expected_data = [[raw_data[i][prop] for prop in env.EnvList.columns]
                         for i in expected_order]

        self.m_client.get_all.return_value = raw_data

        self.exec_command(cmd)
        m_emit_list.assert_called_once_with(mock.ANY,
                                            expected_data,
                                            mock.ANY,
                                            mock.ANY)

    @mock.patch('fuelclient.fuelclient_settings.'
                'FuelClientSettings.update_from_command_line_options')
    def test_settings_override_called(self, m_update):
        cmd = ('--os-password tpass --os-username tname --os-tenant-name tten '
               'node list')
        self.m_client.get_all.return_value = [utils.get_fake_node()
                                              for _ in range(10)]

        self.exec_command(cmd)

        m_update.assert_called_once_with(mock.ANY)
        passed_settings = m_update.call_args[0][0]

        self.assertEqual('tname', passed_settings.os_username)
        self.assertEqual('tpass', passed_settings.os_password)
        self.assertEqual('tten', passed_settings.os_tenant_name)

    def test_get_attribute_path(self):
        cmd = node.NodeShow(None, None)

        attr_types = ('attributes', 'interfaces', 'disks')
        file_format = 'json'
        node_id = 42
        directory = '/test'

        for attr_type in attr_types:
            expected_path = '/test/node_42/{t}.json'.format(t=attr_type)
            real_path = cmd.get_attributes_path(attr_type, file_format,
                                                node_id, directory)

        self.assertEqual(expected_path, real_path)

    def test_get_attribute_path_wrong_attr_type(self):
        cmd = node.NodeShow(None, None)

        attr_type = 'wrong'
        file_format = 'json'
        node_id = 42
        directory = '/test'

        self.assertRaises(ValueError,
                          cmd.get_attributes_path,
                          attr_type, file_format, node_id, directory)

    def test_get_attribute_path_wrong_file_format(self):
        cmd = node.NodeShow(None, None)

        attr_type = 'interfaces'
        file_format = 'wrong'
        node_id = 42
        directory = '/test'

        self.assertRaises(ValueError,
                          cmd.get_attributes_path,
                          attr_type, file_format, node_id, directory)
