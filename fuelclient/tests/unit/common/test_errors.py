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


import shlex

import mock
from oslotest import base as oslo_base
import requests
from six import moves

from fuelclient import main as main_mod


class TestHTTPExpectionsCommand(oslo_base.BaseTestCase):
    """Tests for fuel commands with HTTPError response."""

    def setUp(self):
        super(TestHTTPExpectionsCommand, self).setUp()
        self._m_run_patcher = mock.patch('cliff.command.Command.run')
        self.m_run = self._m_run_patcher.start()
        self.addCleanup(self._m_run_patcher.stop)

    def test_basic(self):
        args = 'env deploy 1'
        response = mock.MagicMock()
        response.json = mock.Mock(return_value={'message': 'Invalid Test'})
        self.m_run.side_effect = requests.HTTPError(response=response)
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('Invalid Test\n', m_stderr.getvalue())

    def test_general_exception(self):
        args = 'env deploy 1'
        self.m_run.side_effect = Exception('Boom!')
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('Boom!\n', m_stderr.getvalue())

    def test_no_message(self):
        args = 'env deploy 1'
        response = mock.MagicMock()
        response.json = mock.Mock(return_value={})
        self.m_run.side_effect = requests.HTTPError('just in case',
                                                    response=response)
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('just in case\n', m_stderr.getvalue())

    def test_wrong_json_expcetion(self):
        args = 'env deploy 1'
        response = mock.MagicMock()
        response.json = mock.Mock(side_effect=ValueError('no value'))
        self.m_run.side_effect = requests.HTTPError('main error',
                                                    response=response)
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertEqual('main error\n', m_stderr.getvalue())

    def exec_command(self, command=''):
        """Executes fuelclient with the specified arguments."""

        return main_mod.main(argv=shlex.split(command))
