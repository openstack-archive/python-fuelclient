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
from mock import call
from mock import Mock
from mock import patch

from fuelclient.tests.unit.v1 import base


class TestSnapshot(base.UnitTestCase):

    def setUp(self):
        super(TestSnapshot, self).setUp()

        self.mtask = Mock(status='ready', data={'message': ''})
        self.mtask.connection = Mock(root='')

    @patch('fuelclient.cli.actions.snapshot.SnapshotTask.get_default_config')
    @patch('sys.stdout')
    def test_get_default_config(self, mstdout, mconf):

        mconf.return_value = {'key': 'value'}

        self.execute(['fuel', 'snapshot', '--conf'])
        self.assertEqual(mstdout.write.call_args_list, [call('key: value\n')])

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

        mstart.return_value = self.mtask

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

        mstart.return_value = self.mtask

        self.execute(['fuel', 'snapshot'])

        mstart.assert_called_once_with({})
        mdownload.assert_called_once_with(
            mock.ANY,
            auth_token='token123',
            directory='.')

    @patch('fuelclient.cli.actions.snapshot.SnapshotTask.start_snapshot_task')
    @patch('sys.stdin')
    @patch('sys.stderr')
    def test_get_snapshot_when_task_is_failed(self, mstderr, mstdin, mstart):
        mstdin.isatty.return_value = True

        mdata = {'message': 'mock task message'}
        self.mtask.status = 'error'
        self.mtask.data = mdata

        mstart.return_value = self.mtask

        self.execute(['fuel', 'snapshot'])

        err_msg = ("Snapshot generating task ended with error. "
                   "Task message: {0}".format(mdata['message']))
        mstderr.write.called_once_with(err_msg)
