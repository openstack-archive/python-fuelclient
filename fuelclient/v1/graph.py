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
import re
import six

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class GraphClient(base_v1.BaseV1Client):
    _entity_wrapper = objects.Environment

    related_graphs_list_api_path = "{related_model}/{related_model_id}" \
                                   "/deployment_graphs/"

    related_graph_api_path = "{related_model}/{related_model_id}" \
                             "/deployment_graphs/{graph_type}"

    cluster_deploy_api_path = "graphs/execute/"

    merged_cluster_tasks_api_path = "clusters/{env_id}/deployment_tasks" \
                                    "/?graph_type={graph_type}"

    merged_plugins_tasks_api_path = "clusters/{env_id}/deployment_tasks" \
                                    "/plugins/?graph_type={graph_type}"

    cluster_release_tasks_api_path = "clusters/{env_id}/deployment_tasks" \
                                     "/release/?graph_type={graph_type}"

    def update_graph_for_model(
            self, data, related_model, related_model_id, graph_type=None):
        return self.connection.put_request(
            self.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""),
            data
        )

    def create_graph_for_model(
            self, data, related_model, related_model_id, graph_type=None):
        return self.connection.post_request(
            self.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""),
            data
        )

    def get_graph_for_model(
            self, related_model, related_model_id, graph_type=None):
        return self.connection.get_request(
            self.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""))

    def upload(self, data, related_model, related_id, graph_type):
        # create or update
        if not isinstance(data, dict):
            data = {'tasks': data}

        method = self.update_graph_for_model
        # FIXME(bgaifullin) need to remove loading whole graph only
        # for detecting that it does not exist
        try:
            self.get_graph_for_model(related_model, related_id, graph_type)
        except error.HTTPError as exc:
            if '404' in exc.message:
                method = self.create_graph_for_model

        # could accept {tasks: [], metadata: {}} or just tasks list
        method(data, related_model, related_id, graph_type)

    def execute(self, env_id, nodes=None, graph_types=None, task_names=None,
                subgraphs=None, **kwargs):
        request_data = {'cluster': env_id}

        def map_args_to_graph_types(graph):
            result = dict()
            result['type'] = graph
            if nodes:
                result['nodes'] = nodes
            if task_names:
                result['tasks'] = task_names
            return result

        def munge_subgraphs(subgraph):
            regexp = re.compile("^([\w\-,]+(?:\/(?:(?:\d+(?:,|-)?)+))?)"
                                "?(:[\w\-,]+(?:\/(?:(?:\d+(?:,|-)?)+))?)?$")
            result = regexp.match(subgraph)
            start_vertex = None
            end_vertex = None
            if result:
                if result.group(1):
                    start_vertex = result.group(1)
                if result.group(2):
                    end_vertex = result.group(2)[1:]
            return {'start': [start_vertex], 'end': [end_vertex]}

        if graph_types:
            request_data['graphs'] = list(six.moves.map(
                map_args_to_graph_types, graph_types
            ))

        if subgraphs:
            request_data['subgraphs'] = list(
                six.moves.map(lambda s: munge_subgraphs(s), subgraphs))

        request_data.update(kwargs)
        deploy_data = self.connection.post_request(
            self.cluster_deploy_api_path,
            request_data
        )
        return objects.DeployTask.init_with_data(deploy_data)

    def get_merged_cluster_tasks(self, env_id, graph_type=None):
        return self.connection.get_request(
            self.merged_cluster_tasks_api_path.format(
                env_id=env_id,
                graph_type=graph_type or ""))

    def get_merged_plugins_tasks(self, env_id, graph_type=None):
        return self.connection.get_request(
            self.merged_plugins_tasks_api_path.format(
                env_id=env_id,
                graph_type=graph_type or ""))

    def get_release_tasks_for_cluster(self, env_id, graph_type=None):
        return self.connection.get_request(
            self.cluster_release_tasks_api_path.format(
                env_id=env_id,
                graph_type=graph_type or ""))

    def download(self, env_id, level, graph_type):
        tasks_levels = {
            'all': lambda: self.get_merged_cluster_tasks(
                env_id=env_id, graph_type=graph_type),

            'cluster': lambda: self.get_graph_for_model(
                related_model='clusters',
                related_model_id=env_id,
                graph_type=graph_type)[0].get('tasks', []),

            'plugins': lambda: self.get_merged_plugins_tasks(
                env_id=env_id,
                graph_type=graph_type),

            'release': lambda: self.get_release_tasks_for_cluster(
                env_id=env_id,
                graph_type=graph_type)
        }
        return tasks_levels[level]()

    def list(self, env_id):
        # todo(ikutukov): extend lists to support all models
        return self.connection.get_request(
            self.related_graphs_list_api_path.format(
                related_model='clusters',
                related_model_id=env_id))


def get_client(connection):
    return GraphClient(connection)
