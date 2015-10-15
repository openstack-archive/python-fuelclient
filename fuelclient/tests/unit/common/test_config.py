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

import os

import fixtures
import mock

from fuelclient import fuelclient_settings
from fuelclient.tests.unit.v1 import base


class TestSettings(base.UnitTestCase):

    @mock.patch('shutil.copy')
    @mock.patch('os.chmod')
    @mock.patch('os.path.exists')
    def test_config_generation(self, m_exists, m_chmod, m_copy):
        project_dir = os.path.dirname(fuelclient_settings.__file__)

        expected_mode = 0o600
        expected_default = os.path.join(project_dir,
                                        'fuelclient_settings.yaml')
        expected_path = os.path.expanduser('~/.config/fuel_client.yaml')

        fuelclient_settings._SETTINGS = None
        m_exists.return_value = False
        self.useFixture(fixtures.EnvironmentVariable('XDG_CONFIG_HOME', None))

        fuelclient_settings.get_settings()

        m_copy.assert_called_once_with(expected_default, expected_path)
        m_chmod.assert_called_once_with(expected_path, expected_mode)
