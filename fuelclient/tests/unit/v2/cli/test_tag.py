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
from fuelclient.tests.utils import fake_tag


class TestTagCommand(test_engine.BaseCLITest):
    """Tests for fuel2 tag * commands."""

    def test_tag_list(self):
        self.m_client.get_all.return_value = [
            {
                "id": 1,
                "tag": "fake_tag_1",
                "has_primary": True,
                "owner_id": 2,
                "owner_type": "release"
            },
            {
                "id": 2,
                "tag": "fake_tag_2",
                "has_primary": False,
                "owner_id": 3,
                "owner_type": "cluster"
            }
        ]
        args = 'tag list'
        self.exec_command(args)
        self.m_client.get_all.assert_called_once()
        self.m_get_client.assert_called_once_with('tag', mock.ANY)

    @mock.patch('json.dump')
    def test_tag_download_json(self, m_dump):
        tag_data = fake_tag.get_fake_tag()
        tag_id = tag_data['id']
        args = 'tag download -t {} -f json -d /tmp'.format(tag_id)
        expected_path = '/tmp/tag_{}.json'.format(tag_id)

        self.m_client.get_by_id.return_value = tag_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(tag_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(tag_id)

    @mock.patch('yaml.safe_dump')
    def test_tag_download_yaml(self, m_safe_dump):
        tag_data = fake_tag.get_fake_tag()
        tag_id = tag_data['id']
        args = 'tag download -t {} -f yaml -d /tmp'.format(tag_id)
        expected_path = '/tmp/tag_{}.yaml'.format(tag_id)

        self.m_client.get_by_id.return_value = tag_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(tag_data, mock.ANY,
                                            default_flow_style=False)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(tag_id)

    def test_tag_update_json(self):
        tag_data = fake_tag.get_fake_tag()
        tag_id = tag_data['id']
        args = 'tag update -t {} -f json -d /tmp'.format(tag_id)
        expected_path = '/tmp/tag_{}.json'.format(tag_id)

        m_open = mock.mock_open(read_data=json.dumps(tag_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.upload.assert_called_once_with(tag_data, tag_id)

    def test_tag_update_yaml(self):
        tag_data = fake_tag.get_fake_tag()
        tag_id = tag_data['id']
        args = 'tag update -t {} -f yaml -d /tmp'.format(tag_id)
        expected_path = '/tmp/tag_{}.yaml'.format(tag_id)

        m_open = mock.mock_open(read_data=yaml.safe_dump(tag_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.upload.assert_called_once_with(tag_data, tag_id)

    def test_tag_create_json(self):
        tag_data = fake_tag.get_fake_tag()
        tag_path = "/tmp/tag22.json"
        args = 'tag create -p {} -f json'.format(tag_path)
        expected_path = tag_path

        m_open = mock.mock_open(read_data=json.dumps(tag_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.create.assert_called_once_with(tag_data)

    def test_tag_create_yaml(self):
        tag_data = fake_tag.get_fake_tag()
        tag_path = "/tmp/tag22.yaml"
        args = 'tag create -p {} -f yaml'.format(tag_path)
        expected_path = tag_path

        m_open = mock.mock_open(read_data=yaml.safe_dump(tag_data))
        with mock.patch('fuelclient.commands.tag.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.create.assert_called_once_with(tag_data)

    def test_tag_delete(self):
        tag_id = 1
        args = 'tag delete {}'.format(tag_id)

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.delete_by_id.assert_called_once_with(tag_id)

    def test_tag_assign(self):
        node_id = 1
        tag_ids = ['4', '5', '6']
        args = 'tag assign -n {} -t {}'.format(node_id, " ".join(tag_ids))

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.assign.assert_called_once_with(node=node_id,
                                                     tag_ids=tag_ids)

    def test_tag_unassign(self):
        node_id = 1
        tag_ids = ['4', '5', '6']
        args = 'tag unassign -n {} -t {}'.format(node_id, " ".join(tag_ids))

        self.exec_command(args)
        self.m_get_client.assert_called_once_with('tag', mock.ANY)
        self.m_client.unassign.assert_called_once_with(node=node_id,
                                                       tag_ids=tag_ids)
