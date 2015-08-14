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

import six

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class EnvironmentClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Environment

    _updatable_attributes = ('name', 'mode')

    def create(self, name, release_id, network_provider,
               deployment_mode='ha_compact', net_segment_type=None):

        if network_provider == 'neutron':
            if net_segment_type not in ('gre', 'vlan', 'tun'):
                msg = 'Using  Neutron as a network provider requires '\
                      'specifying network segmentation type.'
                raise error.BadDataException(msg)
        else:
            if net_segment_type:
                msg = 'Network segmentation type should only be '\
                      'specified for Neutron.'
                raise error.BadDataException(msg)

        env = self._entity_wrapper.create(name, release_id, network_provider,
                                          net_segment_type,
                                          mode=deployment_mode)

        return env.data

    def update(self, environment_id, **kwargs):
        allowed_changes = {}
        extra_args = {}

        for i in six.iterkeys(kwargs):
            if i in self._updatable_attributes:
                allowed_changes[i] = kwargs[i]
            else:
                extra_args[i] = kwargs[i]

        if extra_args != {}:
            msg = 'Only {0} are updatable'.format(self._updatable_attributes)
            raise error.BadDataException(msg)

        env = self._entity_wrapper(obj_id=environment_id)
        env.set(allowed_changes)

        return env.data

    def upgrade(self, environment_id, release_id):
        env = self._entity_wrapper(obj_id=environment_id)

        update = {'pending_release_id': release_id}
        env.set(update)

        return env.update_env()

    def delete_by_id(self, environment_id):
        env_obj = self._entity_wrapper(obj_id=environment_id)
        env_obj.delete()

    def add_nodes(self, environment_id, nodes, roles):
        env = self._entity_wrapper(obj_id=environment_id)
        nodes = [objects.Node(obj_id=n_id) for n_id in nodes]

        env.assign(nodes, roles)

    def deploy_changes(self, environment_id):
        env = self._entity_wrapper(obj_id=environment_id)
        deploy_task = env.deploy_changes()

        return deploy_task.id

    def spawn_vms(self, environment_id):
        env = self._entity_wrapper(obj_id=environment_id)
        return env.spawn_vms()

    def upload_network_template(self, environment_id,
                                file_path=None):
        env = self._entity_wrapper(environment_id)
        network_template_data = env.read_network_template_data_from_file(
            file_path=file_path)
        env.set_network_template_data(network_template_data)

        file_path = env.serializer.prepare_path(file_path)
        return file_path

    def download_network_template(self, environment_id, directory=None):
        env = self._entity_wrapper(environment_id)
        template_data = env.get_network_template_data()
        file_path = env.write_network_template_data(
            template_data,
            directory=directory)

        return file_path

    def delete_network_template(self, environment_id):
        env = self._entity_wrapper(environment_id)
        env.delete_network_template_data()


def get_client():
    return EnvironmentClient()
