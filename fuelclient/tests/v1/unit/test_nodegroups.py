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

from fuelclient.tests import base


@requests_mock.mock()
class TestNodeGroupActions(base.UnitTestCase):

    def setUp(self):
        super(TestNodeGroupActions, self).setUp()

        self.env_id = 42
        self.req_base_path = '/api/v1/nodegroups/'

    def test_list_nodegroups(self, mreq):
        mreq.get(self.req_base_path)
        self.execute(['fuel', 'nodegroup', '--list'])
        self.assertEqual(mreq.last_request.method, 'GET')
        self.assertEqual(mreq.last_request.path, self.req_base_path)

    def test_create_nodegroup(self, mreq):
        mreq.post(self.req_base_path)
        self.execute(['fuel', 'nodegroup', '--create',
                      '--name', 'test group', '--env', str(self.env_id)])

        call_data = mreq.last_request.json()
        self.assertEqual(self.env_id, call_data['cluster_id'])
        self.assertEqual('test group', call_data['name'])

        self.assertEqual(mreq.last_request.method, 'POST')
        self.assertEqual(mreq.last_request.path, self.req_base_path)

    def test_delete_nodegroup(self, mreq):
        path = self.req_base_path + str(self.env_id) + '/'
        mreq.get(path, json={'name': 'test group'})
        delete_path = self.req_base_path + str(self.env_id) + '/'
        mreq.delete(delete_path)
        self.execute(['fuel', 'nodegroup', '--delete', '--group',
                      str(self.env_id)])
        self.assertEqual(mreq.request_history[-2].method, 'GET')
        self.assertEqual(mreq.request_history[-2].path, path)

        self.assertEqual(mreq.last_request.method, 'DELETE')
        self.assertEqual(mreq.last_request.path, delete_path)

    def test_assign_nodegroup_fails_w_multiple_groups(self, mreq):
        err_msg = "Nodes can only be assigned to one node group.\n"
        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(['fuel', 'nodegroup', '--assign', '--node', '1',
                              '--env', '1', '--group', '2,3'])

        msg = m_stderr.write.call_args[0][0]
        self.assertEqual(msg, err_msg)

    @mock.patch('fuelclient.objects.nodegroup.NodeGroup.assign')
    def test_assign_nodegroup(self, m_req, m_assign):
        self.execute(['fuel', 'nodegroup', '--assign', '--node', '1',
                      '--env', '1', '--group', '2'])
        m_assign.assert_called_with([1])

        self.execute(['fuel', 'nodegroup', '--assign', '--node', '1,2,3',
                      '--env', '1', '--group', '2'])
        m_assign.assert_called_with([1, 2, 3])
