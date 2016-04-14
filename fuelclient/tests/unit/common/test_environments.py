# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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
import os

from fuelclient import objects

from fuelclient.tests.unit.v1 import base


class TestEnvironmentObject(base.UnitTestCase):

    def setUp(self):
        super(TestEnvironmentObject, self).setUp()
        self.env_object = objects.Environment(1)

    def _setup_os_mock(self, os_mock):
        os_mock.path.exists.return_value = False
        os_mock.path.join = os.path.join
        os_mock.path.abspath = lambda x: x

    @mock.patch("fuelclient.objects.environment.os")
    def test_write_facts_to_dir_for_legacy_envs(self, os_mock):
        facts = [
            {
                "uid": "1",
                "role": "controller",
                "data": "data1"
            },
            {
                "uid": "2",
                "role": "compute",
                "data": "data2"
            },
        ]

        self._setup_os_mock(os_mock)
        serializer = mock.MagicMock()

        self.env_object.write_facts_to_dir(
            "deployment", facts, serializer=serializer
        )

        serializer.write_to_path.assert_has_calls(
            [
                mock.call("./deployment_1/controller_1", facts[0]),
                mock.call("./deployment_1/compute_2", facts[1])
            ]
        )

    @mock.patch("fuelclient.objects.environment.os")
    def test_write_facts_to_dir_for_new_envs(self, os_mock):
        facts = [
            {
                "uid": "1",
                "roles": ["controller"],
                "data": "data1"
            },
            {
                "uid": "2",
                "roles": ["compute"],
                "data": "data2"
            },
        ]

        self._setup_os_mock(os_mock)
        serializer = mock.MagicMock()

        self.env_object.write_facts_to_dir(
            "deployment", facts, serializer=serializer
        )

        serializer.write_to_path.assert_has_calls(
            [
                mock.call("./deployment_1/1", facts[0]),
                mock.call("./deployment_1/2", facts[1])
            ]
        )

    @mock.patch("fuelclient.objects.environment.os")
    def test_write_facts_to_dir_if_facts_is_dict(self, os_mock):
        facts = {
            "engine": "test_engine",
            "nodes": [
                {
                    "uid": "1",
                    "name": "node-1",
                    "roles": ["controller"],
                    "data": "data1"
                },
                {
                    "uid": "2",
                    "name": "node-2",
                    "roles": ["compute"],
                    "data": "data2"
                },
            ]
        }

        self._setup_os_mock(os_mock)
        serializer = mock.MagicMock()

        self.env_object.write_facts_to_dir(
            "deployment", facts, serializer=serializer
        )

        serializer.write_to_path.assert_has_calls(
            [
                mock.call("./deployment_1/engine", facts['engine']),
                mock.call("./deployment_1/node-1", facts['nodes'][0]),
                mock.call("./deployment_1/node-2", facts['nodes'][1])
            ]
        )
