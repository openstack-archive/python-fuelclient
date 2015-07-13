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


class NodeSetHostname(NodeMixIn, base.BaseCommand):

    columns = ('id',
               'name',
               'hostname',
               'ip',
               'mac',
               'cluster',
               'online')

    def get_parser(self, prog_name):
        parser = super(NodeSetHostname, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='Change hostname for node <node-id>',
        )
        parser.add_argument(
            '--hostname',
            type=str,
            required=True,
            help='New hostname',
        )

        return parser

    def take_action(self, parsed_args):

        data = self.client.set_hostname(parsed_args.id, parsed_args.hostname)
        data = data_utils.get_display_data_single(self.columns, data)

        return (self.columns, data)
