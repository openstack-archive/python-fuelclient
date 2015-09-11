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

from mock import mock_open
from mock import patch

from fuelclient.tests.unit.v1 import base


YAML_SETTINGS_DATA = """editable:
  access:
    user:
      value: test_user
"""
JSON_SETTINGS_DATA = {
    'editable': {
        'access': {
            'user': {
                'value': 'test_user'
            }
        }
    }
}


class BaseSettings(base.UnitTestCase):

    def check_upload_action(self, test_command, test_url):
        m = mock_open(read_data=YAML_SETTINGS_DATA)
        put = self.m_request.put(test_url, json={})

        with patch('six.moves.builtins.open', m, create=True):
            self.execute(test_command)

        m().read.assert_called_once_with()
        self.assertTrue(put.called)
        self.assertDictEqual(put.last_request.json(), JSON_SETTINGS_DATA)

    def check_diff_action(self, test_command, test_url, read_mock):
        m = mock_open()
        self.m_request.get(test_url, json=JSON_SETTINGS_DATA)

        with patch('six.moves.builtins.open', m, create=True):
            with patch('fuelclient.cli.actions.settings.'
                       'DictDiffer') as mdictdiffer:
                read_data = {"key": "value"}
                read_mock.return_value = read_data
                self.execute(test_command)

        mdictdiffer.diff.assert_called_once_with(JSON_SETTINGS_DATA, read_data)

    def check_default_action(self, test_command, test_url):
        m = mock_open()
        get = self.m_request.get(test_url, json=JSON_SETTINGS_DATA)

        with patch('six.moves.builtins.open', m, create=True):
            self.execute(test_command)

        self.assertTrue(get.called)
        m().write.assert_called_once_with(YAML_SETTINGS_DATA)

    def check_download_action(self, test_command, test_url):
        m = mock_open()
        get = self.m_request.get(test_url, json=JSON_SETTINGS_DATA)

        with patch('six.moves.builtins.open', m, create=True):
            self.execute(test_command)

        m().write.assert_called_once_with(YAML_SETTINGS_DATA)
        self.assertTrue(get.called)


class TestSettings(BaseSettings):

    def test_upload_action(self):
        self.check_upload_action(
            test_command=[
                'fuel', 'settings', '--env', '1', '--upload'],
            test_url='/api/v1/clusters/1/attributes')

    def test_default_action(self):
        self.check_default_action(
            test_command=[
                'fuel', 'settings', '--env', '1', '--default'],
            test_url='/api/v1/clusters/1/attributes/defaults')

    def test_download_action(self):
        self.check_download_action(
            test_command=[
                'fuel', 'settings', '--env', '1', '--download'],
            test_url='/api/v1/clusters/1/attributes')

    @patch('fuelclient.cli.actions.settings.Environment.read_settings_data')
    def test_diff_action(self, mread):
        self.check_diff_action(
            test_command=[
                'fuel', 'settings', '--env', '1', '--diff'],
            test_url='/api/v1/clusters/1/attributes',
            read_mock=mread)


class TestVmwareSettings(BaseSettings):

    def test_upload_action(self):
        self.check_upload_action(
            test_command=[
                'fuel', 'vmware-settings', '--env', '1', '--upload'],
            test_url='/api/v1/clusters/1/vmware_attributes')

    def test_default_action(self):
        self.check_default_action(
            test_command=[
                'fuel', 'vmware-settings', '--env', '1', '--default'],
            test_url='/api/v1/clusters/1/vmware_attributes/defaults')

    def test_download_action(self):
        self.check_download_action(
            test_command=[
                'fuel', 'vmware-settings', '--env', '1', '--download'],
            test_url='/api/v1/clusters/1/vmware_attributes')

    @patch('fuelclient.cli.actions.settings.Environment.'
           'read_vmware_settings_data')
    def test_diff_action(self, mread):
        self.check_diff_action(
            test_command=[
                'fuel', 'vmware-settings', '--env', '1', '--diff'],
            test_url='/api/v1/clusters/1/vmware_attributes',
            read_mock=mread)
