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

from fuelclient.tests import base


@mock.patch('fuelclient.client.requests')
class TestNodeGroupActions(base.UnitTestCase):

    def test_list_nodegroups(self, mreq):
        self.execute(['fuel', 'nodegroup', '--list'])
        call_args = mreq.get.call_args_list[-1]
        url = call_args[0][0]
        self.assertIn('nodegroups/', url)

    def test_create_nodegroup(self, mreq):
        self.execute(['fuel', 'nodegroup', '--create',
                      '--name', 'test group', '--env', '1'])

        call_args = mreq.post.call_args_list[0]
        url = call_args[0][0]
        self.assertIn('nodegroups/', url)

    def test_delete_nodegroup(self, mreq):
        self.execute(['fuel', 'nodegroup', '--delete', '--group', '3'])
        call_args = mreq.delete.call_args_list[-1]
        url = call_args[0][0]
        self.assertIn('nodegroups/3', url)

    def test_assign_nodegroup_fails_w_multiple_groups(self, mreq):
        err_msg = "Nodes can only be assigned to one node group.\n"
        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(['fuel', 'nodegroup', '--assign', '--node', '1',
                              '--env', '1', '--group', '2,3'])

        msg = m_stderr.write.call_args[0][0]
        self.assertEqual(msg, err_msg)

    @mock.patch('fuelclient.objects.nodegroup.NodeGroup.assign')
    def test_assign_nodegroup(self, m_assign, mreq):
        self.execute(['fuel', 'nodegroup', '--assign', '--node', '1',
                      '--env', '1', '--group', '2'])
        m_assign.assert_called_with([1])

        self.execute(['fuel', 'nodegroup', '--assign', '--node', '1,2,3',
                      '--env', '1', '--group', '2'])
        m_assign.assert_called_with([1, 2, 3])
