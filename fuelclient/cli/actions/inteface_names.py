#    Copyright 2014 Mirantis, Inc.
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
from fuelclient.objects.node import InterfaceNamesManager


class InterfaceNamesAction(Action):
    """Show or modify network interfaces names
    """
    action_name = "interface-names"
    acceptable_keys = ("id", "node_id", "name", "mac", "max_speed",
                       "current_speed", "ip_addr", "netmask", "bus_info")

    def __init__(self):
        super(InterfaceNamesAction, self).__init__()
        self.args = (
            Args.get_env_arg(),
            Args.get_node_arg("Node IDs to filter on"),
            Args.get_mac_arg(),
            Args.get_bus_arg(),
            Args.get_dir_arg("Directory with interface names configuration."),
            Args.get_rename_nic_from_arg(),
            Args.get_rename_nic_to_arg(),
            group(
                Args.get_list_arg(
                    "List current interface names configuration."),
                Args.get_rename_arg(
                    "Rename interfaces."),
                Args.get_download_arg(
                    "Download current interface names configuration."),
                Args.get_upload_arg(
                    "Upload changed interface names configuration."),
            )
        )
        self.flag_func_map = (
            ("list", self.list),
            ("rename", self.rename),
            ("upload", self.upload),
            ("download", self.download),
            (None, self.list)
        )

    def list(self, params):
        """To list all network interfaces and their names on all nodes:
                fuel interface-names

            To filter them by environment:
                fuel interface-names --env 1

            To list them for specific nodes:
                fuel inteface-names --node 1,2,3

            To filter them by bus_info:
                fuel interface-names --bus "0000:01:00.0"

            To filter them by MAC address:
                fuel interface-names --mac "00:25:90:6a:b1:10"
        """
        ifnames_mgr = InterfaceNamesManager(params=params)
        ifnames_data = ifnames_mgr.get_interface_names(
            node_id=params.node, cluster_id=params.env,
            mac=params.mac, bus_info=params.bus)
        if len(ifnames_data) > 0:
            self.serializer.print_to_output(
                ifnames_data,
                format_table(
                    ifnames_data,
                    acceptable_keys=self.acceptable_keys)
            )

    @check_all("fromnic", "tonic")
    def rename(self, params):
        """To rename all interfaces with name eth0 to ethZ:
                fuel interface-names --rename --fromnic eth0 --tonic ethZ
        """
        ifnames_mgr = InterfaceNamesManager(params=params)
        ifnames_data = ifnames_mgr.get_interface_names(
            node_id=params.node, cluster_id=params.env,
            mac=params.mac, bus_info=params.bus)
        for nic in ifnames_data:
            if nic['name'] == params.fromnic:
                nic['old_name'] = nic['name']
                nic['name'] = params.tonic
        new_ifnames_data = ifnames_mgr.upload_interface_names(ifnames_data)
        if len(new_ifnames_data) > 0:
            self.serializer.print_to_output(
                new_ifnames_data,
                format_table(
                    new_ifnames_data,
                    acceptable_keys=self.acceptable_keys)
            )

    def upload(self, params):
        """To upload interface names configuration
           from the specified directory:
                fuel interface-names --upload --dir path/to/directory
        """
        ifnames_mgr = InterfaceNamesManager(params=params)
        ifnames_data = ifnames_mgr.read_interface_names(params.dir)
        ifnames_mgr.upload_interface_names(ifnames_data)
        print(
            "Interface names configuration uploaded."
        )

    def download(self, params):
        """To download interface names configuration to the current
           directory:
                fuel interface-names --download

           Same filters can be applied as for the 'list' command
        """
        ifnames_mgr = InterfaceNamesManager(params=params)
        ifnames_data = ifnames_mgr.get_interface_names(
            node_id=params.node, cluster_id=params.env,
            mac=params.mac, bus_info=params.bus)
        ifnames_file_path = ifnames_mgr.write_interface_names(
            ifnames_data, params.dir)
        print(
            "Interface names configuration saved to {0}"
            .format(ifnames_file_path)
        )
