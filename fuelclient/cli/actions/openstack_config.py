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

from fuelclient.cli.actions.base import Action
from fuelclient.cli.actions.base import check_all
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli.formatting import format_table
from fuelclient.objects.openstack_config import OpenstackConfig


class OpenstackConfigAction(Action):
    """Manage openstack configuration"""

    action_name = 'openstack-config'
    acceptable_keys = ('id', 'is_active', 'config_type',
                       'cluster_id', 'node_id', 'node_role')

    def __init__(self):
        super(OpenstackConfigAction, self).__init__()
        self.args = (
            Args.get_env_arg(),
            Args.get_file_arg("Openstack configuration file"),
            Args.get_node_arg("Node IDs list"),
            Args.get_single_role_arg("Node role"),
            Args.get_config_id_arg("Openstack config ID"),
            Args.get_deleted_arg("Get deleted configurations"),
            Args.get_force_arg("Force configuration update"),
            group(
                Args.get_list_arg("List openstack configurations"),
                Args.get_download_arg(
                    "Download current openstack configuration"),
                Args.get_upload_arg("Upload new openstack configuration"),
                Args.get_delete_arg("Delete openstack configuration"),
                Args.get_execute_arg("Apply openstack configuration"),
                required=True,
            )
        )

        self.flag_func_map = (
            ('list', self.list),
            ('download', self.download),
            ('upload', self.upload),
            ('delete', self.delete),
            ('execute', self.execute)
        )

    @check_all('env')
    def list(self, params):
        """List all available configurations:
            fuel openstack-config --list --env 1
            fuel openstack-config --list --env 1 --node 1[,2,3,...]
            fuel openstack-config --list --env 1 --deleted
        """
        filters = {'cluster_id': params.env}

        if 'deleted' in params:
            filters['is_active'] = int(not params.deleted)

        if 'node' in params:
            filters['node_ids'] = params.node

        if 'role' in params:
            filters['node_role'] = params.role

        configs = OpenstackConfig.get_filtered_data(**filters)

        self.serializer.print_to_output(
            configs,
            format_table(
                configs,
                acceptable_keys=self.acceptable_keys
            )
        )

    @check_all('config-id', 'file')
    def download(self, params):
        """Download an existing configuration to file:
            fuel openstack-config --download --config-id 1 --file config.yaml
        """
        config_id = getattr(params, 'config-id')
        config = OpenstackConfig(config_id)
        data = config.data
        OpenstackConfig.write_file(params.file, {
            'configuration': data['configuration']})

    @check_all('env', 'file')
    def upload(self, params):
        """Upload new configuration from file:
            fuel openstack-config --upload --env 1 --file config.yaml
            fuel openstack-config --upload --env 1 --node 1[,2,3,...]
                --file config.yaml
            fuel openstack-config --upload --env 1
                --role controller --file config.yaml
        """
        node_ids = getattr(params, 'node', None)
        node_role = getattr(params, 'role', None)
        data = OpenstackConfig.read_file(params.file)

        configs = OpenstackConfig.create(
            cluster_id=params.env,
            configuration=data['configuration'],
            node_ids=node_ids, node_role=node_role)
        configs = [c.data for c in configs]
        self.serializer.print_to_output(
            configs,
            format_table(
                configs,
                acceptable_keys=self.acceptable_keys
            )
        )

    @check_all('config-id')
    def delete(self, params):
        """Delete an existing configuration:
            fuel openstack-config --delete --config 1
        """
        config_id = getattr(params, 'config-id')
        config = OpenstackConfig(config_id)
        config.delete()
        print("Openstack configuration '{0}' "
              "has been deleted.".format(config_id))

    @check_all('env')
    def execute(self, params):
        """Deploy configuration:
            fuel openstack-config --execute --env 1
            fuel openstack-config --execute --env 1 --node 1[,2,3,...]
            fuel openstack-config --execute --env 1 --role controller
            fuel openstack-config --execute --env 1 --force
        """
        node_ids = getattr(params, 'node', None)
        node_role = getattr(params, 'role', None)
        force = getattr(params, 'force', False)
        task_result = OpenstackConfig.execute(
            cluster_id=params.env, node_ids=node_ids,
            node_role=node_role, force=force)
        if task_result['status'] == 'error':
            print(
                'Error applying openstack configuration: {0}.'.format(
                    task_result['message'])
            )
        else:
            print('Openstack configuration update is started.')
