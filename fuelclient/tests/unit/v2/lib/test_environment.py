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

import fuelclient
from fuelclient.cli import error
from fuelclient.objects import base as base_object
from fuelclient.objects import environment as env_object
from fuelclient.objects import task as task_object
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestEnvFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestEnvFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/clusters/'.format(version=self.version)

        self.fake_env = utils.get_fake_env()
        self.fake_envs = [utils.get_fake_env() for i in range(10)]

        self.client = fuelclient.get_client('environment', self.version)

    def test_env_list(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_envs)
        self.client.get_all()

        self.assertTrue(matcher.called)

    def test_env_show(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        matcher = self.m_request.get(expected_uri, json=self.fake_env)

        self.client.get_by_id(env_id)

        self.assertTrue(matcher.called)

    def test_env_delete(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        matcher = self.m_request.delete(expected_uri, json={})

        self.client.delete_by_id(env_id)

        self.assertTrue(matcher.called)

    @mock.patch.object(env_object.Environment, 'init_with_data')
    def test_env_create(self, m_init):
        env_name = self.fake_env['name']
        release_id = self.fake_env['release_id']
        nst = 'vlan'

        matcher = self.m_request.post(self.res_uri, json=self.fake_env)

        self.client.create(name=env_name,
                           release_id=release_id,
                           net_segment_type=nst)

        req_data = matcher.last_request.json()

        self.assertTrue(matcher.called)

        self.assertEqual(release_id, req_data['release_id'])
        self.assertEqual(env_name, req_data['name'])
        self.assertEqual(nst, req_data['net_segment_type'])

    def test_env_create_bad_nst_neutron(self):
        node_name = 'test_node'
        release_id = 20
        nst = 'bad'

        self.assertRaises(error.BadDataException,
                          self.client.create,
                          node_name, release_id, nst)

    def test_env_create_neutron_tun(self):
        env = utils.get_fake_env()
        env_name = env['name']
        release_id = env['release_id']
        nst = env['net_segment_type'] = 'tun'

        matcher = self.m_request.post(self.res_uri, json=env)

        self.client.create(name=env_name,
                           release_id=release_id,
                           net_segment_type=nst)

        req_data = matcher.last_request.json()

        self.assertEqual(release_id, req_data['release_id'])
        self.assertEqual(env_name, req_data['name'])
        self.assertEqual(nst, req_data['net_segment_type'])

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/changes')
        matcher = self.m_request.put(expected_uri, json={})
        dry_run = False
        noop = False

        self.client.deploy_changes(env_id, dry_run=dry_run, noop=noop)
        self.check_deploy_redeploy_changes(dry_run, matcher, noop)

    def check_deploy_redeploy_changes(self, dry_run, matcher, noop):
        self.assertTrue(matcher.called)
        self.assertEqual(matcher.last_request.qs['dry_run'][0],
                         str(int(dry_run)))
        self.assertEqual(matcher.last_request.qs['noop'][0],
                         str(int(noop)))

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy_dry_run(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/changes')
        matcher = self.m_request.put(expected_uri, json={})

        dry_run = True
        noop = False

        self.client.deploy_changes(env_id, dry_run=dry_run, noop=noop)
        self.check_deploy_redeploy_changes(dry_run, matcher, noop)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy_noop(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/changes')
        matcher = self.m_request.put(expected_uri, json={})

        dry_run = False
        noop = True

        self.client.deploy_changes(env_id, dry_run=dry_run, noop=noop)
        self.check_deploy_redeploy_changes(dry_run, matcher, noop)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy_noop_dry_run(self, m_init):
        env_id = 42

        dry_run = True
        noop = True

        self.assertRaises(error.ActionException, self.client.deploy_changes,
                          env_id, dry_run=dry_run, noop=noop)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/changes/redeploy')
        matcher = self.m_request.put(expected_uri, json={})
        dry_run = False
        noop = False

        self.client.redeploy_changes(env_id, dry_run=dry_run, noop=noop)
        self.check_deploy_redeploy_changes(dry_run, matcher, noop)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy_dry_run(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/changes/redeploy')
        matcher = self.m_request.put(expected_uri, json={})

        dry_run = True
        noop = False

        self.client.redeploy_changes(env_id, dry_run=dry_run, noop=noop)
        self.check_deploy_redeploy_changes(dry_run, matcher, noop)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy_noop(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/changes/redeploy')
        matcher = self.m_request.put(expected_uri, json={})

        dry_run = False
        noop = True

        self.client.redeploy_changes(env_id, dry_run=dry_run, noop=noop)
        self.check_deploy_redeploy_changes(dry_run, matcher, noop)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy_noop_dry_run(self, m_init):
        env_id = 42

        dry_run = True
        noop = True

        self.assertRaises(error.ActionException, self.client.redeploy_changes,
                          env_id, dry_run=dry_run, noop=noop)

    @mock.patch.object(base_object.BaseObject, 'init_with_data')
    def test_env_update(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id)

        get_matcher = self.m_request.get(expected_uri, json=self.fake_env)
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_env)

        self.client.update(env_id, name="new_name")

        self.assertTrue(expected_uri, get_matcher.called)
        self.assertTrue(expected_uri, upd_matcher.called)

        req_data = upd_matcher.last_request.json()
        self.assertEqual('new_name', req_data['name'])

    def test_env_update_wrong_attribute(self):
        env_id = 42
        self.assertRaises(error.BadDataException,
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

        matcher = self.m_request.post(expected_uri, json={})

        self.client.add_nodes(env_id, nodes, roles)

        self.assertTrue(matcher.called)

        for assignment in matcher.last_request.json():
            # Check whether all assignments are expected
            self.assertIn(assignment, expected_body)

    def test_env_spawn_vms(self):
        env_id = 10
        expected_uri = '/api/v1/clusters/{0}/spawn_vms/'.format(env_id)

        matcher = self.m_request.put(expected_uri, json={})

        self.client.spawn_vms(env_id)

        self.assertTrue(matcher.called)
