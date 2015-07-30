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
class TestNetworkGroupActions(base.UnitTestCase):

    def setUp(self):
        super(TestNetworkGroupActions, self).setUp()

        self.env_id = 42
        self.req_base_path = '/api/v1/networks/'

    def test_list_network_groups(self, mreq):
        mreq.get(self.req_base_path)
        list_commands = [
            ['fuel', 'network-group', '--list'], ['fuel', 'network-group']]

        for cmd in list_commands:
            self.execute(cmd)
            self.assertEqual(mreq.last_request.method, 'GET')
            self.assertEqual(mreq.last_request.path, self.req_base_path)

    def test_list_network_groups_filtering(self, mreq):
        mreq.get(self.req_base_path)

        self.execute(['fuel', 'network-group', '--node-group', '1'])

        self.assertEqual(mreq.last_request.method, 'GET')
        self.assertEqual(mreq.last_request.path, self.req_base_path)

    def create_network_group(self, mreq, cmd):
        mreq.post(self.req_base_path)
        self.execute(cmd)

        call_data = mreq.last_request.json()
        self.assertEqual(1, call_data['group_id'])
        self.assertEqual("test network", call_data['name'])

        self.assertEqual(mreq.last_request.method, 'POST')
        self.assertEqual(mreq.last_request.path, self.req_base_path)

        return call_data

    def test_create_network_group(self, mreq):
        cmd = ['fuel', 'network-group', '--create', '--cidr', '10.0.0.0/24',
               '--name', 'test network', '--node-group', '1']
        self.create_network_group(mreq, cmd)

    def test_create_network_group_w_meta(self, mreq):
        cmd = ['fuel', 'network-group', '--create', '--cidr', '10.0.0.0/24',
               '--name', 'test network', '--node-group', '1', '--meta',
               '{"ip_ranges": ["10.0.0.2", "10.0.0.254"]}']
        self.create_network_group(mreq, cmd)

        meta = mreq.last_request.json()['meta']
        self.assertEqual(meta['ip_ranges'], ["10.0.0.2", "10.0.0.254"])

    def test_create_network_group_required_args(self, mreq):
        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(
                    ['fuel', 'network-group', '--create'])

        self.assertIn('--nodegroup", "--name" and "--cidr" required!',
                      m_stderr.write.call_args[0][0])

    def test_delete_network_group_required_args(self, mreq):
        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(
                    ['fuel', 'network-group', '--delete'])

        self.assertIn('"--network" required!', m_stderr.write.call_args[0][0])

    def test_delete_network_group(self, mreq):
        path = self.req_base_path + str(self.env_id) + '/'
        mreq.delete(path)
        self.execute(
            ['fuel', 'network-group', '--delete',
             '--network', str(self.env_id)])

        self.assertEqual(mreq.last_request.method, 'DELETE')
        self.assertEqual(mreq.last_request.path, path)

    def test_network_group_duplicate_name(self, mreq):
        mreq.post(self.req_base_path, status_code=409)

        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(
                    ['fuel', 'network-group', '--create', '--cidr',
                     '10.0.0.0/24', '--name', 'test network', '--node-group',
                     '1'])

        self.assertIn("409 Client Error", m_stderr.write.call_args[0][0])
        self.assertEqual(mreq.last_request.method, 'POST')
        self.assertEqual(mreq.last_request.path, self.req_base_path)
