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

import json
import mock
import yaml

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_tag


class TestTagCommand(test_engine.BaseCLITest):
    """Tests for fuel2 tag * commands."""

    def test_tag_list_for_release(self):
        self.m_client.get_all.return_value = [
            {"tag": "fake_tag_1",
             "has_primary": True,
             "owner_id": 1,
             "owner_type": 'release',
             },
            {"tag": "fake_tag_2",
             "has_primary": True,
             "owner_id": 1,
             "owner_type": 'release',
             },
        ]
        release_id = 45
        args = 'tag list -r {id}'.format(id=release_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with('releases', release_id)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)

    def test_tag_list_for_cluster(self):
        self.m_client.get_all.return_value = [
            {"tag": "fake_tag_1",
             "has_primary": True,
             "owner_id": 1,
             "owner_type": 'release',
             },
            {"tag": "fake_tag_2",
             "has_primary": True,
             "owner_id": 1,
             "owner_type": 'release',
             },
        ]
        env_id = 45
        args = 'tag list -e {id}'.format(id=env_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with('clusters', env_id)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)

    def test_tag_list_sorted(self):
        self.m_client.get_all.return_value = [
            {"tag": "fake_tag_2",
             "group": "group_1",
             "has_primary": True,
             "owner_id": 1,
             "owner_type": 'release',
             },
            {"tag": "fake_tag_1",
             "group": "group_2",
             "has_primary": True,
             "owner_id": 1,
             "owner_type": 'release',
             }
        ]
        env_id = 45
        args = 'tag list -e {id} -s group'.format(id=env_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with('clusters', env_id)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)

    @mock.patch('sys.stderr')
    def test_tag_list_fail(self, mocked_stderr):
        args = 'tag list'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-r/--release -e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])

    @mock.patch('sys.stderr')
    def test_tag_list_with_mutually_exclusive_params(self, mocked_stderr):
        args = 'tag list -e 1 -r 2'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('not allowed',
                      mocked_stderr.write.call_args_list[-1][0][0])

    @mock.patch('json.dump')
    def test_release_tag_download_json(self, m_dump):
        release_id = 45
        tag_name = 'fake_tag'
        test_data = fake_tag.get_fake_tag(fake_tag)
        args = 'tag download -r {} -n {} -f json -d /tmp'.format(release_id,
                                                                 tag_name)
        expected_path = '/tmp/releases_{id}/{name}.json'.format(id=release_id,
                                                                name=tag_name)

        self.m_client.get_tag.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.get_tag.assert_called_once_with('releases',
                                                      release_id,
                                                      tag_name)

    @mock.patch('json.dump')
    def test_cluster_tag_download_json(self, m_dump):
        env_id = 45
        tag_name = 'fake_tag'
        test_data = fake_tag.get_fake_tag(fake_tag)
        args = 'tag download -e {} -n {} -f json -d /tmp'.format(env_id,
                                                                 tag_name)
        expected_path = '/tmp/clusters_{id}/{name}.json'.format(id=env_id,
                                                                name=tag_name)

        self.m_client.get_tag.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.get_tag.assert_called_once_with('clusters',
                                                      env_id,
                                                      tag_name)

    @mock.patch('yaml.safe_dump')
    def test_release_tag_download_yaml(self, m_safe_dump):
        release_id = 45
        tag_name = 'fake_tag'
        test_data = fake_tag.get_fake_tag(fake_tag)
        args = 'tag download -r {} -n {} -f yaml -d /tmp'.format(release_id,
                                                                 tag_name)
        expected_path = '/tmp/releases_{id}/{name}.yaml'.format(id=release_id,
                                                                name=tag_name)

        self.m_client.get_tag.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.get_tag.assert_called_once_with('releases',
                                                      release_id,
                                                      tag_name)

    @mock.patch('yaml.safe_dump')
    def test_cluster_tag_download_yaml(self, m_safe_dump):
        env_id = 45
        tag_name = 'fake_tag'
        test_data = fake_tag.get_fake_tag(fake_tag)
        args = 'tag download -e {} -n {} -f yaml -d /tmp'.format(env_id,
                                                                 tag_name)
        expected_path = '/tmp/clusters_{id}/{name}.yaml'.format(id=env_id,
                                                                name=tag_name)

        self.m_client.get_tag.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.get_tag.assert_called_once_with('clusters',
                                                      env_id,
                                                      tag_name)

    def test_release_tag_update_json(self):
        release_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "tag_name": tag_name}
        args = 'tag update -r {} -n {} -f json -d /tmp'.format(release_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/releases_{}/fake_tag.json'.format(release_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_cluster_tag_update_json(self):
        env_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "tag_name": tag_name}
        args = 'tag update -e {} -n {} -f json -d /tmp'.format(env_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/clusters_{}/fake_tag.json'.format(env_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_release_tag_update_yaml(self):
        release_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "tag_name": tag_name}
        args = 'tag update -r {} -n {} -f yaml -d /tmp'.format(release_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/releases_{}/fake_tag.yaml'.format(release_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_cluster_tag_update_yaml(self):
        env_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "tag_name": tag_name}
        args = 'tag update -e {} -n {} -f yaml -d /tmp'.format(env_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/clusters_{}/fake_tag.yaml'.format(env_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.update.assert_called_once_with(test_data, **params)

    def test_release_tag_create_json(self):
        release_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "tag_name": tag_name}
        args = 'tag create -r {} -n {} -f json -d /tmp'.format(release_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/releases_{}/fake_tag.json'.format(release_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_cluster_tag_create_json(self):
        env_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "tag_name": tag_name}
        args = 'tag create -e {} -n {} -f json -d /tmp'.format(env_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/clusters_{}/fake_tag.json'.format(env_id)

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_release_tag_create_yaml(self):
        release_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "releases",
                  "owner_id": release_id,
                  "tag_name": tag_name}
        args = 'tag create -r {} -n {} -f yaml -d /tmp'.format(release_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/releases_{}/fake_tag.yaml'.format(release_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_cluster_tag_create_yaml(self):
        env_id = 45
        tag_name = 'fake_tag'
        params = {"owner_type": "clusters",
                  "owner_id": env_id,
                  "tag_name": tag_name}
        args = 'tag create -e {} -n {} -f yaml -d /tmp'.format(env_id,
                                                               tag_name)
        test_data = fake_tag.get_fake_tag(tag_name)
        expected_path = '/tmp/clusters_{}/fake_tag.yaml'.format(env_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(test_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.create.assert_called_once_with(test_data, **params)

    def test_release_tag_delete(self):
        release_id = 45
        tag_name = 'fake_tag'
        args = 'tag delete -r {} -n {}'.format(release_id, tag_name)

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.delete.assert_called_once_with('releases',
                                                     release_id,
                                                     tag_name)

    def test_cluster_tag_delete(self):
        env_id = 45
        tag_name = 'fake_tag'
        args = 'tag delete -e {} -n {}'.format(env_id, tag_name)

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.delete.assert_called_once_with('clusters',
                                                     env_id,
                                                     tag_name)
