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
import requests_mock
from six import StringIO

from fuelclient.tests import base
from fuelclient.tests.utils import fake_env
from fuelclient.tests.utils import fake_network_group


@requests_mock.mock()
class TestNodeGroupActions(base.UnitTestCase):

    def setUp(self):
        super(TestNodeGroupActions, self).setUp()

        self.env = fake_env.get_fake_env(net_provider='neutron')
        self.req_base_path = '/api/v1/nodegroups/'
        self.ng = fake_network_group.get_fake_network_group()

    def test_list_nodegroups(self, mreq):
        mget = mreq.get(self.req_base_path, json=[])
        self.execute(['fuel', 'nodegroup', '--list'])

        self.assertTrue(mget.called)

    def test_create_nodegroup(self, mreq):
        neutron_url = \
            '/api/v1/clusters/{0}/network_configuration/neutron'.format(
                self.env['id']
            )

        mreq.get('/api/v1/clusters/{0}/'.format(self.env['id']), json={
            'id': self.env['id'],
            'net_provider': self.env['net_provider']
        })

        mreq.get('/api/v1/nodegroups/', json={})

        mpost = mreq.post(self.req_base_path, json={
            'id': self.ng['id'],
            'name': self.ng['name'],
        })
        mget = mreq.get(neutron_url, json={'networking_parameters': {}})
        with mock.patch('sys.stdout', new=StringIO()) as m_stdout:
            self.execute([
                'fuel', 'nodegroup', '--create',
                '--name', self.ng['name'], '--env', str(self.env['id'])
            ])

            msg = "Node group '{name}' with id={id} "\
                "in environment {cluster} was created!"
            self.assertIn(
                msg.format(cluster=self.env['id'], **self.ng),
                m_stdout.getvalue()
            )

        call_data = mpost.last_request.json()
        self.assertEqual(self.env['id'], call_data['cluster_id'])
        self.assertEqual(self.ng['name'], call_data['name'])

        self.assertTrue(mget.called)

    def _check_required_message_for_commands(self, err_msg, commands):
        for cmd in commands:
            with mock.patch("sys.stderr") as m_stderr:
                with self.assertRaises(SystemExit):
                    self.execute(cmd)

                m_stderr.write.assert_called_with(err_msg)

    def test_create_nodegroup_arguments_required(self, mreq):
        err_msg = '"--env" and "--name" required!\n'

        env_not_present = ['fuel', 'nodegroup', '--create',
                           '--name', 'test']

        name_not_present = ['fuel', '--env', str(self.env['id']),
                            'nodegroup', '--create']

        self._check_required_message_for_commands(
            err_msg, (env_not_present, name_not_present))

    def test_delete_nodegroup(self, mreq):
        path = self.req_base_path + str(self.env['id']) + '/'
        mget = mreq.get(path, json={'name': 'test group'})
        delete_path = self.req_base_path + str(self.env['id']) + '/'
        mdelete = mreq.delete(delete_path, status_code=204)
        ngid = self.env['id']
        with mock.patch('sys.stdout', new=StringIO()) as m_stdout:
            self.execute(['fuel', 'nodegroup', '--delete', '--group',
                         str(ngid)])
            msg = u"Node group with id={id} was deleted!"
            self.assertIn(
                msg.format(id=ngid),
                m_stdout.getvalue()
            )

        self.assertTrue(mget.called)
        self.assertTrue(mdelete.called)

    def test_delete_nodegroup_group_arg_required(self, mreq):
        err_msg = '"--group" required!\n'
        self._check_required_message_for_commands(
            err_msg,
            (['fuel', 'nodegroup', '--delete', '--default'],)
        )

    def test_assign_nodegroup_fails_w_multiple_groups(self, mreq):
        err_msg = "Nodes can only be assigned to one node group.\n"
        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(['fuel', 'nodegroup', '--assign', '--node', '1',
                              '--group', '2,3'])

        msg = m_stderr.write.call_args[0][0]
        self.assertEqual(msg, err_msg)

    @mock.patch('fuelclient.objects.nodegroup.NodeGroup.assign')
    def test_assign_nodegroup(self, m_req, m_assign):
        self.execute(['fuel', 'nodegroup', '--assign', '--node', '1',
                      '--group', '2'])
        m_assign.assert_called_with([1])

        self.execute(['fuel', 'nodegroup', '--assign', '--node', '1,2,3',
                      '--group', '2'])
        m_assign.assert_called_with([1, 2, 3])

    def test_node_group_assign_arguments_required(self, mreq):
        err_msg = '"--node" and "--group" required!\n'

        node_not_present_cmd = ['fuel', 'nodegroup', '--assign',
                                '--group', '1']
        group_not_present_cmd = ['fuel', 'nodegroup', '--assign',
                                 '--node', '1']

        commands = (node_not_present_cmd, group_not_present_cmd)

        self._check_required_message_for_commands(err_msg, commands)

    def test_create_nodegroup_with_existing_name(self, mreq):
        group_name = 'testgroup'
        mreq.get('/api/v1/nodegroups/', json=[{
            'cluster': self.env['id'],
            'id': 1,
            'name': group_name
        }])

        with mock.patch('sys.stderr') as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute([
                    'fuel', 'nodegroup', '--create',
                    '--name', group_name, '--env', str(self.env['id'])
                ])
            err_msg = "Error: nodegroup with name '{0}' already exists " \
                "in environment {1}.\n".format(group_name, self.env['id'])
            m_stderr.write.assert_called_with(err_msg)
