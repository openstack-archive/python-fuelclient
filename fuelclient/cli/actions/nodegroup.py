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

import sys

import six

from fuelclient.cli.actions.base import Action
from fuelclient.cli.actions.base import check_all
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli.error import ActionException
from fuelclient.cli.formatting import format_table
from fuelclient.objects import Environment
from fuelclient.objects.nodegroup import NodeGroup
from fuelclient.objects.nodegroup import NodeGroupCollection


class NodeGroupAction(Action):
    """Show or modify node groups
    """
    action_name = "nodegroup"
    acceptable_keys = ("id", "cluster_id", "name")

    def __init__(self):
        super(NodeGroupAction, self).__init__()
        self.args = (
            Args.get_env_arg(),
            Args.get_list_arg("List all node groups."),
            Args.get_name_arg("Name of new node group."),
            Args.get_group_arg("ID of node group."),
            Args.get_node_arg("List of nodes to assign specified group to."),
            group(
                Args.get_create_arg(
                    "Create a new node group in the specified environment."
                ),
                Args.get_assign_arg(
                    "Assign nodes to the specified node group."),
                Args.get_delete_arg(
                    "Delete specified node groups."),
            )
        )
        self.flag_func_map = (
            ("create", self.create),
            ("delete", self.delete),
            ("assign", self.assign),
            (None, self.list)
        )

    @check_all("env", "name")
    def create(self, params):
        """Create a new node group
               fuel --env 1 nodegroup --create --name "group 1"
        """
        env_id = int(params.env)
        data = NodeGroup.create(params.name, env_id)
        env = Environment(env_id)
        network_data = env.get_network_data()
        seg_type = network_data['networking_parameters'].get(
            'segmentation_type'
        )
        if seg_type == 'vlan':
            six.print_("WARNING: In VLAN segmentation type, there will be no "
                       "connectivity over private network between instances "
                       "running on hypervisors in different segments and that "
                       "it's a user's responsibility to handle this "
                       "situation.",
                       file=sys.stderr)

        self.serializer.print_to_output(
            data,
            u"Node group '{name}' with id={id} "
            u"in environment {env} was created!"
            .format(env=env_id, **data)
        )

    @check_all("group")
    def delete(self, params):
        """Delete the specified node groups
               fuel nodegroup --delete --group 1
               fuel nodegroup --delete --group 2,3,4
        """
        ngs = NodeGroup.get_by_ids(params.group)
        for n in ngs:
            if n.name == "default":
                raise ActionException(
                    "Default node groups cannot be deleted."
                )
            data = NodeGroup.delete(n.id)
            self.serializer.print_to_output(
                data,
                u"Node group with id={id} was deleted!"
                .format(id=n.id)
            )

    @check_all("node", "group")
    def assign(self, params):
        """Assign nodes to specified node group:
                fuel nodegroup --assign --node 1 --group 1
                fuel nodegroup --assign --node 2,3,4 --group 1
        """
        if len(params.group) > 1:
            raise ActionException(
                "Nodes can only be assigned to one node group."
            )

        group = NodeGroup(params.group.pop())
        group.assign(params.node)

    def list(self, params):
        """To list all available node groups:
                fuel nodegroup

            To filter them by environment:
                fuel --env-id 1 nodegroup
        """
        group_collection = NodeGroupCollection.get_all()
        if params.env:
            group_collection.filter_by_env_id(int(params.env))
        self.serializer.print_to_output(
            group_collection.data,
            format_table(
                group_collection.data,
                acceptable_keys=self.acceptable_keys,
            )
        )
