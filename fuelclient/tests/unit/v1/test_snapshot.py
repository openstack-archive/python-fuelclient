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
from mock import patch
import sys

from fuelclient.tests.unit.v1 import base


class TestSnapshot(base.UnitTestCase):

    @patch('fuelclient.cli.actions.snapshot.SnapshotTask.get_default_config')
    def test_get_default_config(self, mconf):

        mconf.return_value = {'key': 'value'}
        m_stdout = self.mock_open('')()
        with patch.object(sys, 'stdout', new=m_stdout):
            self.execute(['fuel', 'snapshot', '--conf'])
        self.assertEqual('key: value\n', m_stdout.getvalue())

    @patch('fuelclient.cli.actions.snapshot.APIClient',
           mock.Mock(auth_token='token123'))
    @patch('fuelclient.cli.actions.snapshot.SnapshotTask.start_snapshot_task')
    @patch('fuelclient.cli.actions.snapshot.'
           'download_snapshot_with_progress_bar')
    @patch('sys.stdin')
    def test_snapshot_with_provided_conf(self, mstdin, mdownload, mstart):
        conf = 'key: value\n'

        mstdin.isatty.return_value = False
        mstdin.read.return_value = conf

        self.execute(['fuel', 'snapshot'])

        mstart.assert_called_once_with({'key': 'value'})
        self.assertEqual(mstdin.read.call_count, 1)

        mdownload.assert_called_once_with(
            mock.ANY,
            auth_token='token123',
            directory='.')

    @patch('fuelclient.cli.actions.snapshot.APIClient',
           mock.Mock(auth_token='token123'))
    @patch('fuelclient.cli.actions.snapshot.SnapshotTask.start_snapshot_task')
    @patch('fuelclient.cli.actions.snapshot.'
           'download_snapshot_with_progress_bar')
    @patch('sys.stdin')
    def test_snapshot_without_conf(self, mstdin, mdownload, mstart):

        mstdin.isatty.return_value = True

        self.execute(['fuel', 'snapshot'])

        mstart.assert_called_once_with({})
        mdownload.assert_called_once_with(
            mock.ANY,
            auth_token='token123',
            directory='.')
