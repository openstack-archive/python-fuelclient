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
from fuelclient.cli.error import ActionException
from fuelclient.cli.formatting import format_table
from fuelclient.objects.network_group import NetworkGroup
from fuelclient.objects.network_group import NetworkGroupCollection


class NetworkGroupAction(Action):
    """Show or modify network groups
    """
    action_name = "network-group"
    acceptable_keys = ("id", "name", "vlan_start", "cidr",
                       "gateway", "group_id")

    def __init__(self):
        super(NetworkGroupAction, self).__init__()
        self.args = (
            Args.get_env_arg(),
            Args.get_list_arg("List all network groups."),
            Args.get_name_arg("Name of new network group."),
            Args.get_group_arg("ID of node group."),
            Args.get_release_arg("Release ID this network belongs to."),
            Args.get_vlan_arg("VLAN of network."),
            Args.get_cidr_arg("CIDR of network."),
            Args.get_gateway_arg("Gateway of network."),
            Args.get_network_group_arg("ID of network group."),
            Args.get_meta_arg("Metadata in JSON format to override default "
                              "network metadata."),
            group(
                Args.get_create_arg(
                    "Create a new network group for the specified "
                    " node group."
                ),
                Args.get_delete_arg("Delete specified network groups."),
            )
        )
        self.flag_func_map = (
            ("create", self.create),
            ("delete", self.delete),
            (None, self.list)
        )

    @check_all("group", "name")
    def create(self, params):
        """Create a new network group
               fuel --env 1 network --create --group 1
        """
        NetworkGroup.create(
            params.name,
            params.release,
            params.vlan,
            params.cidr,
            params.gateway,
            int(params.group.pop()),
            params.meta
        )


    def delete(self, params):
        """Delete the specified network groups
               fuel --env 1 network --delete --id 1
               fuel --env 1 network --delete --id 2,3,4
        """
        ngs = NetworkGroup.get_by_ids(params.network)
        for n in ngs:
            NetworkGroup.delete(n.id)

    def list(self, params):
        """To list all available network groups:
                fuel network list

            To filter them by environment:
                fuel --env-id 1 network
        """
        group_collection = NetworkGroupCollection.get_all()
        if params.group:
            group_collection.filter_by_group_id(int(params.group.pop()))
        self.serializer.print_to_output(
            group_collection.data,
            format_table(
                group_collection.data,
                acceptable_keys=self.acceptable_keys,
            )
        )
