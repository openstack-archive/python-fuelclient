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
from fuelclient.tests.utils import fake_network_group


@requests_mock.mock()
class TestNetworkGroupActions(base.UnitTestCase):

    def setUp(self):
        super(TestNetworkGroupActions, self).setUp()

        self.env_id = 42
        self.req_base_path = '/api/v1/networks/'

        self.ng = fake_network_group.get_fake_network_group()

    def test_list_network_groups(self, mreq):
        mget = mreq.get(self.req_base_path, json={})
        list_commands = [
            ['fuel', 'network-group', '--list'], ['fuel', 'network-group']]

        for cmd in list_commands:
            self.execute(cmd)
            self.assertTrue(mget.called)

    def test_list_network_groups_filtering(self, mreq):
        mget = mreq.get(self.req_base_path, json={})

        self.execute(
            ['fuel', 'network-group', '--node-group', str(self.ng['id'])]
        )

        self.assertTrue(mget.called)

    def create_network_group(self, mreq, cmd):
        mpost = mreq.post(self.req_base_path, json={
            'id': self.ng['id'],
            'name': self.ng['name'],
        })
        self.execute(cmd)

        call_data = mpost.last_request.json()
        self.assertEqual(self.ng['id'], call_data['group_id'])
        self.assertEqual(self.ng['name'], call_data['name'])

        self.assertTrue(mpost.called)

        return call_data

    def test_create_network_group(self, mreq):
        cmd = ['fuel', 'network-group', '--create', '--cidr', self.ng['cidr'],
               '--name', self.ng['name'], '--node-group', str(self.ng['id'])]
        self.create_network_group(mreq, cmd)

    def test_create_network_group_w_meta(self, mreq):
        cmd = ['fuel', 'network-group', '--create', '--cidr', self.ng['cidr'],
               '--name', self.ng['name'], '--node-group', str(self.ng['id']),
               '--meta', '{"ip_ranges": ["10.0.0.2", "10.0.0.254"]}']
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
        mdelete = mreq.delete(path, status_code=204)
        self.execute(
            ['fuel', 'network-group', '--delete',
             '--network', str(self.env_id)])

        self.assertTrue(mdelete.called)

    def test_network_group_duplicate_name(self, mreq):
        mpost = mreq.post(self.req_base_path, status_code=409)

        with mock.patch("sys.stderr") as m_stderr:
            with self.assertRaises(SystemExit):
                self.execute(
                    ['fuel', 'network-group', '--create', '--cidr',
                     self.ng['cidr'], '--name', self.ng['name'],
                     '--node-group', str(self.ng['id'])])

        self.assertIn("409 Client Error", m_stderr.write.call_args[0][0])
        self.assertTrue(mpost.called)

    def test_set_network_group(self, mreq):
        path = self.req_base_path + str(self.env_id) + '/'
        mput = mreq.put(path, json={})
        self.execute([
            'fuel', 'network-group', '--set', '--network', str(self.ng['id']),
            '--name', self.ng['name']])

        self.assertTrue(mput.called)

    def test_set_network_group_meta(self, mreq):
        path = self.req_base_path + str(self.env_id) + '/'
        mput = mreq.put(path, json={})
        self.execute([
            'fuel', 'network-group', '--set', '--network', str(self.ng['id']),
            '--meta', '{"ip_ranges": ["10.0.0.2", "10.0.0.254"]}'])

        self.assertTrue(mput.called)

        meta = mreq.last_request.json()['meta']
        self.assertEqual(meta['ip_ranges'], ["10.0.0.2", "10.0.0.254"])
