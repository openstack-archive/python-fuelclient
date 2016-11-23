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

    graphs_list_api = "graphs/"
    cluster_deploy_api_path = "graphs/execute/"

    cluster_own_tasks_api_path = "clusters/{env_id}/deployment_tasks/own/"

    merged_cluster_tasks_api_path = "clusters/{env_id}/deployment_tasks/"

    merged_plugins_tasks_api_path = "clusters/{env_id}/deployment_tasks/" \
                                    "plugins/"

    cluster_release_tasks_api_path = "clusters/{env_id}/deployment_tasks/" \
                                     "release/"

    def update_graph_for_model(
            self, data, related_model, related_model_id, graph_type):
        return self.connection.put_request(
            self.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type),
            data
        )

    def create_graph_for_model(
            self, data, related_model, related_model_id, graph_type):
        return self.connection.post_request(
            self.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type),
            data
        )

    def get_graph_for_model(
            self, related_model, related_model_id, graph_type):
        return self.connection.get_request(
            self.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type))

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
        params = {}
        if graph_type is not None:
            params['graph_type'] = graph_type

        return self.connection.get_request(
            self.merged_cluster_tasks_api_path.format(env_id=env_id),
            params=params
        )

    def get_merged_plugins_tasks(self, env_id, graph_type=None):
        params = {}
        if graph_type is not None:
            params['graph_type'] = graph_type

        return self.connection.get_request(
            self.merged_plugins_tasks_api_path.format(env_id=env_id),
            params=params
        )

    def get_release_tasks_for_cluster(self, env_id, graph_type=None):
        params = {}
        if graph_type is not None:
            params['graph_type'] = graph_type

        return self.connection.get_request(
            self.cluster_release_tasks_api_path.format(env_id=env_id),
            params=params
        )

    def get_own_tasks_for_cluster(self, env_id, graph_type=None):
        params = {}
        if graph_type is not None:
            params['graph_type'] = graph_type

        return self.connection.get_request(
            self.cluster_own_tasks_api_path.format(env_id=env_id),
            params=params
        )

    def download(self, env_id, level, graph_type):
        tasks_levels = {
            'all': lambda: self.get_merged_cluster_tasks(
                env_id=env_id, graph_type=graph_type),

            'cluster': lambda: self.get_own_tasks_for_cluster(
                env_id=env_id, graph_type=graph_type),

            'plugins': lambda: self.get_merged_plugins_tasks(
                env_id=env_id, graph_type=graph_type),

            'release': lambda: self.get_release_tasks_for_cluster(
                env_id=env_id, graph_type=graph_type)
        }
        return tasks_levels[level]()

    def get_env_release_graphs_list(self, env_id):
        """Get list of graphs related to the environment's release.

        :param env_id: environment ID
        :type env_id: int
        :return: list of graphs records
        :rtype: list[dict]
        """
        data = self.get_by_id(env_id)
        release_id = data['release_id']
        return self.connection.get_request(
            self.related_graphs_list_api_path.format(
                related_model='releases',
                related_model_id=release_id
            ), params={'fetch_related': '0'}
        )

    def get_env_cluster_graphs_list(self, env_id, fetch_related=True):
        """Get list of graphs related to the environment.

        :param env_id: environment ID
        :type env_id: int
        :param fetch_related: fetch graphs related to
                              cluster plugins and release
        :type fetch_related: bool

        :return: list of graphs records
        :rtype: list[dict]
        """
        return self.connection.get_request(
            self.related_graphs_list_api_path.format(
                related_model='clusters',
                related_model_id=env_id,
            ), params={'fetch_related': '1' if fetch_related else '0'}
        )

    def get_env_plugins_graphs_list(self, env_id):
        """Get list of graphs related to plugins active for the

        given environment.

        :param env_id: environment ID
        :type env_id: int
        :return: list of graphs records
        :rtype: list[dict]
        """
        env = objects.Environment(env_id)
        enabled_plugins_ids = env.get_enabled_plugins()
        result = []
        for plugin_id in enabled_plugins_ids:
            result += self.connection.get_request(
                self.related_graphs_list_api_path.format(
                    related_model='plugins',
                    related_model_id=plugin_id
                ), params={'fetch_related': '0'}
            )
        return result

    def get_all_graphs_list(self):
        return self.connection.get_request(self.graphs_list_api)

    def list(self, env_id=None, filters=None):
        """Get graphs list.

        If all filter flags are set to False, then it fill be considered as
        'show all' and all filter flags will be toggled to True.

        :param env_id: environment ID
        :type env_id: int
        :param filters: the name of models which graphs will be included
                        to result
        :return: list of graphs records
        :rtype: list[dict]
        """
        # we cannot use dict here, because order is important
        handlers = (
            ('release', self.get_env_release_graphs_list),
            ('plugin', self.get_env_plugins_graphs_list),
            ('cluster', self.get_env_cluster_graphs_list)
        )

        graphs_list = []
        filters = filters and set(filters)

        if env_id:
            for relation, handler in handlers:
                if not filters or relation in filters:
                    graphs_list.extend(handler(env_id=env_id))
        else:
            all_graphs_list = self.get_all_graphs_list()
            for graph in all_graphs_list:
                for relation in graph['relations']:
                    if not filters or relation['model'] in filters:
                        graphs_list.append(graph)
                        break

        return graphs_list

    def delete(self, related_model, related_id, graph_type):
        return self.connection.delete_request(
            self.related_graph_api_path.format(related_model=related_model,
                                               related_model_id=related_id,
                                               graph_type=graph_type))


def get_client(connection):
    return GraphClient(connection)
