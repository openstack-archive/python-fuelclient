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

import mock

from fuelclient.tests.unit.v2.cli import test_engine


class TestNetworkTemplateCommand(test_engine.BaseCLITest):

    def test_network_template_upload(self):
        args = 'network-template upload 1'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.upload_network_template.assert_called_once_with(
            1, None)

    def test_network_template_upload_w_file(self):
        args = 'network-template upload --file /tmp/test-file 1'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.upload_network_template.assert_called_once_with(
            1, '/tmp/test-file')

    def test_network_template_download(self):
        download_mock = self.m_client.download_network_template
        download_mock.return_value = '/tmp/test-dir/settings_1'

        args = 'network-template download 1'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        download_mock.assert_called_once_with(1, None)

    def test_network_template_download_w_dir(self):
        download_mock = self.m_client.download_network_template
        download_mock.return_value = '/tmp/test-dir/settings_1'

        args = 'network-template download --dir /tmp/test-dir 1'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        download_mock.assert_called_once_with(1, '/tmp/test-dir')

    def test_network_template_delete(self):
        args = 'network-template delete 1'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        delete_mock = self.m_client.delete_network_template
        delete_mock.assert_called_once_with(1)
