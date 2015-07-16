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

import json
import re

import mock
import requests_mock as rm

import fuelclient
from fuelclient.cli import error
from fuelclient.objects import base as base_object
from fuelclient.objects import environment as env_object
from fuelclient.objects import task as task_object
from fuelclient.tests import utils
from fuelclient.tests.v2.unit.lib import test_api


class TestEnvFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestEnvFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/clusters/'.format(version=self.version)

        single_regexp = re.compile('{0}\d+/?$'.format(self.res_uri))

        fake_envs = [utils.get_fake_env() for i in range(5)]
        self.multiple_matcher = self.m_request.get(self.res_uri,
                                                   text=json.dumps(fake_envs))

        fake_env = utils.get_fake_env()
        self.single_matcher = self.m_request.get(single_regexp,
                                                 text=json.dumps(fake_env))

        self.client = fuelclient.get_client('environment', self.version)

    def test_env_list(self):
        self.client.get_all()

        self.assertEqual(self.res_uri, self.multiple_matcher.last_request.path)

    def test_env_show(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        self.client.get_by_id(env_id)

        self.assertEqual(expected_uri, self.single_matcher.last_request.path)

    def test_env_delete(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        matcher = self.m_request.delete(expected_uri, text='{}')

        self.client.delete_by_id(env_id)

        self.assertEqual(expected_uri, matcher.last_request.path)

    @mock.patch.object(env_object.Environment, 'init_with_data')
    def test_env_create(self, m_init):
        node_name = 'test_node'
        release_id = 20
        nst = 'gre'
        net = 'neutron'
        mode = 'ha_compact'

        fake_node = json.dumps(utils.get_fake_env())
        matcher = self.m_request.post(self.res_uri, text=fake_node)

        self.client.create(node_name, release_id, net, mode, nst)

        req_data = matcher.last_request.json()

        self.assertEqual(rm.POST, matcher.last_request.method)
        self.assertEqual(self.res_uri, matcher.last_request.path)

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
        matcher = self.m_request.put(expected_uri, text='{}')

        self.client.deploy_changes(env_id)

        self.assertEqual(expected_uri, matcher.last_request.path)

    @mock.patch.object(base_object.BaseObject, 'init_with_data')
    def test_env_upgrade(self, m_init):
        env_id = 42
        release_id = 10

        fake_env = json.dumps(utils.get_fake_env())
        expected = [(self.get_object_uri(self.res_uri, env_id), fake_env),
                    (self.get_object_uri(self.res_uri, env_id, '/update/'),
                     '{}')]

        matchers = [self.m_request.put(uri, text=text)
                    for uri, text in expected]

        self.client.upgrade(env_id, release_id)

        for i in range(len(expected)):
            matcher = matchers[i]
            expected_uri, _ = expected[i]
            self.assertEqual(expected_uri, matcher.last_request.path)

    @mock.patch.object(base_object.BaseObject, 'init_with_data')
    def test_env_update(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        fake_env = json.dumps(utils.get_fake_env())
        matcher = self.m_request.put(expected_uri, text=fake_env)

        self.client.update(env_id, name="new_name")
        req_data = matcher.last_request.json()

        self.assertEqual(expected_uri, matcher.last_request.path)
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

        matcher = self.m_request.post(expected_uri, text='{}')

        self.client.add_nodes(env_id, nodes, roles)

        self.assertEqual(expected_uri, matcher.last_request.path)

        for assignment in matcher.last_request.json():
            # Check whether all assignments are expected
            self.assertIn(assignment, expected_body)

    def test_env_spawn_vms(self):
        env_id = 10
        expected_uri = '/api/v1/clusters/{0}/spawn_vms/'.format(env_id)

        matcher = self.m_request.put(expected_uri, text='{}')

        self.client.spawn_vms(env_id)

        self.assertEqual(expected_uri, matcher.last_request.path)
