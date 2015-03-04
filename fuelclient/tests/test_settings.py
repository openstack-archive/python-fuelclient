# -*- coding: utf-8 -*-
#
#    Copyright 2014 Mirantis, Inc.
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

import ast
import yaml

from mock import Mock
from mock import mock_open
from mock import patch

from fuelclient.tests import base


@patch('fuelclient.client.requests')
class TestSettings(base.UnitTestCase):

    def setUp(self):
        super(TestSettings, self).setUp()
        self.yaml_settings_data = """
            editable:
              access:
                user:
                  value: test_user
        """
        self.settings_data = {
            'editable': {
                'access': {
                    'user': {
                        'value': 'test_user'
                    }
                }
            }
        }

    def test_upload_action(self, mrequests):
        m = mock_open(read_data=self.yaml_settings_data)
        with patch('__builtin__.open', m, create=True):
            self.execute_wo_auth(
                ['fuel', 'settings', '--env', '1', '--upload'])

        request = mrequests.put.call_args_list[0]
        url = request[0][0]
        data = request[1]['data']

        m().read.assert_called_once_with()
        self.assertEqual(mrequests.put.call_count, 1)
        self.assertIn('/api/v1/clusters/1/attributes', url)
        self.assertDictEqual(ast.literal_eval(data), self.settings_data)

    def test_default_action(self, mrequests):
        m = mock_open()
        mresponse = Mock(status_code=200)
        mresponse.json.return_value = self.settings_data
        mrequests.get.return_value = mresponse

        with patch('__builtin__.open', m, create=True):
            self.execute_wo_auth(
                ['fuel', 'settings', '--env', '1', '--default'])

        request = mrequests.get.call_args_list[0]
        url = request[0][0]

        m().write.assert_called_once_with(
            yaml.safe_dump(self.settings_data, default_flow_style=False))
        self.assertEqual(mrequests.get.call_count, 1)
        self.assertIn('/api/v1/clusters/1/attributes/default', url)

    def test_download_action(self, mrequests):
        m = mock_open()
        mresponse = Mock(status_code=200)
        mresponse.json.return_value = self.settings_data
        mrequests.get.return_value = mresponse

        with patch('__builtin__.open', m, create=True):
            self.execute_wo_auth(
                ['fuel', 'settings', '--env', '1', '--download'])

        request = mrequests.get.call_args_list[0]
        url = request[0][0]

        m().write.assert_called_once_with(
            yaml.safe_dump(self.settings_data, default_flow_style=False))
        self.assertEqual(mrequests.get.call_count, 1)
        self.assertIn('/api/v1/clusters/1/attributes', url)


@patch('fuelclient.client.requests')
class TestVmwareSettings(base.UnitTestCase):
    def setUp(self):
        super(TestVmwareSettings, self).setUp()
        self.yaml_settings_data = """
            editable:
              metadata:
                field:
                  name: user
              value:
                user: test_user
        """
        self.settings_data = {
            'editable': {
                'metadata': {
                    'field': {
                        'name': 'user'
                    }
                },
                'value': {
                    'user': 'test_user'
                }
            }
        }

    def test_upload_action(self, mrequests):
        m = mock_open(read_data=self.yaml_settings_data)
        with patch('__builtin__.open', m, create=True):
            self.execute_wo_auth(
                ['fuel', 'vmware-settings', '--env', '1', '--upload'])

        request = mrequests.put.call_args_list[0]
        url = request[0][0]
        data = request[1]['data']

        m().read.assert_called_once_with()
        self.assertEqual(mrequests.put.call_count, 1)
        self.assertIn('/api/v1/clusters/1/vmware_attributes', url)
        self.assertDictEqual(ast.literal_eval(data), self.settings_data)

    def test_default_action(self, mrequests):
        m = mock_open()
        mresponse = Mock(status_code=200)
        mresponse.json.return_value = self.settings_data
        mrequests.get.return_value = mresponse

        with patch('__builtin__.open', m, create=True):
            self.execute_wo_auth(
                ['fuel', 'vmware-settings', '--env', '1', '--default'])

        request = mrequests.get.call_args_list[0]
        url = request[0][0]

        m().write.assert_called_once_with(
            yaml.safe_dump(self.settings_data, default_flow_style=False))
        self.assertEqual(mrequests.get.call_count, 1)
        self.assertIn('/api/v1/clusters/1/vmware_attributes/default', url)

    def test_download_action(self, mrequests):
        m = mock_open()
        mresponse = Mock(status_code=200)
        mresponse.json.return_value = self.settings_data
        mrequests.get.return_value = mresponse

        with patch('__builtin__.open', m, create=True):
            self.execute_wo_auth(
                ['fuel', 'vmware-settings', '--env', '1', '--download'])

        request = mrequests.get.call_args_list[0]
        url = request[0][0]

        m().write.assert_called_once_with(
            yaml.safe_dump(self.settings_data, default_flow_style=False))
        self.assertEqual(mrequests.get.call_count, 1)
        self.assertIn('/api/v1/clusters/1/vmware_attributes', url)
