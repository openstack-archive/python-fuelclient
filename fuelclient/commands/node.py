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

from fuelclient.cli import error
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


class NodeVmsList(NodeMixIn, base.BaseCommand):
    """Show list vms for node."""

    columns = ('id',
               'name',
               'status',
               'task_state',
               'power_state',
               'networks',)

    def get_parser(self, prog_name):
        parser = super(NodeVmsList, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='Display VMs hosted on node <node-id>',
        )

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_node_vms_list(parsed_args.id)
        data = data_utils.get_display_data_multi(self.columns, data)

        return (self.columns, data)


class NodeVmsCreate(NodeMixIn, base.BaseCommand):
    """Create vms on specified node."""

    def get_parser(self, prog_name):
        parser = super(NodeVmsCreate, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='Create VMs on node <node-id>',
        )
        parser.add_argument(
            '--conf',
            type=str,
            required=True,
            help='Json file with VMs configuration',
        )

        return parser

    def take_action(self, parsed_args):
        self.check_file(parsed_args.conf)
        config = utils.parse_json_file(parsed_args.conf)

        data = self.client.node_vms_create(parsed_args.id, config)

        msg = "Response [{0}]".format(data)

        self.app.stdout.write(msg)

    def check_file(self, file_path):
        if not utils.file_exists(file_path):
            raise error.ArgumentException(
                'File {0} does not exists'.format(file_path)
            )
