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
from fuelclient.commands.network_group import get_args_for_update
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
            Args.get_name_arg("Name of new network group."),
            Args.get_node_group_arg("ID of node group."),
            Args.get_release_arg("Release ID this network group belongs to."),
            Args.get_vlan_arg("VLAN of network."),
            Args.get_cidr_arg("CIDR of network."),
            Args.get_gateway_arg("Gateway of network."),
            Args.get_network_group_arg("ID of network group."),
            Args.get_meta_arg("Metadata in JSON format to override default "
                              "network metadata."),
            group(
                Args.get_create_network_arg(
                    "Create a new network group for the specified "
                    " node group."
                ),
                Args.get_delete_arg("Delete specified network groups."),
                Args.get_list_arg("List all network groups."),
                Args.get_set_arg("Set network group parameters.")
            )
        )
        self.flag_func_map = (
            ("create", self.create),
            ("delete", self.delete),
            ("set", self.set),
            (None, self.list),
        )

    @check_all('nodegroup', 'name', 'cidr')
    def create(self, params):
        """Create a new network group
               fuel network-group --create --node-group 1 --name "new network"
                --release 2 --vlan 100 --cidr 10.0.0.0/24

               fuel network-group --create --node-group 2 --name "new network"
               --release 2 --vlan 100 --cidr 10.0.0.0/24 --gateway 10.0.0.1
               --meta 'meta information in JSON format'
        """
        meta = self.serializer.deserialize(params.meta) if params.meta else {}

        NetworkGroup.create(
            params.name,
            params.release,
            params.vlan,
            params.cidr,
            params.gateway,
            int(params.nodegroup.pop()),
            meta
        )
        self.serializer.print_to_output(
            {},
            "Network group {0} has been created".format(params.name)
        )

    @check_all('network')
    def delete(self, params):
        """Delete the specified network groups
               fuel network-group --delete --network 1
               fuel network-group --delete --network 2,3,4
        """
        ngs = NetworkGroup.get_by_ids(params.network)
        for network_group in ngs:
            network_group.delete()

        self.serializer.print_to_output(
            {},
            "Network groups with IDS {0} have been deleted.".format(
                ','.join(params.network))
        )

    @check_all('network')
    def set(self, params):
        """Set parameters for the specified network group:
            fuel network-group --set --network 1 --name new_name
        """
        # Since network has set type and we cannot update multiple network
        # groups at once, we pick first network group id from set.
        ng_id = next(iter(params.network))

        if len(params.network) > 1:
            msg = ("Warning: Only first network with id={0}"
                   " will be updated.".format(ng_id))
            self.serializer.print_to_output({}, msg)

        ng = NetworkGroup(ng_id)

        update_params = get_args_for_update(params, self.serializer)
        data = ng.set(update_params)

        self.serializer.print_to_output(
            data,
            "Network group id={0} has been updated".format(ng_id))

    def list(self, params):
        """To list all available network groups:
                fuel network-group list

            To filter them by node group:
                fuel network-group --node-group 1
        """
        group_collection = NetworkGroupCollection.get_all()
        if params.nodegroup:
            group_collection.filter_by_group_id(int(params.nodegroup.pop()))
        self.serializer.print_to_output(
            group_collection.data,
            format_table(
                group_collection.data,
                acceptable_keys=self.acceptable_keys,
            )
        )
