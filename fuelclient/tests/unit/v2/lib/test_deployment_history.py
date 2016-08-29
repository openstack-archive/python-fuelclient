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
                       '/deployment_history/' \
                       ''.format(self.version, self.transaction_id)

        self.fake_history = utils.get_fake_deployment_history()

        self.client = fuelclient.get_client('deployment_history', self.version)

    def get_url(self, nodes='', statuses='', tasks_names=''):
        params = '?nodes={}&statuses={}&tasks_names={}'
        return self.res_uri + params.format(nodes, statuses, tasks_names)

    def test_deployment_history_list(self):

        matcher = self.m_request.get(self.get_url(), json=self.fake_history)

        self.client.get_all(
            transaction_id=self.transaction_id,
            nodes=None,
            statuses=None)

        self.assertTrue(matcher.called)

    def test_deployment_history(self):

        matcher = self.m_request.get(
            self.get_url(
                nodes='1,2',
                statuses='ready,error,pending',
                tasks_names='controller-remaining-tasks,'
                            'ironic-compute,pending-task'
            ), json=self.fake_history)

        tasks_after_facade = self.client.get_all(
            transaction_id=self.transaction_id,
            nodes=['1', '2'],
            statuses=['ready', 'error', 'pending'],
            tasks_names=['controller-remaining-tasks',
                         'ironic-compute', 'pending-task'],
            show_parameters=False
        )

        self.assertTrue(matcher.called)
        self.assertItemsEqual(
            utils.get_fake_deployment_history(convert_legacy_fields=True),
            tasks_after_facade)

    def test_deployment_history_include_summary(self):
        fake_history = utils.get_fake_deployment_history(include_summary=True)
        matcher = self.m_request.get(
            self.get_url(
                nodes='1,2',
                statuses='ready,error,pending',
                tasks_names='controller-remaining-tasks,'
                            'ironic-compute,pending-task'
            ) + '&include_summary=1', json=fake_history)

        tasks_after_facade = self.client.get_all(
            transaction_id=self.transaction_id,
            nodes=['1', '2'],
            statuses=['ready', 'error', 'pending'],
            tasks_names=['controller-remaining-tasks',
                         'ironic-compute', 'pending-task'],
            include_summary=True,
            show_parameters=False
        )

        self.assertTrue(matcher.called)
        self.assertItemsEqual(
            utils.get_fake_deployment_history(convert_legacy_fields=True,
                                              include_summary=True),
            tasks_after_facade)

    def test_deployment_history_parameters(self):

        matcher = self.m_request.get(
            self.get_url(
                nodes='1,2',
                statuses='ready,error,pending',
                tasks_names='controller-remaining-tasks,'
                            'ironic-compute,pending-task'
            ),
            json=utils.get_fake_deployment_history(add_task_data=True),
        )

        tasks_after_facade = self.client.get_all(
            transaction_id=self.transaction_id,
            nodes=['1', '2'],
            statuses=['ready', 'error', 'pending'],
            tasks_names=['controller-remaining-tasks',
                         'ironic-compute', 'pending-task'],
            show_parameters=True
        )

        self.assertTrue(matcher.called)
        self.assertItemsEqual(
            utils.get_fake_deployment_history_w_params(),
            tasks_after_facade)
