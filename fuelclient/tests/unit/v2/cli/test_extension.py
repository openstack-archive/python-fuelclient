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


class TestExtensionCommand(test_engine.BaseCLITest):
    """Tests for fuel2 extension * commands."""

    def test_extensions_list(self):
        self.m_client.get_all.return_value = [
            {'name': 'fake_name_1',
             'version': '1.0.1',
             'provides': ['fake_method_call_1'],
             'description': 'fake_description_1'},
            {'name': 'fake_name_2',
             'version': '1.2.3',
             'provides': ['fake_method_call_2'],
             'description': 'fake_description_2'},
        ]
        args = 'extension list'
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with()
        self.m_get_client.assert_called_once_with('extension', mock.ANY)

    def test_env_extensions_list(self):
        self.m_client.get_extensions.return_value = [
            'fake_ext1', 'fake_ext2', 'fake_ext3']
        env_id = 45
        args = 'env extension list -e {id}'.format(id=env_id)
        self.exec_command(args)
        self.m_client.get_extensions.assert_called_once_with(env_id)
        self.m_get_client.assert_called_once_with('extension', mock.ANY)

    def test_env_extensions_enable(self):
        exts = ['fake_ext1', 'fake_ext1']
        env_id = 45
        args = 'env extension enable -e {id} --extensions {exts}'.format(
            id=env_id, exts=' '.join(exts))
        self.exec_command(args)
        self.m_client.enable_extensions.assert_called_once_with(env_id, exts)
        self.m_get_client.assert_called_once_with('extension', mock.ANY)

    def test_env_extensions_disable(self):
        exts = ['fake_ext1', 'fake_ext2']
        env_id = 45
        args = 'env extension disable -e {id} --extensions {exts}'.format(
            id=env_id, exts=' '.join(exts))
        self.exec_command(args)
        self.m_client.disable_extensions.assert_called_once_with(env_id, exts)
        self.m_get_client.assert_called_once_with('extension', mock.ANY)
