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

import mock
import yaml

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


TASKS_YAML = '''- id: custom-task-1
  type: puppet
  parameters:
    param: value
- id: custom-task-2
  type: puppet
  parameters:
    param: value
'''


class TestDeploymentGraphFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestDeploymentGraphFacade, self).setUp()
        self.version = 'v1'
        self.client = fuelclient.get_client('graph', self.version)
        self.env_id = 1

    def test_existing_graph_upload(self):
        expected_body = {
            'tasks': yaml.load(TASKS_YAML)}

        matcher_post = self.m_request.post(
            '/api/v1/clusters/1/deployment_graphs/custom_graph',
            json=expected_body)

        matcher_get = self.m_request.get(
            '/api/v1/clusters/1/deployment_graphs/custom_graph',
            status_code=404,
            json={'status': 'error', 'message': 'Does not exist'})

        m_open = mock.mock_open(read_data=TASKS_YAML)
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True):
            self.client.upload(
                data=expected_body,
                related_model='clusters',
                related_id=1,
                graph_type='custom_graph'
            )

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_post.called)
        self.assertItemsEqual(
            expected_body,
            matcher_post.last_request.json()
        )

    def test_new_graph_upload(self):
        expected_body = {
            'tasks': yaml.load(TASKS_YAML)}

        matcher_put = self.m_request.put(
            '/api/v1/clusters/1/deployment_graphs/custom_graph',
            json=expected_body)

        matcher_get = self.m_request.get(
            '/api/v1/clusters/1/deployment_graphs/custom_graph',
            status_code=200,
            json={
                'tasks': [{'id': 'imatask', 'type': 'puppet'}]
            })

        m_open = mock.mock_open(read_data=TASKS_YAML)
        with mock.patch(
                'fuelclient.cli.serializers.open', m_open, create=True):
            self.client.upload(
                data=expected_body,
                related_model='clusters',
                related_id=1,
                graph_type='custom_graph')

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertItemsEqual(
            expected_body,
            matcher_put.last_request.json()
        )

    def test_new_graph_run_wo_params(self):
        matcher_execute = self.m_request.post(
            '/api/v1/graphs/execute/',
            json=utils.fake_task.get_fake_task(cluster=370))
        # this is required to form running task info
        self.m_request.get(
            '/api/v1/nodes/?cluster_id=370',
            json={}
        )
        self.client.execute(env_id=1)
        self.assertEqual(
            matcher_execute.last_request.json(),
            {
                'cluster': 1
            }
        )

    def test_new_graph_run_with_parameters(self):
        matcher_execute = self.m_request.post(
            '/api/v1/graphs/execute/',
            json=utils.fake_task.get_fake_task(cluster=370))
        # this is required to form running task info
        self.m_request.get(
            '/api/v1/nodes/?cluster_id=370',
            json={}
        )
        self.client.execute(
            env_id=1,
            nodes=[1, 2, 3],
            graph_types=["custom_graph", "another_custom_graph"],
            task_names=["rsync_core_puppet"],
            dry_run=True,
            noop_run=True,
            force=True
        )
        self.assertEqual(
            {
                'cluster': 1,
                'dry_run': True,
                'noop_run': True,
                'graphs': [
                    {'nodes': [1, 2, 3], 'type': 'custom_graph',
                     'tasks': ['rsync_core_puppet']},
                    {'nodes': [1, 2, 3], 'type': 'another_custom_graph',
                     'tasks': ['rsync_core_puppet']}
                ],
                'force': True
            },
            matcher_execute.last_request.json()
        )

    def test_env_graphs_list(self):
        release_id = 101
        env_id = 11
        fake_env = utils.get_fake_env(release_id=release_id, env_id=env_id)
        enabled_plugin_id = 331
        self.m_request.get(
            '/api/v1/clusters/{}/'.format(env_id),
            json=fake_env
        )

        self.m_request.get(
            '/api/v1/clusters/{}/attributes'.format(env_id),
            json={
                'editable': {
                    'test-plugin-1': {
                        'metadata': {
                            'class': 'plugin',
                            'enabled': True,
                            'chosen_id': enabled_plugin_id
                        }
                    },
                    'test-plugin-2': {
                        'metadata': {
                            'class': 'plugin',
                            'enabled': False,
                        }
                    }
                }
            }
        )

        release_graphs = [
            {
                "tasks": [],
                "id": 1,
                "relations": [
                    {
                        "model_id": release_id,
                        "model": "release",
                        "type": "default"
                    }
                ],
                "name": None
            }
        ]
        enabled_plugin_graphs = [
            {
                "tasks": [],
                "id": 2,
                "relations": [
                    {
                        "model_id": enabled_plugin_id,
                        "model": "plugin",
                        "type": "default"
                    }
                ],
                "name": None
            }
        ]
        cluster_graphs = [
            {
                "tasks": [],
                "id": 3,
                "relations": [
                    {
                        "model_id": env_id,
                        "model": "cluster",
                        "type": "default"
                    }
                ],
                "name": None
            }
        ]

        all_env_graphs = \
            release_graphs + cluster_graphs + enabled_plugin_graphs

        not_this_env_cluster_graphs = [
            {
                "tasks": [],
                "id": 4,
                "relations": [
                    {
                        "model_id": env_id + 1,
                        "model": "cluster",
                        "type": "default"
                    }
                ],
                "name": None
            }
        ]

        self.m_request.get(
            '/api/v1/releases/{}/deployment_graphs/'.format(release_id),
            json=release_graphs
        )

        self.m_request.get(
            '/api/v1/plugins/{}/deployment_graphs/'.format(enabled_plugin_id),
            json=enabled_plugin_graphs
        )

        self.m_request.get(
            '/api/v1/clusters/{}/deployment_graphs/'.format(env_id),
            json=cluster_graphs
        )

        self.m_request.get(
            '/api/v1/graphs/'.format(env_id),
            json=all_env_graphs + not_this_env_cluster_graphs
        )

        self.assertItemsEqual(
            all_env_graphs, self.client.list(env_id)
        )
        self.assertItemsEqual(
            release_graphs, self.client.list(env_id, filters=['release'])
        )

        self.assertItemsEqual(
            enabled_plugin_graphs,
            self.client.list(env_id, filters=['plugin'])
        )

        self.assertItemsEqual(
            cluster_graphs,
            self.client.list(env_id, filters=['cluster'])
        )

        self.assertItemsEqual(
            all_env_graphs + not_this_env_cluster_graphs,
            self.client.list()
        )

        self.assertItemsEqual(
            cluster_graphs + not_this_env_cluster_graphs + release_graphs,
            self.client.list(filters=['cluster', 'release']))

    def test_new_graph_dry_run_subgraph(self):
        matcher_post = self.m_request.post(
            '/api/v1/graphs/execute/',
            json=utils.get_fake_task(cluster=370))
        # this is required to form running task info
        self.m_request.get(
            '/api/v1/nodes/?cluster_id=370',
            json={}
        )
        self.client.execute(
            env_id=1,
            nodes=[1, 2, 3],
            graph_types=["custom_graph"],
            dry_run=True,
            subgraphs=['primary-database/1,3:keystone-db/1-2,5',
                       'openstack-controller']
        )
        self.assertTrue(matcher_post.called)
        expected_body = {'cluster': 1,
                         'dry_run': True,
                         'graphs':
                             [{
                              'nodes': [1, 2, 3], 'type': 'custom_graph',
                              'tasks': ['rsync_core_puppet']},
                              {
                              'nodes': [1, 2, 3],
                              'type': 'another_custom_graph',
                              'tasks': ['rsync_core_puppet']}],
                         'subgraphs': [
                             {'start': ['primary-database/1,3'],
                              'end': ['keystone-db/1-2,5']},
                             {'start': ['openstack-controller'],
                              'end': [None]}]
                         }
        self.assertItemsEqual(matcher_post.last_request.json(), expected_body)

    def test_graphs_download_all(self):
        matcher_get = self.m_request.get(
            '/api/v1/clusters/1/deployment_tasks/?graph_type=custom_graph',
            json=[]
        )
        self.client.download(env_id=1, level='all',
                             graph_type='custom_graph')
        self.assertTrue(matcher_get.called)

    def test_graphs_download_release(self):
        matcher_get = self.m_request.get(
            '/api/v1/clusters/1/deployment_tasks/'
            'release/?graph_type=custom_graph',
            json=[]
        )
        self.client.download(env_id=1, level='release',
                             graph_type='custom_graph')
        self.assertTrue(matcher_get.called)

    def test_graphs_download_plugins(self):
        matcher_get = self.m_request.get(
            '/api/v1/clusters/1/deployment_tasks/'
            'plugins/?graph_type=custom_graph',
            json=[]
        )
        self.client.download(env_id=1, level='plugins',
                             graph_type='custom_graph')
        self.assertTrue(matcher_get.called)

    def test_graphs_download_cluster(self):
        matcher_get = self.m_request.get(
            '/api/v1/clusters/1/deployment_tasks/own/'
            '?graph_type=custom_graph',
            json=[{'tasks': []}]
        )
        self.client.download(env_id=1, level='cluster',
                             graph_type='custom_graph')
        self.assertTrue(matcher_get.called)

    def test_graph_delete(self):
        matcher_delete = self.m_request.delete(
            '/api/v1/clusters/1/deployment_graphs/custom_graph',
            json={}
        )
        self.client.delete(graph_type='custom_graph',
                           related_id=1,
                           related_model='clusters')
        self.assertTrue(matcher_delete.called)
