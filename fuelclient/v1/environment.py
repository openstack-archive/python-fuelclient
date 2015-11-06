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

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class EnvironmentClient(base_v1.BaseV1Client):
    """Environment Client V1
    """

    _entity_wrapper = objects.Environment

    _updatable_attributes = ('name',)

    def create(self, name, release_id, net_segment_type):
        """Create environment

        :param str name:
        :param str release_id:
        :param str net_segment_type:
        :return dictionary:
        :raises BadDataException:
        """
        supported_nst = ('gre', 'vlan', 'tun')

        if net_segment_type not in supported_nst:
            msg = ('Network segmentation type should be one '
                   'of  {0}'.format(' '.join(supported_nst)))
            raise error.BadDataException(msg)

        env = self._entity_wrapper.create(name, release_id, net_segment_type)

        return env.data

    def update(self, environment_id, **kwargs):
        """Update environment properties

        :param int environment_id:
        :param str name:
        :return object:
        :raises BadDataException:
        """
        allowed_changes = {}
        extra_args = {}

        for i in kwargs:
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
        """Upgrade environment to the given release_id

        :param int environment_id:
        :param str release_id:
        :return dict: Response JSON
        """
        env = self._entity_wrapper(obj_id=environment_id)

        update = {'pending_release_id': release_id}
        env.set(update)

        return env.update_env()

    def delete_by_id(self, environment_id):
        """Delete environment by id

        :param int environment_id:
        """
        env_obj = self._entity_wrapper(obj_id=environment_id)
        env_obj.delete()

    def add_nodes(self, environment_id, nodes, roles):
        """Add nodes to environment

        :param int environment_id:
        :param iterable nodes:
        :param iterable roles:
        """
        env = self._entity_wrapper(obj_id=environment_id)
        env.assign(objects.Node.get_by_ids(nodes), roles)

    def remove_nodes(self, environment_id, nodes):
        """Remove nodes from the environment

        :type nodes: list
        :param int environment_id:
        :param iterable nodes:
        """
        env = self._entity_wrapper(obj_id=environment_id)
        env.unassign(objects.Node.get_by_ids(nodes))

    def deploy_changes(self, environment_id):
        """Deploy changes

        :param int environment_id:
        :return int:
        """
        env = self._entity_wrapper(obj_id=environment_id)
        deploy_task = env.deploy_changes()

        return deploy_task.id

    def spawn_vms(self, environment_id):
        """Spawn VMs assigned to environment

        :param int environment_id:
        :return dict: Response JSON
        """
        env = self._entity_wrapper(obj_id=environment_id)
        return env.spawn_vms()

    def upload_network_template(self, environment_id,
                                file_path=None):
        """Upload network template for the given environment

        :param int environment_id:
        :param str file_path:
        :return str:
        """
        env = self._entity_wrapper(environment_id)
        network_template_data = env.read_network_template_data_from_file(
            file_path=file_path)
        env.set_network_template_data(network_template_data)

        file_path = env.serializer.prepare_path(file_path)
        return file_path

    def download_network_template(self, environment_id, directory=None):
        """Download network template for the given environment

        :param int environment_id:
        :param str directory:
        :return str:
        """
        env = self._entity_wrapper(environment_id)
        template_data = env.get_network_template_data()
        file_path = env.write_network_template_data(
            template_data,
            directory=directory)

        return file_path

    def delete_network_template(self, environment_id):
        """Delete network template for the given environment

        :param int environment_id:
        :return:
        """
        env = self._entity_wrapper(environment_id)
        env.delete_network_template_data()


def get_client():
    """Get Environment client

    :return EnvironmentClient:
    """
    return EnvironmentClient()
