# -*- coding: utf-8 -*-
#
#    Copyright 2014 Mirantis, Inc.
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
from six import moves

from fuelclient.objects.environment import Environment
from fuelclient.tests.unit.v1 import base


class TestEnvironment(base.UnitTestCase):

    def test_delete_operational_wo_force(self):
        cluster_id = 1
        url = '/api/v1/clusters/{0}/'.format(cluster_id)
        cmd = 'fuel --env {0} env delete'.format(cluster_id)

        self.m_request.get(url,
                           json={'id': cluster_id, 'status': 'operational'})
        m_delete = self.m_request.delete(url)

        with mock.patch('sys.stdout', new=moves.cStringIO()) as m_stdout:
            self.execute(cmd.split())
            self.assertIn('--force', m_stdout.getvalue())

        self.assertFalse(m_delete.called)

    def test_neutron_gre_using_warning(self):
        cluster_id = 1
        cluster_data = {
            'id': cluster_id,
            'name': 'test',
        }
        self.m_request.post('/api/v1/clusters/', json=cluster_data)
        self.m_request.get('/api/v1/clusters/{0}/'.format(cluster_id),
                           json=cluster_data)

        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.execute(
                'fuel env create --name test --rel 1 --nst gre'
                .split()
            )

        self.assertIn("WARNING: GRE network segmentation type is "
                      "deprecated since 7.0 release.",
                      m_stderr.getvalue())

    @mock.patch('fuelclient.objects.task.DeployTask.init_with_data')
    def test_deploy_changes(self, task_data):
        dry_run = False
        noop_run = False
        mdeploy = self.m_request.put('/api/v1/clusters/1/changes'
                                     '?dry_run={0}&noop_run={1}'.format(
                                         int(dry_run), int(noop_run)), json={})

        cmd = ['fuel', 'deploy-changes', '--env', '1']
        self.execute(cmd)
        self.check_deploy_redeploy_changes(dry_run, mdeploy)

    @mock.patch('fuelclient.objects.task.DeployTask.init_with_data')
    def test_deploy_changes_dry_run(self, task_data):
        dry_run = True
        mdeploy = self.m_request.put('/api/v1/clusters/1/changes'
                                     '?dry_run={0}'.format(
                                         int(dry_run)), json={})

        cmd = ['fuel', 'deploy-changes', '--env', '1']

        cmd.append('--dry-run')
        self.execute(cmd)
        self.check_deploy_redeploy_changes(dry_run, mdeploy)

    @mock.patch('fuelclient.objects.task.DeployTask.init_with_data')
    def test_redeploy_changes(self, task_data):
        dry_run = False
        mdeploy = self.m_request.put('/api/v1/clusters/1/changes/redeploy'
                                     '?dry_run={0}'.format(
                                         int(dry_run)), json={})

        cmd = ['fuel', 'redeploy-changes', '--env', '1']

        self.execute(cmd)
        self.check_deploy_redeploy_changes(dry_run, mdeploy)

    @mock.patch('fuelclient.objects.task.DeployTask.init_with_data')
    def test_redeploy_changes_dry_run(self, task_data):
        dry_run = True
        mdeploy = self.m_request.put('/api/v1/clusters/1/changes/redeploy'
                                     '?dry_run={0}'.format(
                                         int(dry_run)), json={})

        cmd = ['fuel', 'redeploy-changes', '--env', '1']

        cmd.append('--dry-run')
        self.execute(cmd)
        self.check_deploy_redeploy_changes(dry_run, mdeploy)

    def check_deploy_redeploy_changes(self, res, mdeploy, mode='dry_run'):
        self.assertEqual(mdeploy.last_request.qs[mode][0],
                         str(int(res)))


class TestEnvironmentOstf(base.UnitTestCase):

    def setUp(self):
        super(TestEnvironmentOstf, self).setUp()

        self.env = Environment(None)

    @mock.patch.object(Environment.connection, 'post_request', mock.Mock(
        return_value=[
            {'id': 1},
            {'id': 2}, ]))
    def test_run_test_sets(self):
        self.assertEqual(self.env._testruns_ids, [])

        testruns = self.env.run_test_sets(['sanity', 'ha'])

        self.assertEqual(len(testruns), 2)
        self.assertIn(1, self.env._testruns_ids)
        self.assertIn(2, self.env._testruns_ids)

    @mock.patch.object(Environment.connection, 'post_request')
    def test_credentials_are_passed_to_ostf(self, post_request):
        self.env.run_test_sets(['sanity'], {'tenant': 't1',
                                            'username': 'u1',
                                            'password': 'p1'})
        run_test_request = post_request.call_args[0][1]
        self.assertTrue(len(run_test_request) > 0, 'Got empty request')
        self.assertIn('metadata', run_test_request[0])
        self.assertIn('ostf_os_access_creds', run_test_request[0]['metadata'])
        creds = run_test_request[0]['metadata']['ostf_os_access_creds']
        self.assertEqual(creds['ostf_os_tenant_name'], 't1')
        self.assertEqual(creds['ostf_os_username'], 'u1')
        self.assertEqual(creds['ostf_os_password'], 'p1')

    @mock.patch.object(Environment.connection, 'get_request', mock.Mock(
        side_effect=[
            {'id': 1, 'status': 'running'},
            {'id': 2, 'status': 'finished'}, ]))
    def test_get_state_of_tests(self):
        self.env._testruns_ids.extend([1, 2])
        tests = self.env.get_state_of_tests()

        self.env.connection.get_request.assert_has_calls([
            mock.call('testruns/1', ostf=True),
            mock.call('testruns/2', ostf=True)])
        self.assertEqual(tests, [
            {'id': 1, 'status': 'running'},
            {'id': 2, 'status': 'finished'}])

    def test_get_deployment_tasks_with_end(self):
        end = 'task1'
        get = self.m_request.get(rm.ANY, json={})

        self.env.get_deployment_tasks(end=end)

        self.assertEqual(get.last_request.qs, {'end': ['task1']})

    def test_get_default_facts(self):
        legacy_format_facts = [
            {"uid": "1", "a": 1}, {"uid": "2", "a": 1}
        ]
        new_format_facts = [
            {"uid": "common", "a": 1}, {"uid": "1"}, {"uid": "2"}
        ]
        self.m_request.get(
            '/api/v1/clusters/{0}/orchestrator/deployment/defaults/?split=0'
            .format(self.env.id),
            json=legacy_format_facts
        )
        self.m_request.get(
            '/api/v1/clusters/{0}/orchestrator/deployment/defaults/?split=1'
            .format(self.env.id),
            json=new_format_facts
        )
        facts = self.env.get_default_facts("deployment", split=False)
        self.assertItemsEqual(legacy_format_facts, facts)
        facts = self.env.get_default_facts("deployment", split=True)
        self.assertItemsEqual(new_format_facts, facts)
