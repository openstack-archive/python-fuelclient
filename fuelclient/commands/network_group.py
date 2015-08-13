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

from cliff import show

from fuelclient.cli.serializers import Serializer
from fuelclient.commands import base
from fuelclient.common import data_utils


_updatable_keys = (
    'name', 'vlan', 'cidr', 'gateway', 'group_id', 'meta')


def get_args_for_update(params, serializer=None):
    result = {}
    for attr in _updatable_keys:
        value = getattr(params, attr, None)
        if value is not None:
            result[attr] = value

    if 'meta' in result:
        serializer = serializer or Serializer.from_params(params)
        result['meta'] = serializer.deserialize(result['meta'])

    return result


class NetworkGroupMixin(object):
    entity_name = 'network-group'

    @staticmethod
    def add_parser_arguments(parser, for_update=False):
        parser.add_argument(
            '-N', '--node-group',
            type=int,
            required=not for_update,
            help='ID of the network group'
        )

        parser.add_argument(
            '-C', '--cidr',
            type=str,
            required=not for_update,
            help='CIDR of the network'
        )

        parser.add_argument(
            '-V', '--vlan',
            type=int,
            help='VLAN of the network',
        )

        if not for_update:
            parser.add_argument(
                '-r', '--release',
                type=int,
                help='Release ID this network group belongs to'
            )

        parser.add_argument(
            '-g', '--gateway',
            type=str,
            help='Gateway of the network'
        )

        parser.add_argument(
            '-m', '--meta',
            type=str,
            help='Metadata in JSON format to override default network metadata'
        )


class NetworkGroupList(NetworkGroupMixin, base.BaseListCommand):
    """List all network groups."""

    columns = (
        'id',
        'name',
        'vlan_start',
        'cidr',
        'gateway',
        'group_id'
    )


class NetworkGroupShow(NetworkGroupMixin, base.BaseShowCommand):
    """Show network group."""

    columns = NetworkGroupList.columns + ('meta',)


class NetworkGroupCreate(NetworkGroupMixin, base.BaseShowCommand):
    """Create a new network group."""

    columns = NetworkGroupList.columns

    def get_parser(self, prog_name):
        parser = show.ShowOne.get_parser(self, prog_name)

        parser.add_argument(
            'name',
            type=str,
            help='Name of the new network group'
        )

        self.add_parser_arguments(parser)

        return parser

    def take_action(self, parsed_args):
        meta = None
        if parsed_args.meta:
            serializer = Serializer.from_params(parsed_args)
            meta = serializer.deserialize(parsed_args.meta)

        net_group = self.client.create(
            name=parsed_args.name,
            release=parsed_args.release,
            vlan=parsed_args.vlan,
            cidr=parsed_args.cidr,
            gateway=parsed_args.gateway,
            group_id=parsed_args.node_group,
            meta=meta)

        net_group = data_utils.get_display_data_single(self.columns, net_group)
        return self.columns, net_group


class NetworkGroupUpdate(NetworkGroupMixin, base.BaseShowCommand):
    """Set parameters for the specified network group."""

    columns = NetworkGroupList.columns

    def get_parser(self, prog_name):
        parser = show.ShowOne.get_parser(self, prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='ID of the network group to update')
        parser.add_argument(
            '-n',
            '--name',
            type=str,
            help='New name for network group')

        self.add_parser_arguments(parser, for_update=True)

        return parser

    def take_action(self, parsed_args):
        to_update = get_args_for_update(parsed_args)

        network_group = self.client.update(parsed_args.id, **to_update)
        network_group = data_utils.get_display_data_single(
            self.columns, network_group)

        return self.columns, network_group


class NetworkGroupDelete(NetworkGroupMixin, base.BaseDeleteCommand):
    """Delete specified network group."""
