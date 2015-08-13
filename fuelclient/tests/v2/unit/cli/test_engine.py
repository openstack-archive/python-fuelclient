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

import fuelclient
from fuelclient.cli import error
from fuelclient.commands import environment as env
from fuelclient import main as main_mod
from fuelclient.tests import base


class BaseCLITest(base.UnitTestCase):
    """Base class for testing the new CLI

    It mocks the whole API layer in order to be sure the
    tests test only the stuff which is responsible for
    the command line application. That allows to find bugs
    more precisely and not confuse them with the bugs in the
    API wrapper.

    """
    def setUp(self):
        self._get_client_patcher = mock.patch.object(fuelclient, 'get_client')
        self.m_get_client = self._get_client_patcher.start()

        self.m_client = mock.MagicMock()
        self.m_get_client.return_value = self.m_client

    def tearDown(self):
        self._get_client_patcher.stop()

    def exec_command(self, command=''):
        """Executes fuelclient with the specified arguments."""

        return main_mod.main(argv=shlex.split(command))

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

    @mock.patch.object(sys, 'stderr')
    @mock.patch('cliff.app.App.run_subcommand')
    def test_exec_command_error_handle(self, m_run, m_stderr):
        error_msg = 'Test error'
        expected_output = error_msg + '\n'

        m_run.side_effect = error.FuelClientException(error_msg)

        self.assertRaises(SystemExit,
                          self.exec_command,
                          'some command --fail True')
        m_stderr.write.assert_called_once_with(expected_output)

    @mock.patch('cliff.commandmanager.CommandManager.find_command')
    def test_command_interactive(self, m_find_command):
        commands = ['quit']

        self.exec_command_interactive(commands)
        m_find_command.assert_called_once_with(commands)

    @mock.patch('cliff.formatters.table.TableFormatter.emit_list')
    def test_lister_sorting(self, m_emit_list):
        cmd = 'env list -s status net_provider'

        raw_data = [{'id': 43,
                     'status': 'STATUS 2',
                     'name': 'Test env 2',
                     'mode': 'ha_compact',
                     'release_id': 2,
                     'net_provider': 'nova'},

                    {'id': 42,
                     'status': 'STATUS 1',
                     'name': 'Test env 1',
                     'mode': 'ha_compact',
                     'release_id': 2,
                     'net_provider': 'nova'},

                    {'id': 44,
                     'status': 'STATUS 2',
                     'name': 'Test env 3',
                     'mode': 'ha_compact',
                     'release_id': 2,
                     'net_provider': 'neutron'}]

        expected_order = [1, 2, 0]
        expected_data = [[raw_data[i][prop] for prop in env.EnvList.columns]
                         for i in expected_order]

        self.m_client.get_all.return_value = raw_data

        self.exec_command(cmd)
        m_emit_list.assert_called_once_with(mock.ANY,
                                            expected_data,
                                            mock.ANY,
                                            mock.ANY)
