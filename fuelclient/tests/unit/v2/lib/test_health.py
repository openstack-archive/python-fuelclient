# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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


class TestHealthFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestHealthFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/ostf/'
        self.fake_test_sets = utils.get_fake_test_sets(10)
        self.fake_test_sets_items = utils.get_fake_test_set_items(10)

        self.client = fuelclient.get_client('health', self.version)

    def test_health_list_for_cluster(self):
        cluster_id = 65
        expected_uri = self.res_uri + 'testsets/{0}/'.format(cluster_id)
        matcher = self.m_request.get(expected_uri, json=self.fake_test_sets)

        data = self.client.get_all(cluster_id)

        self.assertTrue(matcher.called)
        self.assertEqual(len(data), 10)

    def test_health_status_list(self):
        expected_uri = self.res_uri + 'testruns/'
        matcher = self.m_request.get(expected_uri,
                                     json=self.fake_test_sets_items)

        data = self.client.get_status_all()

        self.assertTrue(matcher.called)
        self.assertEqual(len(data), 10)

    def test_health_status_list_for_cluster(self):
        cluster_id = 32
        expected_uri = self.res_uri + 'testruns/'
        fake_test_sets_items = [
            utils.get_fake_test_set_item(testset_id=12, cluster_id=cluster_id),
            utils.get_fake_test_set_item(testset_id=13, cluster_id=cluster_id),
            utils.get_fake_test_set_item(testset_id=14, cluster_id=35)
        ]
        matcher = self.m_request.get(expected_uri,
                                     json=fake_test_sets_items)

        data = self.client.get_status_all(cluster_id)

        self.assertTrue(matcher.called)
        self.assertEqual(len(data), 2)

    def test_health_status_show(self):
        testrun_id = 65
        cluster_id = 32
        fake_test_set_item = utils.get_fake_test_set_item(
            testset_id=testrun_id, cluster_id=cluster_id)
        expected_uri = self.get_object_uri(self.res_uri + 'testruns/',
                                           testrun_id)
        matcher = self.m_request.get(expected_uri,
                                     json=fake_test_set_item)

        data = self.client.get_status_single(testrun_id)

        self.assertTrue(matcher.called)
        self.assertEqual(testrun_id, data["id"])
        self.assertEqual(cluster_id, data["cluster_id"])
