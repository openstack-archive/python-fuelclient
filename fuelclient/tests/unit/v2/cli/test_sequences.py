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


class TestSequenceActions(test_engine.BaseCLITest):
    def test_create(self):
        self.exec_command(
            'sequence create -r 1 -n test -t test_graph'
        )
        self.m_client.create.assert_called_once_with(
            1, 'test', ['test_graph']
        )

    def test_upload(self):
        m_open = mock.mock_open(read_data='name: test\ngraphs: [test]')
        module_path = 'fuelclient.cli.serializers.open'
        with mock.patch(module_path, m_open, create=True):
            self.exec_command(
                'sequence upload -r 1 --file sequence.yaml'
            )

        self.m_client.upload.assert_called_once_with(
            1, {'name': 'test', 'graphs': ['test']}
        )

    def test_update(self):
        self.exec_command(
            'sequence update 1 -n test -t test_graph'
        )
        self.m_client.update.assert_called_once_with(
            1, name='test', graph_types=['test_graph']
        )

    def test_show(self):
        self.exec_command('sequence show 1')
        self.m_client.get_by_id.assert_called_once_with(1)

    def test_list(self):
        self.exec_command('sequence list')
        self.m_client.get_all.assert_called_once_with()

    def test_delete(self):
        self.exec_command('sequence delete 1')
        self.m_client.delete_by_id.assert_called_once_with(1)

    def test_execute(self):
        self.exec_command(
            'sequence execute 1 -e 2 --dry-run --force'
        )
        self.m_client.execute.assert_called_once_with(
            sequence_id=1, env_id=2, dry_run=True, noop_run=False, force=True
        )
