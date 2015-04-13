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

import cStringIO
import mock
import yaml

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_fuel_version


class TestFuelVersionCommand(test_engine.BaseCLITest):
    """Tests for fuel2 version * commands."""

    def setUp(self):
        super(TestFuelVersionCommand, self).setUp()
        self.m_client.get_all.return_value = \
            fake_fuel_version.get_fake_fuel_version()

    def test_fuel_version(self):
        args = 'fuel-version'

        with mock.patch('sys.stdout', new=cStringIO.StringIO()) as m_stdout:
            self.exec_command(args)
            self.assertEqual(fake_fuel_version.get_fake_fuel_version(),
                             yaml.safe_load(m_stdout.getvalue()))
