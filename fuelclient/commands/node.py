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


from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient import utils


class NodeMixIn(object):
    entity_name = 'node'


class NodeList(NodeMixIn, base.BaseListCommand):
    """Show list of all avaliable nodes."""

    columns = ('id',
               'name',
               'status',
               'os_platform',
               'roles',
               'ip',
               'mac',
               'cluster',
               'platform_name',
               'online')

    def get_parser(self, prog_name):
        parser = super(NodeList, self).get_parser(prog_name)

        parser.add_argument(
            '-e',
            '--env',
            type=int,
            help='Show only nodes that are in the specified environment'
        )

        return parser

    def take_action(self, parsed_args):

        data = self.client.get_all(environment_id=parsed_args.env)
        data = data_utils.get_display_data_multi(self.columns, data)

        return (self.columns, data)


class NodeShow(NodeMixIn, base.BaseShowCommand):
    """Show info about node with given id."""
    columns = ('id',
               'name',
               'status',
               'os_platform',
               'roles',
               'kernel_params',
               'pending_roles',
               'ip',
               'mac',
               'error_type',
               'pending_addition',
               'hostname',
               'fqdn',
               'platform_name',
               'cluster',
               'online',
               'progress',
               'pending_deletion',
               'group_id',
               # TODO(romcheg): network_data mostly never fits the screen
               # 'network_data',
               'manufacturer')


class NodeVmsList(NodeMixIn, base.BaseShowCommand):
    """Show list vms for node."""

    columns = ('vms_conf',)

    def take_action(self, parsed_args):
        data = self.client.get_node_vms_conf(parsed_args.id)
        data = data_utils.get_display_data_single(self.columns, data)

        return (self.columns, data)


class NodeCreateVMsConf(NodeMixIn, base.BaseCommand):
    """Create vms config in metadata for selected node."""

    def get_parser(self, prog_name):
        parser = super(NodeCreateVMsConf, self).get_parser(prog_name)
        parser.add_argument('id', type=int,
                            help='Id of the {0}.'.format(self.entity_name))
        parser.add_argument(
            '--conf',
            type=str,
            required=True,
            nargs='+',
            help='JSONs with VMs configuration',
        )

        return parser

    def take_action(self, parsed_args):
        confs = utils.parse_to_list_of_dicts(parsed_args.conf)
        data = self.client.node_vms_create(parsed_args.id, confs)
        msg = "{0}".format(data)
        self.app.stdout.write(msg)


class NodeUpdate(NodeMixIn, base.BaseShowCommand):
    """Change given attributes for a node."""

    columns = NodeShow.columns

    def get_parser(self, prog_name):
        parser = super(NodeUpdate, self).get_parser(prog_name)

        parser.add_argument('-H',
                            '--hostname',
                            type=str,
                            default=None,
                            help='New hostname for node')

        return parser

    def take_action(self, parsed_args):
        updates = {}
        for attr in self.client._updatable_attributes:
            if getattr(parsed_args, attr, None):
                updates[attr] = getattr(parsed_args, attr)

        updated_node = self.client.update(parsed_args.id,
                                          updates)
        updated_node = data_utils.get_display_data_single(self.columns,
                                                          updated_node)

        return (self.columns, updated_node)
