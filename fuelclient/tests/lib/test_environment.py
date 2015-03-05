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

import mock
import requests_mock as rm

import fuelclient
from fuelclient.cli import error
from fuelclient.objects import base as base_object
from fuelclient.objects import environment as env_object
from fuelclient.objects import task as task_object
from fuelclient.tests.lib import test_api


class TestEnvFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestEnvFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/clusters/'.format(version=self.version)

        self.client = fuelclient.get_client('environment', self.version)

    def test_env_list(self):
        self.client.get_all()

        self.assertEqual(rm.GET, self.session_adapter.last_request.method)
        self.assertEqual(self.res_uri, self.session_adapter.last_request.path)

    def test_env_show(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        self.client.get_by_id(env_id)

        self.assertEqual(rm.GET, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

    def test_env_delete(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        self.client.delete_by_id(env_id)

        self.assertEqual(rm.DELETE, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

    @mock.patch.object(env_object.Environment, 'init_with_data')
    def test_env_create(self, m_init):
        node_name = 'test_node'
        release_id = 20
        nst = 'gre'
        net = 'neutron'
        mode = 'ha_compact'

        self.client.create(node_name, release_id, net, mode, nst)

        req_data = self.session_adapter.last_request.json()

        self.assertEqual(rm.POST, self.session_adapter.last_request.method)
        self.assertEqual(self.res_uri, self.session_adapter.last_request.path)

        # TODO(romcheg): deployment mode requires investigation
        self.assertEqual(release_id, req_data['release_id'])
        self.assertEqual(node_name, req_data['name'])
        self.assertEqual(nst, req_data['net_segment_type'])

    def test_env_create_no_nst_neutron(self):
        node_name = 'test_node'
        release_id = 20
        net = 'neutron'

        self.assertRaises(error.ArgumentException,
                          self.client.create,
                          node_name, release_id, net)

    def test_env_create_nst_nova(self):
        node_name = 'test_node'
        release_id = 20
        net = 'nova'
        nst = 'gre'

        self.assertRaises(error.ArgumentException,
                          self.client.create,
                          node_name, release_id, net, net_segment_type=nst)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/changes')

        self.client.deploy_changes(env_id)

        self.assertEqual(rm.PUT, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

    @mock.patch.object(base_object.BaseObject, 'init_with_data')
    def test_env_upgrade(self, m_init):
        env_id = 42
        release_id = 10
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/update/')

        self.client.upgrade(env_id, release_id)

        self.assertEqual(rm.PUT, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

    @mock.patch.object(base_object.BaseObject, 'init_with_data')
    def test_env_update(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        self.client.update(env_id, name="new_name")
        req_data = self.session_adapter.request_history[0].json()

        self.assertEqual(rm.PUT,
                         self.session_adapter.request_history[0].method)
        self.assertEqual(expected_uri,
                         self.session_adapter.request_history[0].path)
        self.assertEqual('new_name', req_data['name'])

    def test_env_update_wrong_attribute(self):
        env_id = 42
        self.assertRaises(error.ArgumentException,
                          self.client.update, env_id, id=43)

    def test_env_add_nodes(self):
        nodes = [25, 26]
        roles = ['cinder', 'compute']
        env_id = 42

        expected_body = []
        for n in nodes:
            expected_body.append({'id': n, 'roles': roles})

        expected_uri = self.get_object_uri(self.res_uri,
                                           env_id, '/assignment/')

        self.client.add_nodes(env_id, nodes, roles)

        self.assertEqual(rm.POST, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

        for assignment in self.session_adapter.last_request.json():
            # Check whether all assignments are expected
            self.assertIn(assignment, expected_body)
