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
from fuelclient.objects import fuelversion as fuelversion_object
from fuelclient.objects import task as task_object
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestEnvFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestEnvFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/clusters/'.format(version=self.version)
        self.net_conf_uri = '/network_configuration/neutron'
        self.settings_uri = '/attributes'
        self.net_verify_uri = '/network_configuration/neutron/verify'

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

        self.client.deploy_changes(env_id, dry_run=dry_run)
        self.check_deploy_redeploy_changes(dry_run, matcher)

    def check_deploy_redeploy_changes(self, res, matcher, mode='dry_run'):
        self.assertTrue(matcher.called)
        self.assertEqual(matcher.last_request.qs[mode][0], str(int(res)))

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy_dry_run(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/changes')
        matcher = self.m_request.put(expected_uri, json={})

        dry_run = True

        self.client.deploy_changes(env_id, dry_run=dry_run)
        self.check_deploy_redeploy_changes(dry_run, matcher)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_deploy_noop_run(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/changes')
        matcher = self.m_request.put(expected_uri, json={})

        noop_run = True

        self.client.deploy_changes(env_id, noop_run=noop_run)
        self.check_deploy_redeploy_changes(noop_run, matcher, mode='noop_run')

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/changes/redeploy')
        matcher = self.m_request.put(expected_uri, json={})
        dry_run = False

        self.client.redeploy_changes(env_id, dry_run=dry_run)
        self.check_deploy_redeploy_changes(dry_run, matcher)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy_dry_run(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/changes/redeploy')
        matcher = self.m_request.put(expected_uri, json={})

        dry_run = True

        self.client.redeploy_changes(env_id, dry_run=dry_run)
        self.check_deploy_redeploy_changes(dry_run, matcher)

    @mock.patch.object(task_object.DeployTask, 'init_with_data')
    def test_env_redeploy_noop_run(self, m_init):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/changes/redeploy')
        matcher = self.m_request.put(expected_uri, json={})

        noop_run = True

        self.client.redeploy_changes(env_id, noop_run=noop_run)
        self.check_deploy_redeploy_changes(noop_run, matcher, mode='noop_run')

    def test_env_reset(self):
        env_id = 42
        force = False
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/reset/')

        matcher = self.m_request.put(expected_uri, json=utils.get_fake_task())

        self.client.reset(env_id, force=force)

        self.assertTrue(matcher.called)
        self.assertEqual(matcher.last_request.qs['force'][0], str(int(force)))

    def test_env_reset_force(self):
        env_id = 42
        force = True
        expected_uri = self.get_object_uri(self.res_uri, env_id, '/reset/')

        matcher = self.m_request.put(expected_uri, json=utils.get_fake_task())

        self.client.reset(env_id, force=force)

        self.assertTrue(matcher.called)
        self.assertEqual(matcher.last_request.qs['force'][0], str(int(force)))

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

    @mock.patch.object(fuelversion_object.FuelVersion, 'get_feature_groups')
    def test_env_spawn_vms(self, m_feature_groups):
        env_id = 10
        expected_uri = '/api/v1/clusters/{0}/spawn_vms/'.format(env_id)
        m_feature_groups.return_value = \
            utils.get_fake_fuel_version()['feature_groups']

        matcher = self.m_request.put(expected_uri, json={})

        self.client.spawn_vms(env_id)

        self.assertTrue(matcher.called)

    def test_env_stop(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_uri, env_id,
                                           '/stop_deployment/')

        matcher = self.m_request.put(expected_uri, json=utils.get_fake_task())

        self.client.stop(env_id)

        self.assertTrue(matcher.called)

    def test_env_remove_nodes_by_id(self):
        nodes = [25, 26]
        env_id = 42

        expected_body = []
        for n in nodes:
            expected_body.append({'id': n})

        expected_uri = self.get_object_uri(self.res_uri,
                                           env_id, '/unassignment/')

        matcher = self.m_request.post(expected_uri, json={})

        self.client.remove_nodes(env_id, nodes=nodes)

        self.assertTrue(matcher.called)

        for unassignment in matcher.last_request.json():
            # Check whether all unassignments are expected
            self.assertIn(unassignment, expected_body)

    def test_env_remove_nodes_all(self):
        nodes = [24, 25, 26]
        env_id = 42

        expected_body = []
        for n in nodes:
            expected_body.append({'id': n})

        fake_nodes = [utils.get_fake_node(node_name='node_' + str(n),
                                          node_id=n,
                                          cluster=env_id) for n in nodes]

        expected_uri = self.get_object_uri(self.res_uri,
                                           env_id, '/unassignment/')
        matcher_get = self.m_request.get(
            '/api/v1/nodes/?cluster_id={}'.format(env_id),
            json=fake_nodes
        )
        matcher_post = self.m_request.post(expected_uri, json={})
        self.client.remove_nodes(env_id)
        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_post.called)

        for unassignment in matcher_post.last_request.json():
            # Check whether all unassignments are expected
            self.assertIn(unassignment, expected_body)

    def test_env_deploy_nodes(self):
        env_id = 42
        node_ids = [43, 44]

        expected_url = self.get_object_uri(self.res_uri, env_id, '/deploy/')
        matcher = self.m_request.put(expected_url, json=utils.get_fake_task())

        self.client.deploy_nodes(env_id, node_ids)

        self.assertTrue(matcher.called)
        self.assertEqual([','.join(str(i) for i in node_ids)],
                         matcher.last_request.qs['nodes'])

    def test_env_deploy_nodes_force(self):
        env_id = 42
        node_ids = [43, 44]
        force = True

        expected_url = self.get_object_uri(self.res_uri, env_id, '/deploy/')
        matcher = self.m_request.put(expected_url, json=utils.get_fake_task())

        self.client.deploy_nodes(env_id, node_ids, force=force)

        self.assertTrue(matcher.called)
        self.assertEqual([','.join(str(i) for i in node_ids)],
                         matcher.last_request.qs['nodes'])
        self.assertEqual(matcher.last_request.qs['force'][0], str(int(force)))

    def test_env_deploy_nodes_noop_run(self):
        env_id = 42
        node_ids = [43, 44]
        noop_run = True

        expected_url = self.get_object_uri(self.res_uri, env_id, '/deploy/')
        matcher = self.m_request.put(expected_url, json=utils.get_fake_task())

        self.client.deploy_nodes(env_id, node_ids, noop_run=noop_run)

        self.assertTrue(matcher.called)
        self.assertEqual([','.join(str(i) for i in node_ids)],
                         matcher.last_request.qs['nodes'])
        self.assertEqual(matcher.last_request.qs['noop_run'][0],
                         str(int(noop_run)))

    def test_env_provision_nodes(self):
        env_id = 42
        node_ids = [43, 44]

        expected_url = self.get_object_uri(self.res_uri, env_id, '/provision/')
        matcher = self.m_request.put(expected_url, json=utils.get_fake_task())

        self.client.provision_nodes(env_id, node_ids)

        self.assertTrue(matcher.called)
        self.assertEqual([','.join(str(i) for i in node_ids)],
                         matcher.last_request.qs['nodes'])

    def test_env_network_verify(self):
        env_id = 42
        fake_env = utils.get_fake_env(env_id=env_id)
        test_conf = utils.get_fake_env_network_conf()

        env_uri = self.get_object_uri(self.res_uri, env_id)
        download_uri = self.get_object_uri(self.res_uri,
                                           env_id,
                                           self.net_conf_uri)
        verify_uri = self.get_object_uri(self.res_uri,
                                         env_id,
                                         self.net_verify_uri)

        m_get = self.m_request.get(env_uri, json=fake_env)
        m_download = self.m_request.get(download_uri, json=test_conf)
        m_verify = self.m_request.put(verify_uri, json=utils.get_fake_task())

        self.client.verify_network(env_id)

        self.assertTrue(m_get.called)
        self.assertTrue(m_download.called)
        self.assertTrue(m_verify.called)
        self.assertEqual(test_conf, m_verify.last_request.json())

    def test_env_network_download(self):
        env_id = 42
        fake_env = utils.get_fake_env(env_id=env_id)
        env_uri = self.get_object_uri(self.res_uri, env_id)
        download_uri = self.get_object_uri(self.res_uri,
                                           env_id,
                                           self.net_conf_uri)
        test_conf = utils.get_fake_env_network_conf()

        m_get = self.m_request.get(env_uri, json=fake_env)
        m_download = self.m_request.get(download_uri, json=test_conf)

        net_conf = self.client.get_network_configuration(env_id)

        self.assertEqual(test_conf, net_conf)
        self.assertTrue(m_get.called)
        self.assertTrue(m_download.called)

    def test_env_network_upload(self):
        env_id = 42
        fake_env = utils.get_fake_env(env_id=env_id)
        env_uri = self.get_object_uri(self.res_uri, env_id)
        upload_uri = self.get_object_uri(self.res_uri,
                                         env_id,
                                         self.net_conf_uri)
        test_conf = utils.get_fake_env_network_conf()

        m_get = self.m_request.get(env_uri, json=fake_env)
        m_upload = self.m_request.put(upload_uri, json={})

        self.client.set_network_configuration(env_id, test_conf)

        self.assertTrue(m_get.called)
        self.assertTrue(m_upload.called)
        self.assertEqual(test_conf, m_upload.last_request.json())

    def test_env_settings_download(self):
        env_id = 42
        download_uri = self.get_object_uri(self.res_uri,
                                           env_id,
                                           self.settings_uri)
        test_settings = {'test-data': 42}

        m_download = self.m_request.get(download_uri, json=test_settings)

        settings = self.client.get_settings(env_id)

        self.assertEqual(test_settings, settings)
        self.assertTrue(m_download.called)

    def test_env_settings_upload(self):
        env_id = 42
        upload_uri = self.get_object_uri(self.res_uri,
                                         env_id,
                                         self.settings_uri)
        test_settings = {'test-data': 42}

        m_upload = self.m_request.put(upload_uri, json={})

        self.client.set_settings(env_id, test_settings)

        self.assertTrue(m_upload.called)
        self.assertEqual(test_settings, m_upload.last_request.json())

    def test_env_settings_upload_force(self):
        env_id = 42
        upload_uri = self.get_object_uri(self.res_uri,
                                         env_id,
                                         self.settings_uri)
        test_settings = {'test-data': 42}

        m_upload = self.m_request.put(upload_uri, json={})

        self.client.set_settings(env_id, test_settings, force=True)

        self.assertTrue(m_upload.called)
        self.assertEqual(test_settings, m_upload.last_request.json())
        self.assertEqual(['1'], m_upload.last_request.qs.get('force'))

    def test_delete_facts(self):
        env_id = 42
        fact_type = 'deployment'
        expected_uri = self.get_object_uri(
            self.res_uri,
            env_id,
            '/orchestrator/{fact_type}/'.format(fact_type=fact_type))

        matcher = self.m_request.delete(expected_uri, json={})
        self.client.delete_facts(env_id, fact_type)
        self.assertTrue(matcher.called)
        self.assertIsNone(matcher.last_request.body)

    def test_download_facts(self):
        env_id = 42
        fact_type = 'deployment'
        nodes = [2, 5]
        expected_uri = self.get_object_uri(
            self.res_uri,
            env_id,
            "/orchestrator/{fact_type}/?nodes={nodes}".format(
                fact_type=fact_type, nodes=",".join(map(str, nodes))))
        fake_resp = {'foo': 'bar'}

        matcher = self.m_request.get(expected_uri, json=fake_resp)
        facts = self.client.download_facts(
            env_id, fact_type, nodes=nodes, default=False)
        self.assertTrue(matcher.called)
        self.assertIsNone(matcher.last_request.body)
        self.assertEqual(facts, fake_resp)

    def test_upload_facts(self):
        env_id = 42
        fact_type = 'deployment'
        facts = {'foo': 'bar'}
        expected_uri = self.get_object_uri(
            self.res_uri,
            env_id,
            "/orchestrator/{fact_type}/".format(fact_type=fact_type))

        matcher = self.m_request.put(expected_uri, json={})
        self.client.upload_facts(env_id, fact_type, facts)
        self.assertTrue(matcher.called)
        self.assertEqual(facts, matcher.last_request.json())
