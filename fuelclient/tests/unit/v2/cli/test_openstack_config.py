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


class TestOpenstackConfig(test_engine.BaseCLITest):

    def _test_config_list(self, cmd_line, expected_kwargs):
        self.m_get_client.reset_mock()
        self.m_client.get_filtered.reset_mock()

        self.exec_command('openstack-config list {0}'.format(cmd_line))

        self.m_get_client.assert_called_once_with(
            'openstack-config', mock.ANY)
        self.m_client.get_filtered.assert_called_once_with(
            **expected_kwargs)

    def test_config_list_for_node(self):
        self._test_config_list(
            cmd_line='--env 42 --node 64',
            expected_kwargs={'cluster_id': 42, 'node_id': 64,
                             'node_role': None, 'is_active': True}
        )

    def test_config_list_for_role(self):
        self._test_config_list(
            cmd_line='--env 42 --role compute',
            expected_kwargs={'cluster_id': 42, 'node_id': None,
                             'node_role': 'compute', 'is_active': True}
        )

    def test_config_list_for_cluster(self):
        self._test_config_list(
            cmd_line='--env 42',
            expected_kwargs={'cluster_id': 42, 'node_id': None,
                             'node_role': None, 'is_active': True}
        )

    def test_config_upload(self):
        self.m_client.upload.return_value = 'config.yaml'

        cmd = 'openstack-config upload --env 42 --node 64 --file config.yaml'
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.upload.assert_called_once_with(
            path='config.yaml', cluster_id=42, node_id=64, node_role=None)

    def test_config_download(self):
        self.m_client.download.return_value = 'config.yaml'

        cmd = 'openstack-config download 1 --file config.yaml'
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.download.assert_called_once_with(1, 'config.yaml')

    def test_config_execute(self):
        cmd = 'openstack-config execute --env 42 --node 64'
        self.exec_command(cmd)

        self.m_get_client.assert_called_once_with('openstack-config', mock.ANY)
        self.m_client.execute.assert_called_once_with(
            cluster_id=42, node_id=64, node_role=None)
