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

import collections
import json
import operator
import os

from oslo_utils import fileutils
import six

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient import utils


class NodeMixIn(object):
    entity_name = 'node'

    numa_fields = (
        'numa_nodes',
        'supported_hugepages',
        'distances')

    supported_file_formats = ('json', 'yaml')
    allowed_attr_types = ('attributes', 'disks', 'interfaces')

    @classmethod
    def get_numa_topology_info(cls, data):
        numa_topology_info = {}
        numa_topology = data['meta'].get('numa_topology', {})
        for key in cls.numa_fields:
            numa_topology_info[key] = numa_topology.get(key)
        return numa_topology_info


class NodeList(NodeMixIn, base.BaseListCommand):
    """Show list of all available nodes."""

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
            help='Show only nodes that are in the specified environment')

        parser.add_argument(
            '-l',
            '--labels',
            type=utils.str_to_unicode,
            nargs='+',
            help='Show only nodes that have specific labels')

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all(
            environment_id=parsed_args.env, labels=parsed_args.labels)
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
    columns += NodeMixIn.numa_fields

    def take_action(self, parsed_args):
        data = self.client.get_by_id(parsed_args.id)
        numa_topology = self.get_numa_topology_info(data)
        data.update(numa_topology)
        data = data_utils.get_display_data_single(self.columns, data)
        return self.columns, data


class NodeUpdate(NodeMixIn, base.BaseShowCommand):
    """Change given attributes for a node."""

    columns = NodeShow.columns

    def get_parser(self, prog_name):
        parser = super(NodeUpdate, self).get_parser(prog_name)

        parser.add_argument(
            '-H',
            '--hostname',
            type=str,
            default=None,
            help='New hostname for node')

        parser.add_argument(
            '--name',
            type=lambda x: x.decode('utf-8') if six.PY2 else x,
            default=None,
            help='New name for node')

        return parser

    def take_action(self, parsed_args):
        updates = {}
        for attr in self.client._updatable_attributes:
            if getattr(parsed_args, attr, None):
                updates[attr] = getattr(parsed_args, attr)

        updated_node = self.client.update(
            parsed_args.id, **updates)
        numa_topology = self.get_numa_topology_info(updated_node)
        updated_node.update(numa_topology)
        updated_node = data_utils.get_display_data_single(
            self.columns, updated_node)

        return self.columns, updated_node


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
            type=json.loads,
            required=True,
            nargs='+',
            help='JSONs with VMs configuration',
        )

        return parser

    def take_action(self, parsed_args):
        try:
            confs = utils.parse_to_list_of_dicts(parsed_args.conf)
        except TypeError:
            raise error.BadDataException(
                'VM configuration should be a dictionary '
                'or a list of dictionaries')
        data = self.client.node_vms_create(parsed_args.id, confs)
        msg = "{0}".format(data)
        self.app.stdout.write(msg)


class NodeLabelList(NodeMixIn, base.BaseListCommand):
    """Show list of all labels."""

    columns = (
        'node_id',
        'label_name',
        'label_value')

    def get_parser(self, prog_name):
        parser = super(NodeLabelList, self).get_parser(prog_name)

        parser.add_argument(
            '-n',
            '--nodes',
            nargs='+',
            help='Show labels for specific nodes')

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all_labels_for_nodes(
            node_ids=parsed_args.nodes)
        data = data_utils.get_display_data_multi(self.columns, data)

        return (self.columns, data)


class NodeLabelSet(NodeMixIn, base.BaseCommand):
    """Create or update specifc labels on nodes."""

    def get_parser(self, prog_name):
        parser = super(NodeLabelSet, self).get_parser(prog_name)

        parser.add_argument(
            '-l',
            '--labels',
            required=True,
            nargs='+',
            help='List of labels for create or update')

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-n',
            '--nodes',
            nargs='+',
            help='Create or update labels only for specific nodes')
        group.add_argument(
            '--nodes-all',
            action='store_true',
            help='Create or update labels for all nodes')

        return parser

    def take_action(self, parsed_args):
        nodes_ids = None if parsed_args.nodes_all else parsed_args.nodes
        data = self.client.set_labels_for_nodes(
            labels=parsed_args.labels, node_ids=nodes_ids)
        msg = "Labels have been updated on nodes: {0} \n".format(
            ','.join(data))
        self.app.stdout.write(msg)


class NodeLabelDelete(NodeMixIn, base.BaseCommand):
    """Delete specific labels on nodes."""

    def get_parser(self, prog_name):
        parser = super(NodeLabelDelete, self).get_parser(prog_name)

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-l',
            '--labels',
            nargs='+',
            help='List of labels keys for delete')
        group.add_argument(
            '--labels-all',
            action='store_true',
            help='Delete all labels for node')

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-n',
            '--nodes',
            nargs='+',
            help='Delete labels only for specific nodes')
        group.add_argument(
            '--nodes-all',
            action='store_true',
            help='Delete labels for all nodes')

        return parser

    def take_action(self, parsed_args):
        nodes_ids = None if parsed_args.nodes_all else parsed_args.nodes
        labels = None if parsed_args.labels_all \
            else parsed_args.labels
        data = self.client.delete_labels_for_nodes(
            labels=labels, node_ids=nodes_ids)
        msg = "Labels have been deleted on nodes: {0} \n".format(
            ','.join(data))
        self.app.stdout.write(msg)


class NodeAttributesDownload(NodeMixIn, base.BaseCommand):
    """Download node attributes."""

    def get_parser(self, prog_name):
        parser = super(NodeAttributesDownload, self).get_parser(prog_name)

        parser.add_argument(
            'id', type=int, help='Node ID')
        parser.add_argument(
            '--dir', type=str, help='Directory to save attributes')

        return parser

    def take_action(self, parsed_args):
        file_path = self.client.download_attributes(
            parsed_args.id, parsed_args.dir)
        self.app.stdout.write(
            "Attributes for node {0} were written to {1}"
            .format(parsed_args.id, file_path) + os.linesep)


class NodeAttributesUpload(NodeMixIn, base.BaseCommand):
    """Upload node attributes."""

    def get_parser(self, prog_name):
        parser = super(NodeAttributesUpload, self).get_parser(prog_name)

        parser.add_argument(
            'id', type=int, help='Node ID')
        parser.add_argument(
            '--dir', type=str, help='Directory to read attributes from')

        return parser

    def take_action(self, parsed_args):
        self.client.upload_attributes(parsed_args.id, parsed_args.dir)
        self.app.stdout.write(
            "Attributes for node {0} were uploaded."
            .format(parsed_args.id) + os.linesep)


class NodeAnsibleInventory(NodeMixIn, base.BaseCommand):
    """Generate ansible inventory file based on the nodes list."""

    def get_parser(self, prog_name):
        parser = super(NodeAnsibleInventory, self).get_parser(prog_name)

        # if this is a required argument, we'll avoid ambiguity of having nodes
        # of multiple different clusters in the same inventory file
        parser.add_argument(
            '-e',
            '--env',
            type=int,
            required=True,
            help='Use only nodes that are in the specified environment')

        parser.add_argument(
            '-l',
            '--labels',
            type=utils.str_to_unicode,
            nargs='+',
            help='Use only nodes that have specific labels')

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all(environment_id=parsed_args.env,
                                   labels=parsed_args.labels)

        nodes_by_role = collections.defaultdict(list)
        for node in data:
            for role in node['roles']:
                nodes_by_role[role].append(node)

        for role, nodes in sorted(nodes_by_role.items()):
            self.app.stdout.write(u'[{role}]\n'.format(role=role))
            self.app.stdout.write(
                u'\n'.join(
                    u'{name} ansible_host={ip}'.format(name=node['hostname'],
                                                       ip=node['ip'])
                    for node in sorted(nodes_by_role[role],
                                       key=operator.itemgetter('hostname'))
                )
            )
            self.app.stdout.write(u'\n\n')


class NodeInterfacesDownload(NodeMixIn, base.BaseCommand):
    """Download and store configuration of interfaces for a node to a file."""

    def get_parser(self, prog_name):
        parser = super(NodeInterfacesDownload, self).get_parser(prog_name)
        parser.add_argument('id',
                            type=int,
                            help='Id of a node.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized interfaces data.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            help='Destination directory.')

        return parser

    def take_action(self, parsed_args):
        directory = parsed_args.directory or os.curdir
        interfaces_conf = self.client.get_interfaces(parsed_args.id)
        file_path = self.get_attributes_path('interfaces',
                                             parsed_args.format,
                                             parsed_args.id,
                                             directory)

        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format,
                                     stream,
                                     interfaces_conf)
        except (OSError, IOError):
            msg = 'Could not store configuration of interfaces at {}.'
            raise error.InvalidFileException(msg.format(file_path))

        msg = ('Configuration of interfaces for node with id '
               '{node} was stored in {path}\n')
        self.app.stdout.write(msg.format(node=parsed_args.id, path=file_path))


class NodeInterfacesGetDefault(NodeMixIn, base.BaseCommand):
    """Download default configuration of interfaces for a node to a file."""

    def get_parser(self, prog_name):
        parser = super(NodeInterfacesGetDefault, self).get_parser(prog_name)
        parser.add_argument('id',
                            type=int,
                            help='Id of a node.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized interfaces data.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            help='Destination directory.')

        return parser

    def take_action(self, parsed_args):
        directory = parsed_args.directory or os.curdir
        interfaces_conf = self.client.get_default_interfaces(parsed_args.id)
        file_path = self.get_attributes_path('interfaces',
                                             parsed_args.format,
                                             parsed_args.id,
                                             directory)

        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format,
                                     stream,
                                     interfaces_conf)
        except (OSError, IOError):
            msg = 'Could not store default configuration of interfaces at {}.'
            raise error.InvalidFileException(msg.format(file_path))

        msg = ('Default configuration of interfaces for node with id '
               '{node} was stored in {path}\n')
        self.app.stdout.write(msg.format(node=parsed_args.id, path=file_path))


class NodeInterfacesUpload(NodeMixIn, base.BaseCommand):
    """Upload stored configuration of interfaces for a node from a file."""

    def get_parser(self, prog_name):
        parser = super(NodeInterfacesUpload, self).get_parser(prog_name)
        parser.add_argument('id',
                            type=int,
                            help='Id of a node.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized interfaces data.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            help='Source directory.')

        return parser

    def take_action(self, parsed_args):
        directory = parsed_args.directory or os.curdir

        file_path = self.get_attributes_path('interfaces',
                                             parsed_args.format,
                                             parsed_args.id,
                                             directory)

        try:
            with open(file_path, 'r') as stream:
                interfaces_conf = data_utils.safe_load(parsed_args.format,
                                                       stream)
                self.client.set_interfaces(parsed_args.id, interfaces_conf)
        except (OSError, IOError):
            msg = 'Could not read configuration of interfaces at {}.'
            raise error.InvalidFileException(msg.format(file_path))

        msg = ('Configuration of interfaces for node with id '
               '{node} was loaded from {path}\n')
        self.app.stdout.write(msg.format(node=parsed_args.id, path=file_path))
