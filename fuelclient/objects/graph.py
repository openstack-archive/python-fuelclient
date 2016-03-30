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

from fuelclient.cli.serializers import Serializer
from fuelclient.objects.base import BaseObject
from fuelclient.objects.task import DeployTask


class Graph(BaseObject):

    # Graph is not managed as independent resource with it's own so
    # all methods are class methods not requiring to create Graph instance
    # to use them.

    related_graphs_list_api_path = "{related_model}/{related_model_id}" \
                                   "/deployment_graphs/"

    related_graph_api_path = "{related_model}/{related_model_id}" \
                             "/deployment_graphs/{graph_type}"

    cluster_deploy_api_path = "clusters/{cluster_id}/deploy/"

    @classmethod
    def read_tasks_data_from_file(cls, file_path=None, serializer=None):
        """Read Tasks data from given path.

        :param file_path: path
        :type file_path: str
        :param serializer: serializer object
        :type serializer: object
        :return: data
        :rtype: list|object
        """
        cls._check_file_path(file_path)
        # fixme: serializer will not work with classmethod
        return (serializer or Serializer()).read_from_full_path(file_path)

    @classmethod
    def get_graph_for_model(
            cls, related_model, related_model_id, graph_type=None):
        return cls.connection.get_request(
            cls.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""))

    @classmethod
    def create_graph_for_model(
            cls, data, related_model, related_model_id, graph_type=None):
        return cls.connection.post_request(
            cls.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""),
            data
        )

    @classmethod
    def update_graph_for_model(
            cls, data, related_model, related_model_id, graph_type=None):
        return cls.connection.put_request(
            cls.related_graph_api_path.format(
                related_model=related_model,
                related_model_id=related_model_id,
                graph_type=graph_type or ""),
            data
        )

    @classmethod
    def execute(cls, cluster_id, nodes, graph_type=None):
        get_args = []

        if nodes:
            get_args.append("nodes={0}".format(",".join(map(str, nodes))))

        if graph_type:
            get_args.append(("graph_type=" + graph_type))

        url = "".join([
            cls.cluster_deploy_api_path.format(cluster_id=cluster_id),
            '?',
            '&'.join(get_args)])

        deploy_data = cls.connection.put_request(url, {})
        return DeployTask.init_with_data(deploy_data)
