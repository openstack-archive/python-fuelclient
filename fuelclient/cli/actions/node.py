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

from itertools import groupby
from operator import attrgetter

from fuelclient.cli.actions.base import Action
from fuelclient.cli.actions.base import check_all
from fuelclient.cli.actions.base import check_any
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli import error
from fuelclient.cli.formatting import format_table
from fuelclient.objects.environment import Environment
from fuelclient.objects.node import Node
from fuelclient.objects.node import NodeCollection


class NodeAction(Action):
    """List and assign available nodes to environments
    """
    action_name = "node"
    acceptable_keys = ("id", "status", "name", "cluster", "ip",
                       "mac", "roles", "pending_roles", "online", "group_id")

    def __init__(self):
        super(NodeAction, self).__init__()
        self.args = [
            Args.get_env_arg(),
            group(
                Args.get_list_arg("List all nodes."),
                Args.get_set_arg("Set role for specific node."),
                Args.get_delete_arg("Delete specific node from environment."),
                Args.get_network_arg("Node network configuration."),
                Args.get_disk_arg("Node disk configuration."),
                Args.get_deploy_arg("Deploy specific nodes."),
                Args.get_hostname_arg("Set node hostname."),
                Args.get_delete_from_db_arg(
                    "Delete specific nodes only from fuel db.\n"
                    "User should still delete node from cobbler"),
                Args.get_provision_arg("Provision specific nodes."),
            ),
            group(
                Args.get_default_arg(
                    "Get default configuration of some node"),
                Args.get_download_arg(
                    "Download configuration of specific node"),
                Args.get_upload_arg(
                    "Upload configuration to specific node")
            ),
            Args.get_dir_arg(
                "Select directory to which download node attributes"),
            Args.get_node_arg("Node id."),
            Args.get_force_arg("Bypassing parameter validation."),
            Args.get_all_arg("Select all nodes."),
            Args.get_role_arg("Role to assign for node."),
            group(
                Args.get_skip_tasks(),
                Args.get_tasks()
            ),
            Args.get_graph_endpoint(),
            Args.get_graph_startpoint(),
        ]

        self.flag_func_map = (
            ("set", self.set),
            ("delete", self.delete),
            ("network", self.attributes),
            ("disk", self.attributes),
            ("deploy", self.start),
            ("provision", self.start),
            ("hostname", self.set_hostname),
            ("delete-from-db", self.delete_from_db),
            ("tasks", self.execute_tasks),
            ("skip", self.execute_tasks),
            ("end", self.execute_tasks),
            ("start", self.execute_tasks),
            (None, self.list)
        )

    @check_all("node", "role", "env")
    def set(self, params):
        """Assign some nodes to environment with with specific roles:
                fuel --env 1 node set --node 1 --role controller
                fuel --env 1 node set --node 2,3,4 --role compute,cinder
        """
        env = Environment(params.env)
        nodes = Node.get_by_ids(params.node)
        roles = map(str.lower, params.role)
        env.assign(nodes, roles)
        self.serializer.print_to_output(
            {},
            "Nodes {0} with roles {1} "
            "were added to environment {2}"
            .format(params.node, roles, params.env)
        )

    @check_any("node", "env")
    def delete(self, params):
        """Remove some nodes from environment:
                fuel --env 1 node remove --node 2,3

           Remove nodes no matter to which environment they were assigned:
                fuel node remove --node 2,3,6,7

           Remove all nodes from some environment:
                fuel --env 1 node remove --all
        """
        if params.env:
            env = Environment(params.env)
            if params.node:
                env.unassign(params.node)
                self.serializer.print_to_output(
                    {},
                    "Nodes with ids {0} were removed "
                    "from environment with id {1}."
                    .format(params.node, params.env))
            else:
                if params.all:
                    env.unassign_all()
                else:
                    raise error.ArgumentException(
                        "You have to select which nodes to remove "
                        "with --node-id. Try --all for removing all nodes."
                    )
                self.serializer.print_to_output(
                    {},
                    "All nodes from environment with id {0} were removed."
                    .format(params.env))
        else:
            nodes = map(Node, params.node)
            for env_id, _nodes in groupby(nodes, attrgetter("env_id")):
                list_of_nodes = [n.id for n in _nodes]
                if env_id:
                    Environment(env_id).unassign(list_of_nodes)
                    self.serializer.print_to_output(
                        {},
                        "Nodes with ids {0} were removed "
                        "from environment with id {1}."
                        .format(list_of_nodes, env_id)
                    )
                else:
                    self.serializer.print_to_output(
                        {},
                        "Nodes with ids {0} aren't added to "
                        "any environment.".format(list_of_nodes)
                    )

    @check_all("node")
    @check_any("default", "download", "upload")
    def attributes(self, params):
        """Download current or default disk, network,
           configuration for some node:
                fuel node --node-id 2 --disk --default
                fuel node --node-id 2 --network --download \\
                --dir path/to/directory

           Upload disk, network, configuration for some node:
                fuel node --node-id 2 --network --upload
                fuel node --node-id 2 --disk --upload --dir path/to/directory
        """
        nodes = Node.get_by_ids(params.node)
        attribute_type = "interfaces" if params.network else "disks"
        attributes = []
        files = []
        if params.default:
            for node in nodes:
                default_attribute = node.get_default_attribute(attribute_type)
                file_path = node.write_attribute(
                    attribute_type,
                    default_attribute,
                    params.dir,
                    serializer=self.serializer
                )
                files.append(file_path)
                attributes.append(default_attribute)
            message = "Default node attributes for {0} were written" \
                      " to:\n{1}".format(attribute_type, "\n".join(files))
        elif params.upload:
            for node in nodes:
                attribute = node.read_attribute(
                    attribute_type,
                    params.dir,
                    serializer=self.serializer
                )
                node.upload_node_attribute(
                    attribute_type,
                    attribute
                )
                attributes.append(attribute)
            message = "Node attributes for {0} were uploaded" \
                      " from {1}".format(attribute_type, params.dir)
        else:
            for node in nodes:
                downloaded_attribute = node.get_attribute(attribute_type)
                file_path = node.write_attribute(
                    attribute_type,
                    downloaded_attribute,
                    params.dir,
                    serializer=self.serializer
                )
                attributes.append(downloaded_attribute)
                files.append(file_path)
            message = "Node attributes for {0} were written" \
                      " to:\n{1}".format(attribute_type, "\n".join(files))
        print(message)

    def get_env_id(self, node_collection):
        env_ids = set(n.env_id for n in node_collection)
        if len(env_ids) != 1:
            raise error.ActionException(
                "Inputed nodes assigned to multiple environments!")
        else:
            return env_ids.pop()

    @check_all("node")
    def start(self, params):
        """Deploy/Provision some node:
                fuel node --node-id 2 --provision
                fuel node --node-id 2 --deploy
        """
        node_collection = NodeCollection.init_with_ids(params.node)
        method_type = "deploy" if params.deploy else "provision"
        env_id_to_start = self.get_env_id(node_collection)

        if not env_id_to_start:
            raise error.ActionException(
                "Input nodes are not assigned to any environment!")

        task = Environment(env_id_to_start).install_selected_nodes(
            method_type, node_collection.collection)

        self.serializer.print_to_output(
            task.data,
            "Started {0}ing {1}."
            .format(method_type, node_collection))

    @check_all("node")
    def execute_tasks(self, params):
        """Execute deployment tasks
                fuel node --node 2 --tasks hiera netconfig
                fuel node --node 2 --skip hiera netconfig
                fuel node --node 2 --skip rsync --end pre_deployment
                fuel node --node 2 --end netconfig
                fuel node --node 2 --start hiera --end neutron
                fuel node --node 2 --start post_deployment
        """
        node_collection = NodeCollection.init_with_ids(params.node)
        env_id_to_start = self.get_env_id(node_collection)

        env = Environment(env_id_to_start)

        tasks = params.tasks or None

        if params.skip or params.end or params.start:
            tasks = env.get_tasks(
                skip=params.skip,
                end=params.end,
                start=params.start,
                include=tasks)

        if not tasks:
            self.serializer.print_to_output({}, "Nothing to run.")
            return

        task = env.execute_tasks(node_collection.collection, tasks=tasks)

        self.serializer.print_to_output(
            task.data,
            "Started tasks {0} for nodes {1}.".format(tasks, node_collection))

    def list(self, params):
        """To list all available nodes:
                fuel node

            To filter them by environment:
                fuel --env-id 1 node

            It's Possible to manipulate nodes with their short mac addresses:
                fuel node --node-id 80:ac
                fuel node remove --node-id 80:ac,5d:a2
        """
        if params.node:
            node_collection = NodeCollection.init_with_ids(params.node)
        else:
            node_collection = NodeCollection.get_all()
        if params.env:
            node_collection.filter_by_env_id(int(params.env))
        self.serializer.print_to_output(
            node_collection.data,
            format_table(
                node_collection.data,
                acceptable_keys=self.acceptable_keys,
                column_to_join=("roles", "pending_roles")
            )
        )

    @check_all("node")
    def delete_from_db(self, params):
        """To delete nodes from fuel db:
                fuel node --node-id 1 --delete-from-db
                fuel node --node-id 1 2 --delete-from-db
            (this works only for offline nodes)
                fuel node --node-id 1 --delete-from-db --force
            (this forces deletion of nodes regardless of their state)
        """
        if not params.force:
            node_collection = NodeCollection.init_with_ids(params.node)

            online_nodes = [node for node in node_collection.data
                            if node['online']]

            if online_nodes:
                raise error.ActionException(
                    "Nodes with ids {0} cannot be deleted from cluster "
                    "because they are online. You might want to use the "
                    "--force option.".format(
                        [node['id'] for node in online_nodes]))

        NodeCollection.delete_by_ids(params.node)

        self.serializer.print_to_output(
            {},
            "Nodes with ids {0} have been deleted from Fuel db.".format(
                params.node)
        )

    @check_all("node", "hostname")
    def set_hostname(self, params):
        """To set node hostname:
                fuel node --node-id 1 --hostname ctrl-01
        """
        nodes = Node.get_by_ids(params.node)

        if len(nodes) > 1:
            raise error.ArgumentException(
                "You should select only one node to change hostname."
            )
        nodes[0].set({"hostname": params.hostname})
        self.serializer.print_to_output(
            {},
            "Hostname for node with id {0} has been changed to {1}."
            .format(params.node[0], params.hostname)
        )
