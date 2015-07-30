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

from fuelclient.commands import base
from fuelclient.common import data_utils


class NetworkGroupMixin(object):
    entity_name = 'network_group'


class NetworkGroupList(NetworkGroupMixin, base.BaseListCommand):

    columns = (
        'id',
        'name',
        'vlan_start',
        'cidr',
        'gateway',
        'group_id'
    )


class NetworkGroupCreate(NetworkGroupMixin, base.BaseShowCommand):

    columns = NetworkGroupList.columns

    def get_parser(self, prog_name):
        parser = show.ShowOne.get_parser(self, prog_name)

        parser.add_argument(
            'name',
            type=str,
            help='Name of the new network group'
        )

        parser.add_argument(
            '-n', '--node-group',
            type=int,
            required=True,
            help='ID of the network group'
        )

        parser.add_argument(
            '-C', '--cidr',
            type=str,
            required=True,
            help='CIDR of the network'
        )

        parser.add_argument(
            '-V', '--vlan',
            type=int,
            help='VLAN of the network',
        )

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

        return parser

    def take_action(self, parsed_args):
        net_group = self.client.create(
            name=parsed_args.name,
            release=parsed_args.release,
            vlan=parsed_args.vlan,
            cidr=parsed_args.cidr,
            gateway=parsed_args.gateway,
            group_id=parsed_args.node_group,
            meta=parsed_args.meta)

        net_group = data_utils.get_display_data_single(self.columns, net_group)
        return self.columns, net_group


class NetworkGroupDelete(NetworkGroupMixin, base.BaseDeleteCommand):
    pass
