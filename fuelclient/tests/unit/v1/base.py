#    Copyright 2013-2015 Mirantis, Inc.
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
from oslotest import base as oslo_base
import requests_mock as rm
import six

from fuelclient.cli import parser


class FakeFile(six.StringIO):
    """Context manager for a fake file

    NOTE(eli): We cannot use mock_open from mock library
    here, because it hangs when we use 'with' statement,
    and when we want to read file by chunks.

    """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class UnitTestCase(oslo_base.BaseTestCase):
    """Base test class which does not require nailgun server to run."""

    def setUp(self):
        super(UnitTestCase, self).setUp()

        self.auth_token_patcher = mock.patch('fuelclient.client.'
                                             'Client.auth_token',
                                             new_callable=mock.PropertyMock)

        self.auth_token_mock = self.auth_token_patcher.start()
        self.auth_token_mock.return_value = ''

        self.api_root_patcher = mock.patch('fuelclient.client.'
                                           'Client.api_root',
                                           new_callable=mock.PropertyMock)
        self.api_root_mock = self.api_root_patcher.start()
        self.api_root_mock.return_value = 'http://127.0.0.1:8003/api/v1/'

        self.ostf_root_patcher = mock.patch('fuelclient.client.'
                                            'Client.ostf_root',
                                            new_callable=mock.PropertyMock)
        self.ostf_root_mock = self.ostf_root_patcher.start()
        self.ostf_root_mock.return_value = 'http://127.0.0.1:8003/ostf/'

        self.m_request = rm.Mocker()
        self.m_request.start()

        self.addCleanup(self.auth_token_patcher.stop)
        self.addCleanup(self.api_root_patcher.stop)
        self.addCleanup(self.ostf_root_patcher.stop)
        self.addCleanup(self.m_request.stop)

    def execute(self, command):
        """Execute old CLI."""

        return parser.main(command)

    def mock_open(self, text, filename='some.file'):
        """Mocks builtin open function

        Usage example:

          with mock.patch('__builtin__.open', self.mock_open('file content')):
              # call mocked code
        """
        fileobj = FakeFile(text)
        setattr(fileobj, 'name', filename)
        return mock.MagicMock(return_value=fileobj)
