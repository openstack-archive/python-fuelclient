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

from fuelclient import objects
from fuelclient.v1 import base_v1


class SequenceClient(base_v1.BaseV1Client):
    _entity_wrapper = objects.Sequence

    executor_path = _entity_wrapper.instance_api_path + 'execute/'

    def create(self, release_id, name, graph_types):
        """Creates new sequence object.

        :param release_id: the release object id
        :param name: the sequence name
        :param graph_types: the types of graphs
        :returns: created object
        """
        data = {'name': name}
        graphs = data['graphs'] = []
        for graph_type in graph_types:
            graphs.append({'type': graph_type})

        return self.upload(release_id, data)

    def upload(self, release_id, data):
        """Creates new sequence object from data.

        :param release_id: release object id
        :param data: the sequence properties
        :returns: created object
        """
        url = self._entity_wrapper.class_api_path
        data['release'] = release_id
        return self.connection.post_request(url, data)

    def download(self, sequence_id):
        """Get raw content of sequence."""
        return super(SequenceClient, self).get_by_id(sequence_id)

    def update(self, sequence_id, name=None, graph_types=None):
        """Updates existing object.

        :param sequence_id: the sequence object id
        :param name: new name
        :param graph_types: new graph types
        :returns: updated object or False if nothing to update
        """
        data = {}
        if name:
            data['name'] = name
        if graph_types:
            graphs = data['graphs'] = []
            for graph_type in graph_types:
                graphs.append({'type': graph_type})

        if not data:
            return False

        url = self._entity_wrapper.instance_api_path.format(sequence_id)
        return self.connection.put_request(url, data)

    def get_by_id(self, sequence_id):
        """Gets formatted sequence data by id."""
        data = super(SequenceClient, self).get_by_id(sequence_id)
        data['graphs'] = ', '.join(g['type'] for g in data['graphs'])
        return data

    def delete_by_id(self, sequence_id):
        """Deletes existed object.

        :param sequence_id: the sequence object id
        """
        url = self._entity_wrapper.instance_api_path.format(sequence_id)
        self.connection.delete_request(url)

    def execute(self, sequence_id, env_id, **kwargs):
        """Executes sequence on cluster.

        :param sequence_id: the sequence object id
        :param env_id: the cluster id
        :param kwargs: options - force, dry_run and noop.
        """
        data = {'cluster': env_id}
        data.update(kwargs)
        url = self.executor_path.format(sequence_id)
        deploy_data = self.connection.post_request(url, data)
        return objects.DeployTask.init_with_data(deploy_data)


def get_client(connection):
    return SequenceClient(connection)
