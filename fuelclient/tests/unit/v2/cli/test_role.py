# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

import json
import mock
import yaml

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_role


class TestRoleCommand(test_engine.BaseCLITest):
    """Tests for fuel2 role * commands."""

    def test_role_list_for_release(self):
        self.m_client.get_all.return_value = [
            {"name": "fake_role_1",
             "group": "fake_group",
             "conflicts": ["fake_role_2", "fake_role_3"],
             "description": "some fake description"},
            {"name": "fake_role_2",
             "group": "fake_group",
             "conflicts": ["fake_role_1", "fake_role_3"],
             "description": "some fake description"}
        ]
        release_id = 45
        args = 'role list -r {id}'.format(id=release_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with('releases', release_id)
        self.m_get_client.assert_called_once_with('role', mock.ANY)

    def test_role_list_for_cluster(self):
        self.m_client.get_all.return_value = [
            {"name": "fake_role_1",
             "group": "fake_group",
             "conflicts": ["fake_role_2", "fake_role_3"],
             "description": "some fake description"},
            {"name": "fake_role_2",
             "group": "fake_group",
             "conflicts": ["fake_role_1", "fake_role_3"],
             "description": "some fake description"}
        ]
        env_id = 45
        args = 'role list -e {id}'.format(id=env_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with('clusters', env_id)
        self.m_get_client.assert_called_once_with('role', mock.ANY)

    def test_role_list_sorted(self):
        self.m_client.get_all.return_value = [
            {"name": "fake_role_2",
             "group": "fake_group_1",
             "conflicts": ["fake_role_1", "fake_role_3"],
             "description": "some fake description"},
            {"name": "fake_role_1",
             "group": "fake_group_2",
             "conflicts": ["fake_role_2", "fake_role_3"],
             "description": "some fake description"},
        ]
        env_id = 45
        args = 'role list -e {id} -s group'.format(id=env_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with('clusters', env_id)
        self.m_get_client.assert_called_once_with('role', mock.ANY)

    @mock.patch('sys.stderr')
    def test_role_list_fail(self, mocked_stderr):
        args = 'role list'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-r/--release -e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])

    @mock.patch('sys.stderr')
    def test_role_list_with_mutually_exclusive_params(self, mocked_stderr):
        args = 'role list -e 1 -r 2'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('not allowed',
                      mocked_stderr.write.call_args_list[-1][0][0])

    @mock.patch('json.dump')
    def test_release_role_download_json(self, m_dump):
        release_id = 45
        role_name = 'fake_role'
        test_data = fake_role.get_fake_role(fake_role)
        args = 'role download -r {} -n {} -f json -d /tmp'.format(release_id,
                                                                  role_name)
        expected_path = '/tmp/releases_{id}/{name}.json'.format(id=release_id,
                                                                name=role_name)

        self.m_client.get_one.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.get_one.assert_called_once_with('releases',
                                                      release_id,
                                                      role_name)

    @mock.patch('json.dump')
    def test_cluster_role_download_json(self, m_dump):
        env_id = 45
        role_name = 'fake_role'
        test_data = fake_role.get_fake_role(fake_role)
        args = 'role download -e {} -n {} -f json -d /tmp'.format(env_id,
                                                                  role_name)
        expected_path = '/tmp/clusters_{id}/{name}.json'.format(id=env_id,
                                                                name=role_name)

        self.m_client.get_one.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.get_one.assert_called_once_with('clusters',
                                                      env_id,
                                                      role_name)

    @mock.patch('yaml.safe_dump')
    def test_release_role_download_yaml(self, m_safe_dump):
        release_id = 45
        role_name = 'fake_role'
        test_data = fake_role.get_fake_role(fake_role)
        args = 'role download -r {} -n {} -f yaml -d /tmp'.format(release_id,
                                                                  role_name)
        expected_path = '/tmp/releases_{id}/{name}.yaml'.format(id=release_id,
                                                                name=role_name)

        self.m_client.get_one.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.get_one.assert_called_once_with('releases',
                                                      release_id,
                                                      role_name)

    @mock.patch('yaml.safe_dump')
    def test_cluster_role_download_yaml(self, m_safe_dump):
        env_id = 45
        role_name = 'fake_role'
        test_data = fake_role.get_fake_role(fake_role)
        args = 'role download -e {} -n {} -f yaml -d /tmp'.format(env_id,
                                                                  role_name)
        expected_path = '/tmp/clusters_{id}/{name}.yaml'.format(id=env_id,
                                                                name=role_name)

        self.m_client.get_one.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.get_one.assert_called_once_with('clusters',
                                                      env_id,
                                                      role_name)

    def test_release_role_update_json(self):
        release_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "role_name": role_name}
        args = 'role update -r {} -n {} -f json -d /tmp'.format(release_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/releases_{}/fake_role.json'.format(release_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_cluster_role_update_json(self):
        env_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "role_name": role_name}
        args = 'role update -e {} -n {} -f json -d /tmp'.format(env_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/clusters_{}/fake_role.json'.format(env_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_release_role_update_yaml(self):
        release_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "role_name": role_name}
        args = 'role update -r {} -n {} -f yaml -d /tmp'.format(release_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/releases_{}/fake_role.yaml'.format(release_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_cluster_role_update_yaml(self):
        env_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "role_name": role_name}
        args = 'role update -e {} -n {} -f yaml -d /tmp'.format(env_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/clusters_{}/fake_role.yaml'.format(env_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_release_role_create_json(self):
        release_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "role_name": role_name}
        args = 'role create -r {} -n {} -f json -d /tmp'.format(release_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/releases_{}/fake_role.json'.format(release_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_cluster_role_create_json(self):
        env_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "role_name": role_name}
        args = 'role create -e {} -n {} -f json -d /tmp'.format(env_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/clusters_{}/fake_role.json'.format(env_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_release_role_create_yaml(self):
        release_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "role_name": role_name}
        args = 'role create -r {} -n {} -f yaml -d /tmp'.format(release_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/releases_{}/fake_role.yaml'.format(release_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_cluster_role_create_yaml(self):
        env_id = 45
        role_name = 'fake_role'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "role_name": role_name}
        args = 'role create -e {} -n {} -f yaml -d /tmp'.format(env_id,
                                                                role_name)
        test_data = fake_role.get_fake_role(role_name)
        expected_path = '/tmp/clusters_{}/fake_role.yaml'.format(env_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.role.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_release_role_delete(self):
        release_id = 45
        role_name = 'fake_role'
        args = 'role delete -r {} -n {}'.format(release_id, role_name)

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.delete.assert_called_once_with('releases',
                                                     release_id,
                                                     role_name)

    def test_cluster_role_delete(self):
        env_id = 45
        role_name = 'fake_role'
        args = 'role delete -e {} -n {}'.format(env_id, role_name)

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('role', mock.ANY)
        self.m_client.delete.assert_called_once_with('clusters',
                                                     env_id,
                                                     role_name)
