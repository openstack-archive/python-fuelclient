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

from fuelclient.tests import base
from fuelclient.tests.utils import fake_fuel_version


@requests_mock.mock()
class TestFuelVersion(base.UnitTestCase):

    def test_return_yaml(self, mrequests):
        mrequests.get('/api/v1/version/',
                      json=fake_fuel_version.get_fake_fuel_version())

        with mock.patch('sys.stdout') as mstdout:
            self.execute(['fuel', 'fuel-version', '--yaml'])
        args, _ = mstdout.write.call_args_list[0]
        with self.assertRaisesRegexp(
                ValueError, 'No JSON object could be decoded'):
            json.loads(args[0])
        self.assertEqual(
            fake_fuel_version.get_fake_fuel_version(),
            yaml.safe_load(args[0]))

    def test_return_json(self, mrequests):
        mrequests.get('/api/v1/version/',
                      json=fake_fuel_version.get_fake_fuel_version())

        with mock.patch('sys.stdout') as mstdout:
            self.execute(['fuel', 'fuel-version', '--json'])
        args, _ = mstdout.write.call_args_list[0]
        self.assertEqual(
            fake_fuel_version.get_fake_fuel_version(),
            json.loads(args[0]))
