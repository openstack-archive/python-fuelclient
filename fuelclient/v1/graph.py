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
from fuelclient.cli.serializers import Serializer
from fuelclient import objects
from fuelclient.v1 import base_v1


class GraphClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Graph

    def upload(self, cluster_id, release_id, plugin_id, graph_type, file_path):
        if cluster_id:
            related_model = 'clusters'
            related_id = cluster_id
        elif release_id:
            related_model = 'releases'
            related_id = release_id
        elif plugin_id:
            related_model = 'plugins'
            related_id = plugin_id
        else:
            return

        data = self._entity_wrapper.read_tasks_data_from_file(
            file_path, serializer=Serializer())

        # create or update
        try:
            self._entity_wrapper.get_graph_for_model(
                related_model, related_id, graph_type)
            self._entity_wrapper.update_graph_for_model(
                {'tasks': data}, related_model, related_id, graph_type)
        except error.HTTPError as exc:
            if '404' in exc.message:
                self._entity_wrapper.create_graph_for_model(
                    {'tasks': data}, related_model, related_id, graph_type)

    def execute(self, env_id, nodes, graph_type=None):
        return self._entity_wrapper.execute(
            cluster_id=env_id,
            nodes=nodes,
            graph_type=graph_type)


def get_client():
    return GraphClient()
