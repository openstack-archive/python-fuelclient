# -*- coding: utf-8 -*-

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

import json

import mock
from six import moves
import yaml

from fuelclient.cli.actions import base
from fuelclient.cli import error
from fuelclient.tests.unit.v1 import base as base_tests
from fuelclient.tests.utils import fake_fuel_version


class TestBaseAction(base_tests.UnitTestCase):

    def setUp(self):
        super(TestBaseAction, self).setUp()
        self.action = base.Action()

    @mock.patch('fuelclient.cli.actions.base.os')
    def test_default_directory_with_param(self, m_os):
        directory = 'some/dir'
        self.action.default_directory(directory)
        m_os.path.abspath.assert_called_once_with(directory)

    @mock.patch('fuelclient.cli.actions.base.os')
    def test_default_directory_without_param(self, m_os):
        self.action.default_directory()
        m_os.path.abspath.assert_called_once_with(m_os.curdir)

    @mock.patch('fuelclient.cli.actions.base.os.mkdir')
    @mock.patch('fuelclient.cli.actions.base.os.path.exists')
    def test_full_path_directory(self, m_exists, m_mkdir):
        m_exists.return_value = False
        self.assertEqual(
            self.action.full_path_directory('/base/path', 'subdir'),
            '/base/path/subdir'
        )
        m_mkdir.assert_called_once_with('/base/path/subdir')

    @mock.patch('fuelclient.cli.actions.base.os')
    def test_full_path_directory_no_access(self, m_os):
        exc_msg = 'Bas permissions'
        m_os.path.exists.return_value = False
        m_os.mkdir.side_effect = OSError(exc_msg)

        with self.assertRaisesRegexp(error.ActionException, exc_msg):
            self.action.full_path_directory('/base/path', 'subdir')

    @mock.patch('fuelclient.cli.actions.base.os')
    def test_full_path_directory_already_exists(self, m_os):
        m_os.path.exists.return_value = True
        self.action.full_path_directory('/base/path', 'subdir')
        self.assertEqual(m_os.mkdir.call_count, 0)


class TestFuelVersion(base_tests.UnitTestCase):

    VERSION = fake_fuel_version.get_fake_fuel_version()

    def test_return_yaml(self):
        self.m_request.get('/api/v1/version', json=self.VERSION)

        with mock.patch('sys.stdout') as mstdout:
            self.assertRaises(SystemExit,
                              self.execute,
                              ['fuel', '--fuel-version', '--yaml'])
        args, _ = mstdout.write.call_args_list[0]
        regex = ('No JSON object could be decoded'
                 '|Expecting value: line 1 column 1')
        with self.assertRaisesRegexp(ValueError, regex):
            json.loads(args[0])
        self.assertEqual(self.VERSION, yaml.load(args[0]))

    def test_return_json(self):
        self.m_request.get('/api/v1/version', json=self.VERSION)

        with mock.patch('sys.stdout') as mstdout:
            self.assertRaises(SystemExit,
                              self.execute,
                              ['fuel', '--fuel-version', '--json'])
        args, _ = mstdout.write.call_args_list[0]
        self.assertEqual(self.VERSION, json.loads(args[0]))


class TestExtraArguments(base_tests.UnitTestCase):

    def test_error_on_extra_arguments(self):
        err_msg = 'unrecognized arguments: extraarg1 extraarg2\n'

        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.assertRaises(
                SystemExit, self.execute,
                ['fuel', 'nodegroup', '--delete', 'extraarg1', 'extraarg2'])

            self.assertIn(err_msg, m_stderr.getvalue())
