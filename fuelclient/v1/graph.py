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
from fuelclient.client import APIClient
from fuelclient import objects
from fuelclient.v1 import base_v1


class GraphClient(base_v1.BaseV1Client):
    _entity_wrapper = objects.Environment

    related_graphs_list_api_path = "{related_model}/{related_model_id}" \
                                   "/deployment_graphs/"

    related_graph_api_path = "{related_model}/{related_model_id}" \
                             "/deployment_graphs/{graph_type}"

    cluster_deploy_api_path = "clusters/{env_id}/deploy/"

    @classmethod
    def update_graph_for_model(
            cls, data, related_model, related_model_id, graph_type=None):
        return APIClient.put_request(
            cls.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""),
            data
        )

    @classmethod
    def create_graph_for_model(
            cls, data, related_model, related_model_id, graph_type=None):
        return APIClient.post_request(
            cls.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""),
            data
        )

    @classmethod
    def get_graph_for_model(
            cls, related_model, related_model_id, graph_type=None):
        return APIClient.get_request(
            cls.related_graph_api_path.format(
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

    @classmethod
    def execute(cls, env_id, nodes, graph_type=None):
        put_args = []

        if nodes:
            put_args.append("nodes={0}".format(",".join(map(str, nodes))))

        if graph_type:
            put_args.append(("graph_type=" + graph_type))

        url = "".join([
            cls.cluster_deploy_api_path.format(env_id=env_id),
            '?',
            '&'.join(put_args)])

        deploy_data = APIClient.put_request(url, {})
        return objects.DeployTask.init_with_data(deploy_data)


def get_client():
    return GraphClient()
