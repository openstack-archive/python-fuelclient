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


import mock
import requests
import shlex
from six import moves

from oslotest import base as oslo_base

from fuelclient import main as main_mod


@mock.patch('cliff.command.Command.run')
class TestHTTPExpectionsCommand(oslo_base.BaseTestCase):
    """Tests for fuel commands with HTTPError response."""

    def setUp(self):
        super(TestHTTPExpectionsCommand, self).setUp()

    def test_basic(self, m_run):
        args = 'env deploy 1'
        response = mock.MagicMock()
        response.json = mock.Mock(return_value={'message': 'Invalid Test'})
        m_run.side_effect = requests.HTTPError(response=response)
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('Invalid Test\n', m_stderr.getvalue())

    def test_general_execption(self, m_run):
        args = 'env deploy 1'
        m_run.side_effect = Exception('Boom!')
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('Boom!\n', m_stderr.getvalue())

    def test_no_message(self, m_run):
        args = 'env deploy 1'
        response = mock.MagicMock()
        response.json = mock.Mock(return_value={})
        m_run.side_effect = requests.HTTPError(
                'just in case',
                response=response)
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('just in case\n', m_stderr.getvalue())

    def test_wrong_json_expection(self, m_run):
        args = 'env deploy 1'
        response = mock.MagicMock()
        response.json = mock.Mock(side_effect=ValueError('no value'))
        m_run.side_effect = requests.HTTPError('main error', response=response)
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('main error\n', m_stderr.getvalue())

    def exec_command(self, command=''):
        """Executes fuelclient with the specified arguments."""

        return main_mod.main(argv=shlex.split(command))
