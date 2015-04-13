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
import six
import subprocess

import mock
import requests

from fuelclient.cli import error
from fuelclient.common import data_utils
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

    def make_process_mock(self, return_code=0):
        process_mock = mock.Mock()
        process_mock.stdout = ['Stdout line 1', 'Stdout line 2']
        process_mock.returncode = return_code

        return process_mock

    def test_exec_cmd(self):
        cmd = 'some command'

        process_mock = self.make_process_mock()
        with mock.patch.object(
                subprocess, 'Popen', return_value=process_mock) as popen_mock:
            utils.exec_cmd(cmd)

        popen_mock.assert_called_once_with(
            cmd,
            stdout=None,
            stderr=subprocess.STDOUT,
            shell=True,
            cwd=None)

    def test_exec_cmd_raises_error(self):
        cmd = 'some command'
        return_code = 1

        process_mock = self.make_process_mock(return_code=return_code)

        with mock.patch.object(
                subprocess, 'Popen', return_value=process_mock) as popen_mock:
            self.assertRaisesRegexp(
                error.ExecutedErrorNonZeroExitCode,
                'Shell command executed with "{0}" '
                'exit code: {1} '.format(return_code, cmd),
                utils.exec_cmd, cmd)

        popen_mock.assert_called_once_with(
            cmd,
            stdout=None,
            stderr=subprocess.STDOUT,
            shell=True,
            cwd=None)

    def test_exec_cmd_iterator(self):
        cmd = 'some command'

        process_mock = self.make_process_mock()
        with mock.patch.object(
                subprocess, 'Popen', return_value=process_mock) as popen_mock:
            for line in utils.exec_cmd_iterator(cmd):
                self.assertTrue(line.startswith('Stdout line '))

        popen_mock.assert_called_once_with(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)

    def test_exec_cmd_iterator_raises_error(self):
        cmd = 'some command'
        return_code = 1

        process_mock = self.make_process_mock(return_code=return_code)
        with mock.patch.object(subprocess, 'Popen', return_value=process_mock):
            with self.assertRaisesRegexp(
                    error.ExecutedErrorNonZeroExitCode,
                    'Shell command executed with "{0}" '
                    'exit code: {1} '.format(return_code, cmd)):
                for line in utils.exec_cmd_iterator(cmd):
                    self.assertTrue(line.startswith('Stdout line '))

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

    def test_get_display_data_single(self):
        test_data = {'a': 1, 'b': 2, 'c': 3}
        fields = ('b', 'c')

        result = data_utils.get_display_data_single(fields, test_data)
        self.assertEqual([2, 3], result)

    def test_get_display_data_single_empty_val(self):
        test_data = {'a': 1, 'b': {}, 'c': []}
        fields = ('a', 'b', 'c')

        result = data_utils.get_display_data_single(fields, test_data)
        self.assertEqual([1, '-', '-'], result)

    def test_get_display_data_single_list_val(self):
        test_data = {'a': 1, 'b': ['2'], 'c': ['3', '4']}
        fields = ('a', 'b', 'c')

        result = data_utils.get_display_data_single(fields, test_data)
        self.assertEqual([1, '2', '3, 4'], result)

    def test_get_display_data_bad_key(self):
        test_data = {'a': 1, 'b': 2, 'c': 3}
        fields = ('b', 'bad_key')

        self.assertRaises(KeyError,
                          data_utils.get_display_data_single,
                          fields, test_data)

    def test_get_display_data_multi(self):
        test_data = [{'a': 1, 'b': 2, 'c': 3}, {'b': 8, 'c': 9}]
        fields = ('b', 'c')

        result = data_utils.get_display_data_multi(fields, test_data)
        self.assertEqual([[2, 3], [8, 9]], result)

    @mock.patch('sys.getfilesystemencoding', return_value='utf-8')
    def test_str_to_unicode(self, _):
        test_data = 'тест'
        expected_data = test_data if six.PY3 else u'тест'
        result = utils.str_to_unicode(test_data)
        self.assertIsInstance(result, six.text_type)
        self.assertEqual(result, expected_data)

    @mock.patch('sys.getfilesystemencoding', return_value='iso-8859-16')
    def test_latin_str_to_unicode(self, _):
        test_data = 'czegoś' if six.PY3 else u'czegoś'.encode('iso-8859-16')
        expected_data = test_data if six.PY3 else u'czegoś'
        result = utils.str_to_unicode(test_data)
        self.assertIsInstance(result, six.text_type)
        self.assertEqual(result, expected_data)
