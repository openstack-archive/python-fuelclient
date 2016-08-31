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

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests import utils


class TestExtensionCommand(test_engine.BaseCLITest):
    """Tests for fuel2 extension * commands."""

    def test_extensions_list(self):
        self.m_client.get_all.return_value = utils.get_fake_extensions(2)
        args = 'extension list'
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with()
        self.m_get_client.assert_called_once_with('extension', mock.ANY)

    def test_env_extensions_show(self):
        self.m_client.get_extensions.return_value = \
            utils.get_fake_env_extensions()
        env_id = 45
        args = 'env extension show {id}'.format(id=env_id)
        self.exec_command(args)
        self.m_client.get_by_id.assert_called_once_with(env_id)
        self.m_get_client.assert_called_once_with('extension', mock.ANY)

    @mock.patch('sys.stderr')
    def test_env_extension_show_fail(self, mocked_stderr):
        args = 'env extension show'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('id',
                      mocked_stderr.write.call_args_list[0][0][0])

    @mock.patch('sys.stderr')
    def test_env_extension_enable_fail(self, mocked_stderr):
        args = 'env extension enable 1'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-E/--extensions',
                      mocked_stderr.write.call_args_list[-1][0][0])

    @mock.patch('sys.stderr')
    def test_env_extension_disable_fail(self, mocked_stderr):
        args = 'env extension disable 1'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-E/--extensions',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_env_extensions_enable(self):
        exts = utils.get_fake_env_extensions()
        env_id = 45
        args = 'env extension enable {id} --extensions {exts}'.format(
            id=env_id, exts=' '.join(exts))
        self.exec_command(args)
        self.m_client.enable_extensions.assert_called_once_with(env_id, exts)
        self.m_get_client.assert_called_once_with('extension', mock.ANY)

    def test_env_extensions_disable(self):
        exts = utils.get_fake_env_extensions()
        env_id = 45
        args = 'env extension disable {id} --extensions {exts}'.format(
            id=env_id, exts=' '.join(exts))
        self.exec_command(args)
        self.m_client.disable_extensions.assert_called_once_with(env_id, exts)
        self.m_get_client.assert_called_once_with('extension', mock.ANY)
