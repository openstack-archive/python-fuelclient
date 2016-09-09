# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api


class TestDeploymentSequence(test_api.BaseLibTest):

    def setUp(self):
        super(TestDeploymentSequence, self).setUp()
        self.version = 'v1'
        self.client = fuelclient.get_client('sequence', self.version)
        self.env_id = 1
        self.sequence_body = {
            'id': 1, 'release_id': 1, 'name': 'test',
            'graphs': [{'type': 'graph1'}]
        }

    def _check_sequence_object(self, sequence):
        self.assertEqual(self.sequence_body, sequence)

    def test_create(self):
        matcher_post = self.m_request.post(
            '/api/v1/sequences/', json=self.sequence_body
        )
        sequence = self.client.create(1, name='test', graph_types=['graph1'])
        self.assertTrue(matcher_post.called)
        self._check_sequence_object(sequence)

    def test_update(self):
        matcher_put = self.m_request.put(
            '/api/v1/sequences/1/', json=self.sequence_body
        )
        sequence = self.client.update(1, name='test')
        self.assertTrue(matcher_put.called)
        self.assertEqual('{"name": "test"}', matcher_put.last_request.body)
        self._check_sequence_object(sequence)

    def test_delete(self):
        mathcher_delete = self.m_request.delete(
            '/api/v1/sequences/1/', status_code=204
        )
        self.client.delete_by_id(1)
        self.assertTrue(mathcher_delete.called)

    def test_get_one(self):
        matcher_get = self.m_request.get(
            '/api/v1/sequences/1/', json=self.sequence_body
        )
        sequence = self.client.get_by_id(1)
        self.assertTrue(matcher_get.called)
        self.assertEqual('test', sequence['name'])
        self.assertEqual('graph1', sequence['graphs'])

    def test_get_all(self):
        matcher_get = self.m_request.get(
            '/api/v1/sequences/?release=1', json=[self.sequence_body]
        )
        sequences = self.client.get_all(release=1)
        self.assertTrue(matcher_get.called)
        self.assertEqual(1, len(sequences))
        self._check_sequence_object(sequences[0])

    def test_execute(self):
        self.m_request.get('/api/v1/nodes/?cluster_id=2', json=[])
        self.m_request.get('/api/v1/cluster/2', json={'id': 2})

        matcher_post = self.m_request.post(
            '/api/v1/sequences/1/execute/', json={'id': 10, 'cluster': 2}
        )
        self.client.execute(1, 2, dry_run=True, noop_run=False)
        self.assertTrue(matcher_post.called)
        self.assertIn('"cluster": 2', matcher_post.last_request.body)
        self.assertIn('"noop_run": false', matcher_post.last_request.body)
        self.assertIn('"dry_run": true', matcher_post.last_request.body)

    def test_upload(self):
        matcher_post = self.m_request.post(
            '/api/v1/sequences/', json=self.sequence_body
        )
        sequence = self.client.upload(1, self.sequence_body)
        self.assertTrue(matcher_post.called)
        self._check_sequence_object(sequence)

    def test_download(self):
        matcher_get = self.m_request.get(
            '/api/v1/sequences/1/', json=self.sequence_body
        )
        sequence = self.client.download(1)
        self.assertTrue(matcher_get.called)
        self._check_sequence_object(sequence)
