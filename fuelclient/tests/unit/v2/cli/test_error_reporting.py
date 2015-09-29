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
from six import moves

from fuelclient.tests.unit.v2.cli import test_engine


class TestErrorReporting(test_engine.BaseCLITest):

    def test_debug_is_off_traceback_is_absent(self):
        upload_mock = self.m_client.upload_network_template
        upload_mock.side_effect = Exception('File cannot be opened.')
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command('network-template upload --file /foo/bar/baz 1')
            self.assertIn('File cannot be opened.', m_stderr.getvalue())
            self.assertNotIn('Traceback', m_stderr.getvalue())

    def test_debug_is_on_output_traceback(self):
        upload_mock = self.m_client.upload_network_template
        upload_mock.side_effect = Exception('File cannot be opened.')
        cmd = 'network-template upload --file /foo/bar/baz 1 --debug'
        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            try:
                self.exec_command(cmd)
                # The following assert statement shouldn't be
                # executed, `exec_command` must raise SystemExit
                # exception.
                self.assertTrue(False)
            except SystemExit:
                self.assertIn('File cannot be opened.', m_stderr.getvalue())
                self.assertIn('Traceback (most recent call last)',
                              m_stderr.getvalue())
