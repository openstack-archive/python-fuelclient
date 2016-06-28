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

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.objects import Environment
from fuelclient.v1 import base_v1
from fuelclient.v1.plugins import PluginsClient


class GraphClient(base_v1.BaseV1Client):
    _entity_wrapper = objects.Environment

    related_graphs_list_api_path = "{related_model}/{related_model_id}" \
                                   "/deployment_graphs/"

    related_graph_api_path = "{related_model}/{related_model_id}" \
                             "/deployment_graphs/{graph_type}"

    cluster_deploy_api_path = "clusters/{env_id}/deploy/"

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
        try:
            self.get_graph_for_model(
                related_model, related_id, graph_type)
            self.update_graph_for_model(
                {'tasks': data}, related_model, related_id, graph_type)
        except error.HTTPError as exc:
            if '404' in exc.message:
                self.create_graph_for_model(
                    {'tasks': data}, related_model, related_id, graph_type)

    def execute(self, env_id, nodes, graph_type=None, dry_run=False):
        put_args = []

        if nodes:
            put_args.append("nodes={0}".format(",".join(map(str, nodes))))

        if graph_type:
            put_args.append(("graph_type=" + graph_type))

        if dry_run:
            put_args.append("dry_run=1")
        url = "".join([
            self.cluster_deploy_api_path.format(env_id=env_id),
            '?',
            '&'.join(put_args)])

        deploy_data = self.connection.put_request(url, {})
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
                graph_type=graph_type).get('tasks', []),

            'plugins': lambda: self.get_merged_plugins_tasks(
                env_id=env_id,
                graph_type=graph_type),

            'release': lambda: self.get_release_tasks_for_cluster(
                env_id=env_id,
                graph_type=graph_type)
        }
        return tasks_levels[level]()

    def get_env_release_graphs_list(self, env_id):
        data = self.get_by_id(env_id)
        release_id = data['release_id']
        return self.connection.get_request(
            self.related_graphs_list_api_path.format(
                related_model='releases',
                related_model_id=release_id)
        )

    def get_env_cluster_graphs_list(self, env_id):
        return self.connection.get_request(
            self.related_graphs_list_api_path.format(
                related_model='clusters',
                related_model_id=env_id)
        )

    def get_env_plugins_graphs_list(self, env_id):
        # fixme(ikutukov): code is taken from
        # https://review.openstack.org/#/c/332886/6/
        # fuelweb_test/models/fuel_web_client.py
        # Actually, for now there is no elegant way to get all enabled plugins
        cl_attrib = Environment(env_id).get_attributes()
        all_plugins_data = PluginsClient().get_all()
        enabled_plugins_ids = []
        for plugin in all_plugins_data:
            plugin_name = plugin['name']
            if plugin_name in cl_attrib['editable']:
                if cl_attrib['editable'][plugin_name]\
                        .get('metadata', {}).get('enabled', False):
                    enabled_plugins_ids.append(plugin['id'])

        result = []
        for plugin_id in enabled_plugins_ids:
            result += self.connection.get_request(
                self.related_graphs_list_api_path.format(
                    related_model='plugins',
                    related_model_id=plugin_id
                )
            )
        return result

    def get_env_all_graphs_list(self, env_id):
        return (
            self.get_env_release_graphs_list(env_id) +
            self.get_env_plugins_graphs_list(env_id) +
            self.get_env_cluster_graphs_list(env_id)
        )

    def list(self, env_id, level='all'):
        graph_levels = {
            'release': lambda: self.get_env_release_graphs_list(env_id=env_id),
            'plugins': lambda: self.get_env_plugins_graphs_list(env_id=env_id),
            'cluster': lambda: self.get_env_cluster_graphs_list(env_id=env_id),
            'all': lambda: self.get_env_all_graphs_list(env_id=env_id)
        }

        if level in graph_levels:
            return graph_levels[level]()
        else:
            raise error.BadDataException(
                'Graph level value {} not among valid: {}'.format(
                    level, ", ".join(list(graph_levels))
                )
            )


def get_client(connection):
    return GraphClient(connection)
