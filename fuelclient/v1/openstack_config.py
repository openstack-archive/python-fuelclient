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

from fuelclient import objects
from fuelclient.v1 import base_v1


class OpenstackConfigClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.OpenstackConfig

    def upload(self, path, cluster_id, node_ids=None, node_role=None):
        data = self._entity_wrapper.read_file(path)
        configuration = data['configuration']

        config_obj = self._entity_wrapper.create(cluster_id=cluster_id,
                                                 configuration=configuration,
                                                 node_ids=node_ids,
                                                 node_role=node_role)
        return [obj.data for obj in config_obj]

    def download(self, config_id, path):
        config = self._entity_wrapper(config_id)
        config.write_file(path, {
            'configuration': config.data['configuration']})

        return path

    def execute(self, cluster_id, config_id=None, node_ids=None,
                node_role=None, force=False):
        task = self._entity_wrapper.execute(cluster_id=cluster_id,
                                            config_id=config_id,
                                            node_ids=node_ids,
                                            node_role=node_role,
                                            force=force)

        return task.data

    def get_filtered(self, cluster_id, node_ids=None,
                     node_role=None, is_active=True):
        return self._entity_wrapper.get_filtered_data(
            cluster_id=cluster_id, node_ids=node_ids,
            node_role=node_role, is_active=is_active)

    def delete(self, config_id):
        config = self._entity_wrapper(config_id)
        config.delete()


def get_client(connection):
    return OpenstackConfigClient(connection)
