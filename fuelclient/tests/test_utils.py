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

import json
import os
import subprocess

import mock
import requests

from oslo_concurrency.processutils import ProcessExecutionError

from fuelclient.cli import error
from fuelclient.tests import base
from fuelclient import utils


class TestUtils(base.UnitTestCase):

    @mock.patch('fuelclient.utils.os.walk')
    def test_iterfiles(self, mwalk):
        mwalk.return_value = [
            ('/some_directory/', [], ['valid.yaml', 'invalid.yml'])]

        pattern = '*.yaml'
        directory = '/some_directory'

        expected_result = [os.path.join(directory, 'valid.yaml')]
        files = list(utils.iterfiles(directory, pattern))

        mwalk.assert_called_once_with(directory)
        self.assertEqual(expected_result, files)

    @mock.patch('fuelclient.utils.execute')
    def test_exec_cmd(self, exec_mock):
        cmd = 'some command'

        utils.exec_cmd(cmd, shell=True)

        exec_mock.assert_called_once_with(
            cmd,
            shell=True)

    @mock.patch('fuelclient.utils.execute',
                side_effect=ProcessExecutionError(
                    cmd='cmd',
                    exit_code=1,
                    stdout='stdout',
                    stderr='stderr'))
    def test_exec_cmd_raises_error(self, exec_mock):
        self.assertRaisesRegexp(
            error.ExecutedErrorNonZeroExitCode,
            'Shell command "cmd" executed with '
            'exit code: 1\n'
            'stdout: stdout\n'
            'stderr: stderr\n',
            utils.exec_cmd, 'cmd')

        exec_mock.assert_called_once_with('cmd')

    def test_parse_yaml_file(self):
        mock_open = self.mock_open("key: value")

        with mock.patch('fuelclient.utils.io.open', mock_open):
            self.assertEqual(
                utils.parse_yaml_file('some_file_name'),
                {'key': 'value'})

    @mock.patch('fuelclient.utils.glob.iglob',
                return_value=['file1', 'file2'])
    @mock.patch('fuelclient.utils.parse_yaml_file',
                side_effect=['content_file1', 'content_file2'])
    def test_glob_and_parse_yaml(self, parse_mock, iglob_mock):
        path = '/tmp/path/mask*'

        content = []
        for data in utils.glob_and_parse_yaml(path):
            content.append(data)

        iglob_mock.assert_called_once_with(path)
        self.assertEqual(
            parse_mock.call_args_list,
            [mock.call('file1'),
             mock.call('file2')])

        self.assertEqual(content, ['content_file1', 'content_file2'])

    def test_major_plugin_version(self):
        pairs = [
            ['1.2.3', '1.2'],
            ['123456789.123456789.12121', '123456789.123456789'],
            ['1.2', '1.2']]

        for arg, expected in pairs:
            self.assertEqual(
                utils.major_plugin_version(arg),
                expected)

    @mock.patch('fuelclient.utils.os.path.lexists', side_effect=[True, False])
    def test_file_exists(self, lexists_mock):
        self.assertTrue(utils.file_exists('file1'))
        self.assertFalse(utils.file_exists('file2'))

        self.assertEqual(
            lexists_mock.call_args_list,
            [mock.call('file1'), mock.call('file2')])

    def test_get_error_body_get_from_json(self):
        error_body = 'This is error body'

        resp = requests.Response()
        resp._content = json.dumps({
            'message': error_body
        })

        exception = requests.HTTPError()
        exception.response = resp

        self.assertEqual(error.get_error_body(exception), error_body)

    def test_get_error_body_get_from_plaintext(self):
        error_body = 'This is error body'

        resp = requests.Response()
        resp._content = error_body

        exception = requests.HTTPError()
        exception.response = resp

        self.assertEqual(error.get_error_body(exception), error_body)
