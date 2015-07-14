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
import requests_mock
import yaml

from fuelclient.cli.actions import base
from fuelclient.cli import error
from fuelclient.tests import base as base_tests


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


@requests_mock.mock()
class TestFuelVersion(base_tests.UnitTestCase):

    VERSION = {
        "astute_sha": "16b252d93be6aaa73030b8100cf8c5ca6a970a91",
        "release": "6.0",
        "build_id": "2014-12-26_14-25-46",
        "build_number": "58",
        "auth_required": True,
        "fuellib_sha": "fde8ba5e11a1acaf819d402c645c731af450aff0",
        "production": "docker",
        "nailgun_sha": "5f91157daa6798ff522ca9f6d34e7e135f150a90",
        "release_versions": {
            "2014.2-6.0": {
                "VERSION": {
                    "ostf_sha": "a9afb68710d809570460c29d6c3293219d3624d4",
                    "astute_sha": "16b252d93be6aaa73030b8100cf8c5ca6a970a91",
                    "release": "6.0",
                    "build_id": "2014-12-26_14-25-46",
                    "build_number": "58",
                    "fuellib_sha": "fde8ba5e11a1acaf819d402c645c731af450aff0",
                    "production": "docker",
                    "nailgun_sha": "5f91157daa6798ff522ca9f6d34e7e135f150a90",
                    "api": "1.0",
                    "fuelmain_sha": "81d38d6f2903b5a8b4bee79ca45a54b76c1361b8",
                    "feature_groups": [
                        "mirantis"
                    ]
                }
            }
        },
        "api": "1.0",
        "fuelmain_sha": "81d38d6f2903b5a8b4bee79ca45a54b76c1361b8",
        "feature_groups": [
            "mirantis"
        ]
    }

    def test_return_yaml(self, mrequests):
        mrequests.get('/api/v1/version', json=self.VERSION)

        with mock.patch('sys.stdout') as stdout:
            with self.assertRaises(SystemExit):
                self.execute(['fuel', '--fuel-version', '--yaml'])
        args, _ = stdout.write.call_args
        with self.assertRaisesRegexp(
                ValueError, 'No JSON object could be decoded'):
            json.loads(args[0])
        yaml.load(args[0])

    def test_return_json(self, mrequests):
        mrequests.get('/api/v1/version', json=self.VERSION)

        with mock.patch('sys.stdout') as stdout:
            with self.assertRaises(SystemExit):
                self.execute(['fuel', '--fuel-version', '--json'])
        args, _ = stdout.write.call_args
        json.loads(args[0])
