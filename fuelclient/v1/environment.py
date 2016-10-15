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
from fuelclient.v1 import fuelversion


class EnvironmentClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Environment
    _updatable_attributes = ('name',)

    provision_nodes_url = 'clusters/{env_id}/provision/?nodes={nodes}'
    deploy_nodes_url = ('clusters/{env_id}/deploy/?'
                        'nodes={nodes}&force={force}&noop_run={noop_run}')

    def create(self, name, release_id, net_segment_type):

        supported_nst = ('gre', 'vlan', 'tun')

        if net_segment_type not in supported_nst:
            msg = ('Network segmentation type should be one '
                   'of  {0}'.format(' '.join(supported_nst)))
            raise error.BadDataException(msg)

        env = self._entity_wrapper.create(name, release_id, net_segment_type)

        return env.data

    def update(self, environment_id, **kwargs):
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

    def delete_by_id(self, environment_id):
        env_obj = self._entity_wrapper(obj_id=environment_id)
        env_obj.delete()

    def add_nodes(self, environment_id, nodes, roles):
        env = self._entity_wrapper(obj_id=environment_id)
        nodes = [objects.Node(obj_id=n_id) for n_id in nodes]

        env.assign(nodes, roles)

    def remove_nodes(self, environment_id, nodes=None):
        """Remove nodes from environment. If nodes are empty list then
         all nodes will be removed

        :param environment_id: Id of specific environment (cluster)
        :type environment_id: int
        :param nodes: List of node ids that should be removed
        :type nodes: list
        """
        env = self._entity_wrapper(obj_id=environment_id)
        if nodes is not None:
            env.unassign(nodes)
        else:
            env.unassign_all()

    def deploy_changes(self, environment_id, dry_run=False, noop_run=False):
        env = self._entity_wrapper(obj_id=environment_id)

        deploy_task = env.deploy_changes(dry_run=dry_run, noop_run=noop_run)
        return deploy_task.id

    def provision_nodes(self, environment_id, node_ids):
        """Provision specified nodes for the specified environment."""

        nodes = ','.join(str(i) for i in node_ids)
        uri = self.provision_nodes_url.format(env_id=environment_id,
                                              nodes=nodes)
        return self.connection.put_request(uri, {})

    def deploy_nodes(self, environment_id, node_ids, force=False,
                     noop_run=False):
        """Deploy specified nodes for the specified environment."""

        nodes = ','.join(str(i) for i in node_ids)
        uri = self.deploy_nodes_url.format(env_id=environment_id, nodes=nodes,
                                           force=int(force),
                                           noop_run=int(noop_run))
        return self.connection.put_request(uri, {})

    def redeploy_changes(self, environment_id, dry_run=False, noop_run=False):
        env = self._entity_wrapper(obj_id=environment_id)

        redeploy_task = env.redeploy_changes(dry_run=dry_run,
                                             noop_run=noop_run)
        return redeploy_task.id

    def spawn_vms(self, environment_id):
        env = self._entity_wrapper(obj_id=environment_id)
        fuelversion.FuelVersionClient.check_advanced_feature()
        return env.spawn_vms()

    def upload_network_template(self, environment_id,
                                file_path=None):
        env = self._entity_wrapper(environment_id)
        network_template_data = env.read_network_template_data_from_file(
            file_path=file_path)
        env.set_network_template_data(network_template_data)

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

    def get_network_configuration(self, environment_id):
        env = self._entity_wrapper(environment_id)
        return env.get_network_data()

    def set_network_configuration(self, environment_id, new_configuration):
        env = self._entity_wrapper(environment_id)
        env.set_network_data(new_configuration)

    def verify_network(self, environment_id):
        """Start network verification for an environment."""

        env = self._entity_wrapper(environment_id)
        return env.verify_network()

    def get_settings(self, environment_id):
        env = self._entity_wrapper(environment_id)
        return env.get_settings_data()

    def set_settings(self, environment_id, new_configuration, force=False):
        env = self._entity_wrapper(environment_id)
        env.set_settings_data(new_configuration, force=force)

    def delete_facts(self, env_id, fact_type):
        env = self._entity_wrapper(env_id)
        return env.delete_facts(fact_type)

    def download_facts(self, env_id, fact_type, default=False, **kwargs):
        env = self._entity_wrapper(env_id)
        return env.get_facts(fact_type, default=default, **kwargs)

    def upload_facts(self, env_id, fact_type, facts):
        env = self._entity_wrapper(env_id)
        return env.upload_facts(fact_type, facts)

    def reset(self, env_id, force=False):
        env = self._entity_wrapper(obj_id=env_id)
        return env.reset(force)

    def stop(self, env_id):
        env = self._entity_wrapper(obj_id=env_id)
        return env.stop()


def get_client(connection):
    return EnvironmentClient(connection)
