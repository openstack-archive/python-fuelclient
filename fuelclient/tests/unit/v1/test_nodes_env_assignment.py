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
from six import moves

from fuelclient.tests.unit.v1 import base
from fuelclient.tests.utils import fake_env
from fuelclient.tests.utils import get_fake_node


# Test cases:
#
#     Add nodes to the environment
#         fuel --env 1 node set --node 1 --role controller
#         fuel --env 1 node set --node 2,3,4 --role compute,cinder
#
#     Remove some nodes from environment:
#         fuel --env 1 node remove --node 2,3
#
#     Remove nodes no matter to which environment they were assigned:
#         fuel node remove --node 2,3,6,7
#
#     Remove all nodes from some environment:
#         fuel --env 1 node remove --all


class TestNodesEnvAssignment(base.UnitTestCase):
    roles = ['cinder', 'compute']
    env = fake_env.get_fake_env(env_id=42)
    nodesets = [[24], [25, 26, 27]]
    second_env = fake_env.get_fake_env(env_id=777)
    second_env_nodset = [725, 726]

    def setUp(self):
        super(TestNodesEnvAssignment, self).setUp()
        self.m_request.get(
            '/api/v1/clusters/{0}/'.format(self.env['id']),
            json=self.env)

    def test_assign_environment(self):
        assign_req = self.m_request.post(
            '/api/v1/clusters/{0}/assignment/'.format(self.env['id']),
            json={})

        for nodeset in self.nodesets:
            with mock.patch('sys.stdout',
                            new=moves.cStringIO()) as m_stdout:
                self.execute(
                    ['fuel', '--env', str(self.env['id']), 'node',
                     'set', '--node',
                     ",".join([str(n) for n in nodeset]),
                     '--role',
                     ",".join(self.roles)])

                resp = assign_req.last_request.json()
                self.assertEqual(len(nodeset), len(resp))
                for lsi, ls in enumerate(nodeset):
                    self.assertEqual(nodeset[lsi], resp[lsi]['id'])
                    self.assertItemsEqual(
                        self.roles,
                        resp[lsi]['roles'])

                self.assertIn(
                    "Nodes {n} with roles ".format(n=nodeset),
                    m_stdout.getvalue()
                )
                self.assertIn(
                    " were added to environment {e}".format(
                        e=self.env['id']),
                    m_stdout.getvalue()
                )
                for r in self.roles:
                    self.assertIn(r, m_stdout.getvalue())

    def test_remove_from_environment(self):
        unassign_req = self.m_request.post(
            '/api/v1/clusters/{0}/unassignment/'.format(self.env['id']),
            json={})

        for nodeset in self.nodesets:
            with mock.patch('sys.stdout',
                            new=moves.cStringIO()) as m_stdout:
                self.execute(
                    ['fuel', '--env', str(self.env['id']), 'node',
                     'remove', '--node',
                     ",".join([str(n) for n in nodeset])]
                )

                resp = unassign_req.last_request.json()
                self.assertEqual(len(nodeset), len(resp))
                self.assertItemsEqual(nodeset, [r['id'] for r in resp])
                self.assertIn(
                    "Nodes with ids {n} were removed "
                    "from environment with id {e}.".format(
                        n=nodeset, e=self.env['id']),
                    m_stdout.getvalue()
                )

    def test_remove_wo_environment(self):
        # fixme: introduce ddt or the similar fixture data
        # sourcing solution to avoid further copy-paste
        for nodeset in self.nodesets:
            self.m_request.get(
                '/api/v1/nodes/',
                json=[get_fake_node(cluster=self.env['id'], node_id=nid)
                      for nid in nodeset]
            )
            for nid in nodeset:
                self.m_request.get(
                    '/api/v1/nodes/{0}/'.format(nid),
                    json=get_fake_node(cluster=self.env['id'],
                                       node_id=nid)
                )
            mpost = self.m_request.post(
                '/api/v1/clusters/{0}/unassignment/'.format(
                    self.env['id']), json={})
            with mock.patch('sys.stdout',
                            new=moves.cStringIO()) as m_stdout:
                self.execute(
                    ['fuel', 'node', 'remove', '--node',
                     ",".join([str(n) for n in nodeset])]
                )

                resp = mpost.last_request.json()
                self.assertItemsEqual(nodeset, [r['id'] for r in resp])
                self.assertIn(
                    "Nodes with ids {n} were removed "
                    "from environment with id {e}.".format(
                        n=nodeset, e=self.env['id']),
                    m_stdout.getvalue()
                )

    def test_remove_wo_environment_mixed(self):
        # fixme: introduce ddt or the similar fixture data
        # sourcing solution to avoid further copy-paste
        for nodeset in self.nodesets:
            self.m_request.get(
                '/api/v1/nodes/',
                json=[get_fake_node(cluster=self.env['id'], node_id=nid)
                      for nid in nodeset]
            )
            for nid in nodeset:
                self.m_request.get(
                    '/api/v1/nodes/{0}/'.format(nid),
                    json=get_fake_node(cluster=self.env['id'],
                                       node_id=nid)
                )
            for nid in self.second_env_nodset:
                self.m_request.get(
                    '/api/v1/nodes/{0}/'.format(nid),
                    json=get_fake_node(cluster=self.second_env['id'],
                                       node_id=nid)
                )
            mpost = self.m_request.post(
                '/api/v1/clusters/{0}/unassignment/'.format(
                    self.env['id']), json={})
            mpost_second = self.m_request.post(
                '/api/v1/clusters/{0}/unassignment/'.format(
                    self.second_env['id']), json={})
            with mock.patch('sys.stdout',
                            new=moves.cStringIO()) as m_stdout:
                merged_nodeset = nodeset[:]
                merged_nodeset.extend(self.second_env_nodset)
                self.execute(
                    ['fuel', 'node', 'remove', '--node',
                     ",".join([str(n) for n in merged_nodeset])]
                )

                resp = mpost.last_request.json()
                self.assertItemsEqual(nodeset, [r['id'] for r in resp])

                resp_second = mpost_second.last_request.json()
                self.assertItemsEqual(self.second_env_nodset,
                                      [r['id'] for r in resp_second])

                self.assertIn(
                    "Nodes with ids {n} were removed from "
                    "environment with id {e}.".format(
                        n=nodeset, e=self.env['id']),
                    m_stdout.getvalue()
                )
                self.assertIn(
                    "Nodes with ids {n} were removed from "
                    "environment with id {e}.".format(
                        n=self.second_env_nodset, e=self.second_env['id']),
                    m_stdout.getvalue()
                )

    def test_remove_all_from_environment(self):
        for nodeset in self.nodesets:
            self.m_request.get(
                '/api/v1/nodes/',
                json=[get_fake_node(cluster=self.env['id'], node_id=nid)
                      for nid in nodeset]
            )
            mpost = self.m_request.post(
                '/api/v1/clusters/{0}/unassignment/'.format(
                    self.env['id']), json={})
            with mock.patch('sys.stdout',
                            new=moves.cStringIO()) as m_stdout:
                self.execute(
                    ['fuel', '--env', str(self.env['id']), 'node',
                     'remove', '--all'])

                resp = mpost.last_request.json()
                self.assertItemsEqual(nodeset, [r['id'] for r in resp])
                self.assertIn(
                    "All nodes from environment "
                    "with id {e} were removed.".format(
                        e=self.env['id']),
                    m_stdout.getvalue()
                )
