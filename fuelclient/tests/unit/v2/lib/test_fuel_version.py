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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestFuelVersionFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestFuelVersionFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/version/'.format(version=self.version)

        self.fake_version = utils.get_fake_fuel_version()

        self.client = fuelclient.get_client('fuel-version', self.version)

    def test_fuel_version(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_version)

        self.client.get_all()

        self.assertTrue(matcher.called)
