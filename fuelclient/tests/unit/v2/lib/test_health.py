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

import mock

import fuelclient
from fuelclient.cli import error
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

    def test_health_status_show_non_existing_testrun(self):
        testrun_id = 65
        expected_uri = self.get_object_uri(self.res_uri + 'testruns/',
                                           testrun_id)
        matcher = self.m_request.get(expected_uri, json={})

        msg = "Test sets with id {id} does not exist".format(id=testrun_id)
        self.assertRaisesRegexp(error.ActionException,
                                msg,
                                self.client.get_status_single,
                                testrun_id)
        self.assertTrue(matcher.called)

    @mock.patch('fuelclient.objects.Environment')
    def test_health_start(self, m_env_obj):
        cluster_id = 32
        cluster_state = 'operational'
        test_sets = ['fake_test_set1', 'fake_test_set2']
        expected_uri = self.res_uri + 'testruns/'
        type(m_env_obj.return_value).status = mock.PropertyMock(
            return_value=cluster_state)
        type(m_env_obj.return_value).is_customized = mock.PropertyMock(
            return_value=False)
        expected_body = [
            {'testset': test_sets[0],
             'metadata': {'cluster_id': cluster_id, 'config': {}}},
            {'testset': test_sets[1],
             'metadata': {'cluster_id': cluster_id, 'config': {}}}
        ]
        matcher = self.m_request.post(expected_uri, json=expected_body)

        data = self.client.start(cluster_id,
                                 ostf_credentials={},
                                 test_sets=test_sets,
                                 force=False)
        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())
        self.assertEqual(data, matcher.last_request.json())

    @mock.patch('fuelclient.objects.Environment')
    def test_health_start_fail_not_allowed_env_status(self, m_env_obj):
        cluster_id = 32
        cluster_state = 'new'
        test_sets = ['fake_test_set1', 'fake_test_set2']
        type(m_env_obj.return_value).status = mock.PropertyMock(
            return_value=cluster_state)

        msg = ("Environment is not ready to run health check "
               "because it is in '{0}' state.".format(cluster_state))
        self.assertRaisesRegexp(error.EnvironmentException,
                                msg,
                                self.client.start,
                                cluster_id,
                                ostf_credentials={},
                                test_sets=test_sets,
                                force=False)

    @mock.patch('fuelclient.objects.Environment')
    def test_health_start_not_allowed_env_status_w_force(self, m_env_obj):
        cluster_id = 32
        cluster_state = 'new'
        test_sets = ['fake_test_set1', 'fake_test_set2']
        expected_uri = self.res_uri + 'testruns/'
        type(m_env_obj.return_value).status = mock.PropertyMock(
            return_value=cluster_state)
        type(m_env_obj.return_value).is_customized = mock.PropertyMock(
            return_value=False)
        expected_body = [
            {'testset': test_sets[0],
             'metadata': {'cluster_id': cluster_id, 'config': {}}},
            {'testset': test_sets[1],
             'metadata': {'cluster_id': cluster_id, 'config': {}}}
        ]
        matcher = self.m_request.post(expected_uri, json=expected_body)

        data = self.client.start(cluster_id,
                                 ostf_credentials={},
                                 test_sets=test_sets,
                                 force=True)
        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())
        self.assertEqual(data, matcher.last_request.json())

    @mock.patch('fuelclient.objects.Environment')
    def test_health_start_fail_customized_env(self, m_env_obj):
        cluster_id = 32
        cluster_state = 'operational'
        is_customized = True
        test_sets = ['fake_test_set1', 'fake_test_set2']
        type(m_env_obj.return_value).status = mock.PropertyMock(
            return_value=cluster_state)
        type(m_env_obj.return_value).is_customized = mock.PropertyMock(
            return_value=is_customized)
        msg = ("Environment deployment facts were updated. "
               "Health check is likely to fail because of that.")
        self.assertRaisesRegexp(error.EnvironmentException,
                                msg,
                                self.client.start,
                                cluster_id,
                                ostf_credentials={},
                                test_sets=test_sets,
                                force=False)

    @mock.patch('fuelclient.objects.Environment')
    def test_health_start_customized_env_w_force(self, m_env_obj):
        cluster_id = 32
        cluster_state = 'operational'
        is_customized = True
        test_sets = ['fake_test_set1', 'fake_test_set2']
        expected_uri = self.res_uri + 'testruns/'
        type(m_env_obj.return_value).status = mock.PropertyMock(
            return_value=cluster_state)
        type(m_env_obj.return_value).is_customized = mock.PropertyMock(
            return_value=is_customized)
        expected_body = [
            {'testset': test_sets[0],
             'metadata': {'cluster_id': cluster_id, 'config': {}}},
            {'testset': test_sets[1],
             'metadata': {'cluster_id': cluster_id, 'config': {}}}
        ]
        matcher = self.m_request.post(expected_uri, json=expected_body)

        data = self.client.start(cluster_id,
                                 ostf_credentials={},
                                 test_sets=test_sets,
                                 force=True)
        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())
        self.assertEqual(data, matcher.last_request.json())

    @mock.patch('fuelclient.objects.Environment')
    def test_health_start_w_ostf_credentials(self, m_env_obj):
        cluster_id = 32
        cluster_state = 'operational'
        is_customized = False
        test_sets = ['fake_test_set1', 'fake_test_set2']
        ostf_credentials = {
            'username': 'admin',
            'password': 'admin',
            'tenant': 'admin'
        }
        expected_uri = self.res_uri + 'testruns/'
        type(m_env_obj.return_value).status = mock.PropertyMock(
            return_value=cluster_state)
        type(m_env_obj.return_value).is_customized = mock.PropertyMock(
            return_value=is_customized)
        expected_body = [
            {'testset': test_sets[0],
             'metadata': {
                 'ostf_os_access_creds':
                     {'ostf_os_username': 'admin',
                      'ostf_os_tenant_name': 'admin',
                      'ostf_os_password': 'admin'},
                 'cluster_id': cluster_id,
                 'config': {}}},
            {'testset': test_sets[1],
             'metadata': {
                 'ostf_os_access_creds':
                     {'ostf_os_username': 'admin',
                      'ostf_os_tenant_name': 'admin',
                      'ostf_os_password': 'admin'},
                 'cluster_id': cluster_id,
                 'config': {}}}
        ]

        matcher = self.m_request.post(expected_uri, json=expected_body)

        data = self.client.start(cluster_id,
                                 ostf_credentials=ostf_credentials,
                                 test_sets=test_sets,
                                 force=False)
        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())
        self.assertEqual(data, matcher.last_request.json())

    def test_health_stop_action(self):
        testrun_id = 65
        cluster_id = 32
        expected_uri = self.res_uri + 'testruns/'
        fake_test_set_item = utils.get_fake_test_set_item(
            testset_id=testrun_id, cluster_id=cluster_id)
        matcher = self.m_request.put(expected_uri,
                                     json=[fake_test_set_item])

        data = self.client.action(testrun_id, action_status='stopped')

        self.assertTrue(matcher.called)
        self.assertEqual(testrun_id, data["id"])
        self.assertEqual(cluster_id, data["cluster_id"])

    def test_health_restart_action(self):
        testrun_id = 65
        cluster_id = 32
        expected_uri = self.res_uri + 'testruns/'
        fake_test_set_item = utils.get_fake_test_set_item(
            testset_id=testrun_id, cluster_id=cluster_id)
        matcher = self.m_request.put(expected_uri,
                                     json=[fake_test_set_item])

        data = self.client.action(testrun_id, action_status='restarted')

        self.assertTrue(matcher.called)
        self.assertEqual(testrun_id, data["id"])
        self.assertEqual(cluster_id, data["cluster_id"])
