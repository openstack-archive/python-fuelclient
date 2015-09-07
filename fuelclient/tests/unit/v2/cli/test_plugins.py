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

from fuelclient.tests.unit.v2.cli import test_engine


class TestPluginsCommand(test_engine.BaseCLITest):
    """Tests for fuel2 node * commands."""

    def setUp(self):
        super(TestPluginsCommand, self).setUp()

    def test_plugins_sync_all(self):
        args = 'plugins sync'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('plugins', mock.ANY)
        self.m_client.sync.assert_called_once_with(ids=None)

    def test_plugins_sync_specified_plugins(self):
        ids = [1, 2]
        args = 'plugins sync {ids}'.format(ids=' '.join(map(str, ids)))
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('plugins', mock.ANY)
        self.m_client.sync.assert_called_once_with(ids=ids)
