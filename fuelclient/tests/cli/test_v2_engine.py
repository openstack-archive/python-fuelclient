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

import sys

import mock

import fuelclient
from fuelclient import main as main_mod
from fuelclient.tests import base


class BaseCLITest(base.UnitTestCase):
    """Base class for CLI-v2 tests."""

    def setUp(self):
        self._get_client_patcher = mock.patch.object(fuelclient, 'get_client')
        self.m_get_client = self._get_client_patcher.start()

        self.m_client = mock.MagicMock()
        self.m_get_client.return_value = self.m_client

    def tearDown(self):
        self._get_client_patcher.stop()

    def exec_v2_command(self, *args, **kwargs):
        """Executes fuelclient with the specified arguments."""

        return main_mod.main(argv=args)

    def exec_v2_command_interactive(self, commands):
        """Executes specified commands in one sesstion of interactive mode

        Starts Fuel Client's interactive console and passes
        supplied commands there.

        :param commands: The list of commands to execute in the
                         Fuel Client's console.
        :type commands:  list of str

        """
        with mock.patch.object(sys, 'stdin') as m_stdin:
            m_stdin.readline.side_effect = commands
            self.exec_v2_command()

    @mock.patch('cliff.commandmanager.CommandManager.find_command')
    def test_command_non_interactive(self, m_find_command):
        args = ['help']
        self.exec_v2_command(*args)
        m_find_command.assert_called_once_with(args)

    @mock.patch('cliff.commandmanager.CommandManager.find_command')
    def test_command_interactive(self, m_find_command):
        commands = ['quit']

        self.exec_v2_command_interactive(commands)
        m_find_command.assert_called_once_with(commands)
