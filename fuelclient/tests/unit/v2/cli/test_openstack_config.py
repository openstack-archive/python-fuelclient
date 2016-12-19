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
from fuelclient.tests import utils


class TestOpenstackConfig(test_engine.BaseCLITest):
    CLUSTER_ID = 42
    NODE_ID = 64

    def _test_config_list(self, cmd_line, expected_kwargs):
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()
        self.exec_command('openstack-config list {0}'.format(cmd_line))
        self.m_get_client.assert_called_once_with('openstack-config',
                                                  mock.ANY)
        self.m_client.get_filtered.assert_called_once_with(
            **expected_kwargs)

    def test_config_list_for_node(self):
        self._test_config_list(
            cmd_line='--env {0} --node {1}'.format(self.CLUSTER_ID,
                                                   self.NODE_ID),
            expected_kwargs={'cluster_id': self.CLUSTER_ID,
                             'node_ids': [self.NODE_ID], 'node_role': None,
                             'is_active': True}
        )

    def test_config_list_for_role(self):
        self._test_config_list(
            cmd_line='--env {0} --role compute'.format(self.CLUSTER_ID),
            expected_kwargs={'cluster_id': self.CLUSTER_ID, 'node_ids': None,
                             'node_role': 'compute', 'is_active': True}
        )

    def test_config_list_for_cluster(self):
        self._test_config_list(
            cmd_line='--env {0}'.format(self.CLUSTER_ID),
            expected_kwargs={'cluster_id': self.CLUSTER_ID, 'node_ids': None,
                             'node_role': None, 'is_active': True}
        )

    def test_config_list_sorted(self):
        self._test_config_list(
            cmd_line='--env {0} -s node_id'.format(self.CLUSTER_ID),
            expected_kwargs={'cluster_id': self.CLUSTER_ID, 'node_ids': None,
                             'node_role': None, 'is_active': True}
        )

    @mock.patch('sys.stderr')
    def test_config_list_for_cluster_fail(self, mocked_stderr):
        self.assertRaises(SystemExit,
                          self.exec_command, 'openstack-config list')
        self.assertIn('-e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_config_upload(self):
        self.m_client.upload.return_value = [utils.get_fake_openstack_config()
                                             for i in range(10)]

        cmd = 'openstack-config upload --env {0} --node {1} --file ' \
              'config.yaml'.format(self.CLUSTER_ID, self.NODE_ID)
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.upload.assert_called_once_with(
            path='config.yaml', cluster_id=self.CLUSTER_ID,
            node_ids=[self.NODE_ID], node_role=None)

    @mock.patch('sys.stderr')
    def test_config_upload_fail(self, mocked_stderr):
        cmd = 'openstack-config upload --env {0} ' \
              '--node {1}'.format(self.CLUSTER_ID, self.NODE_ID)
        self.assertRaises(SystemExit, self.exec_command, cmd)
        self.assertIn('--file',
                      mocked_stderr.write.call_args_list[-1][0][0])
        mocked_stderr.reset_mock()

        cmd = 'openstack-config upload  --node {1} ' \
              '--file config.yaml'.format(self.CLUSTER_ID, self.NODE_ID)
        self.assertRaises(SystemExit, self.exec_command, cmd)
        self.assertIn('-e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_config_download(self):
        self.m_client.download.return_value = 'config.yaml'

        cmd = 'openstack-config download 1 --file config.yaml'
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.download.assert_called_once_with(1, 'config.yaml')

    @mock.patch('sys.stderr')
    def test_config_download_fail(self, mocked_stderr):
        cmd = 'openstack-config download 1'
        self.assertRaises(SystemExit, self.exec_command, cmd)
        self.assertIn('--file',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_config_execute(self):
        cmd = 'openstack-config execute --env {0} --node {1}' \
              ''.format(self.CLUSTER_ID, self.NODE_ID)
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.execute.assert_called_once_with(
            cluster_id=self.CLUSTER_ID, node_ids=[self.NODE_ID],
            node_role=None, force=False)

    def test_config_force_execute(self):
        task_id = 42
        test_task = utils.get_fake_task(task_id=task_id)

        self.m_client.execute.return_value = test_task

        cmd = ('openstack-config execute --env {0}'
               ' --node {1} --force ').format(self.CLUSTER_ID, self.NODE_ID)

        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.execute.assert_called_once_with(
            cluster_id=self.CLUSTER_ID, node_ids=[self.NODE_ID],
            node_role=None, force=True)

    def test_config_delete(self):
        cmd = 'openstack-config delete 1'
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.delete.assert_called_once_with(1)
