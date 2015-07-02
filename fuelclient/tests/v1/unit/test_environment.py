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

import cStringIO

import mock

from fuelclient.objects.environment import Environment
from fuelclient.tests import base


@mock.patch('requests.Response', new_callable=mock.MagicMock)
@mock.patch('requests.Session.delete')
@mock.patch('requests.Session.get')
@mock.patch('requests.Session.post')
class TestEnvironment(base.UnitTestCase):

    def test_delete_operational_wo_force(self, m_get, m_del, m_post, m_resp):
        m_resp.json.return_value = {'id': 1, 'status': 'operational'}
        m_get.return_value = m_resp

        with mock.patch('sys.stdout', new=cStringIO.StringIO()) as m_stdout:
            self.execute('fuel --env 1 env delete'.split())
            self.assertIn('--force', m_stdout.getvalue())

        self.assertEqual(0, m_del.call_count)

    def test_nova_network_using_warning(self, m_get, m_del, m_post, m_resp):
        m_resp.json.return_value = {'id': 1, 'name': 'test',
                                    'mode': 'ha_compact',
                                    'net_provider': 'neutron'}
        m_get.return_value = m_resp

        with mock.patch('sys.stdout', new=cStringIO.StringIO()) as m_stdout:
            self.execute(
                'fuel env create --name test --rel 1 --network-mode nova'
                .split()
            )
            self.assertIn('Warning: nova-network is '
                          'deprecated since 6.1 release.',
                          m_stdout.getvalue())


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

    @mock.patch('requests.Session')
    def test_get_deployment_tasks_with_end(self, mrequests):
        end = 'task1'
        self.env.get_deployment_tasks(end=end)
        kwargs = mrequests.get.call_args[1]
        self.assertEqual(kwargs['params'], {'start': None, 'end': 'task1'})
