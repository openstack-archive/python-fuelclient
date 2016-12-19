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
from fuelclient.tests.utils import fake_release


class TestReleaseCommand(test_engine.BaseCLITest):
    """Tests for fuel2 release * commands."""

    def setUp(self):
        super(TestReleaseCommand, self).setUp()
        self.m_client.get_by_id.return_value = fake_release.get_fake_release()
        self.m_client.get_attributes_metadata_by_id.return_value = \
            fake_release.get_fake_attributes_metadata()
        self.m_client.get_components_by_id.return_value = \
            fake_release.get_fake_release_components(10)

    def test_release_list(self):
        args = 'release list'
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with()
        self.m_get_client.assert_called_once_with('release', mock.ANY)

    def test_release_repos_list(self):
        args = 'release repos list 1'
        self.exec_command(args)
        self.m_client.get_attributes_metadata_by_id.assert_called_once_with(1)
        self.m_get_client.assert_called_once_with('release', mock.ANY)

    def test_release_repos_list_sorted(self):
        args = 'release repos list 1 -s name'
        self.exec_command(args)
        self.m_client.get_attributes_metadata_by_id.assert_called_once_with(1)
        self.m_get_client.assert_called_once_with('release', mock.ANY)

    @mock.patch('fuelclient.commands.release.utils.parse_yaml_file')
    def test_release_repos_update(self, mock_parse_yaml):
        args = 'release repos update 1 -f repos.yaml'
        new_repos = [
            {
                "name": "fake",
                "type": "deb",
                "uri": "some_uri",
                "priority": 1050,
                "section": "main",
                "suite": "trusty"
            }
        ]
        mock_parse_yaml.return_value = new_repos
        data = fake_release.get_fake_attributes_metadata()
        data["editable"]["repo_setup"]["repos"]["value"] = new_repos
        self.exec_command(args)
        mock_parse_yaml.assert_called_once_with('repos.yaml')
        self.m_client.get_attributes_metadata_by_id.assert_called_once_with(1)
        self.m_client.update_attributes_metadata_by_id \
            .assert_called_once_with(1, data)
        self.m_get_client.assert_called_once_with('release', mock.ANY)

    def test_release_component_list(self):
        release_id = 42
        args = 'release component list {0}'.format(release_id)
        self.exec_command(args)
        self.m_client.get_components_by_id.assert_called_once_with(release_id)
        self.m_get_client.assert_called_once_with('release', mock.ANY)

    def test_release_component_list_sorted(self):
        release_id = 42
        args = 'release component list {0} -s default'.format(release_id)
        self.exec_command(args)
        self.m_client.get_components_by_id.assert_called_once_with(release_id)
        self.m_get_client.assert_called_once_with('release', mock.ANY)
