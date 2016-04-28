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

        self.auth_required_patcher = mock.patch('fuelclient.client.'
                                                'APIClient.auth_required',
                                                new_callable=mock.PropertyMock)

        self.auth_required_mock = self.auth_required_patcher.start()
        self.auth_required_mock.return_value = False

        self.m_request = rm.Mocker()
        self.m_request.start()

        self.addCleanup(self.auth_required_patcher.stop)
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
