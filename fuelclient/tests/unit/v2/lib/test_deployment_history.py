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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestDeploymentHistoryFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestDeploymentHistoryFacade, self).setUp()

        self.version = 'v1'
        self.transaction_id = '1'
        self.res_uri = '/api/{0}/transactions/{1}'\
                       '/deployment_history/?nodes=&statuses='.format(
                           self.version, self.transaction_id)

        self.fake_history = utils.get_fake_deployment_history()

        self.client = fuelclient.get_client('deployment_history',
                                            self.version)

    def test_deployment_history_list(self):

        matcher = self.m_request.get(self.res_uri, json=self.fake_history)

        self.client.get_all(
            transaction_id=self.transaction_id,
            nodes=None,
            statuses=None)

        self.assertTrue(matcher.called)
