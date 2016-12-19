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

import abc
import os

from cliff import command
from cliff import lister
from cliff import show
import six

import fuelclient
from fuelclient.cli.serializers import Serializer
from fuelclient.common import data_utils

VERSION = 'v1'


@six.add_metaclass(abc.ABCMeta)
class BaseCommand(command.Command):
    """Base Fuel Client command."""

    def get_attributes_path(self, attr_type, file_format, ent_id, directory):
        """Returnes a path for attributes of an entity

        :param attr_type:   Type of the attribute, e. g., disks, networks.
        :param file_format: The format of the file that contains or will
                            contain the attributes, e. g.,  json or yaml.
        :param ent_id:      Id of an entity
        :param directory:   Directory that is used to store attributes.

        """
        if attr_type not in self.allowed_attr_types:
            raise ValueError('attr_type must be '
                             'one of {}'.format(self.allowed_attr_types))

        if file_format not in self.supported_file_formats:
            raise ValueError('file_format must be '
                             'one of {}'.format(self.supported_file_formats))

        return os.path.join(os.path.abspath(directory),
                            '{ent}_{id}'.format(ent=self.entity_name,
                                                id=ent_id),
                            '{}.{}'.format(attr_type, file_format))

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.client = fuelclient.get_client(self.entity_name, VERSION)

    @abc.abstractproperty
    def entity_name(self):
        """Name of the Fuel entity."""
        pass

    @property
    def supported_file_formats(self):
        raise NotImplementedError()

    @property
    def allowed_attr_types(self):
        raise NotImplementedError()


@six.add_metaclass(abc.ABCMeta)
class BaseListCommand(lister.Lister, BaseCommand):
    """Lists all entities showing some information."""

    filters = {}

    @property
    def default_sorting_by(self):
        return ['id']

    @abc.abstractproperty
    def columns(self):
        """Names of columns in the resulting table."""
        pass

    def get_parser(self, prog_name):
        parser = super(BaseListCommand, self).get_parser(prog_name)

        # Add sorting key argument to the output formatters group
        # if it exists. If not -- add is to the general group.
        matching_groups = (gr
                           for gr in parser._action_groups
                           if gr.title == 'output formatters')

        group = next(matching_groups, None) or parser

        group.add_argument('-s',
                           '--sort-columns',
                           type=str,
                           nargs='+',
                           choices=self.columns,
                           metavar='SORT_COLUMN',
                           default=self.default_sorting_by,
                           help='Space separated list of keys for sorting '
                                'the data. Defaults to {}. Wrong values '
                                'are ignored.'.format(
                                    ', '.join(self.default_sorting_by)))

        return parser

    def _sort_data(self, parsed_args, data):
        scolumn_ids = [self.columns.index(col)
                       for col in parsed_args.sort_columns]
        data.sort(key=lambda x: [x[scolumn_id] for scolumn_id in scolumn_ids])
        return data

    def take_action(self, parsed_args):
        filters = {}
        for name, prop in self.filters.items():
            value = getattr(parsed_args, prop, None)
            if value is not None:
                filters[name] = value

        data = self.client.get_all(**filters)
        data = data_utils.get_display_data_multi(self.columns, data)
        data = self._sort_data(parsed_args, data)

        return self.columns, data


@six.add_metaclass(abc.ABCMeta)
class BaseShowCommand(show.ShowOne, BaseCommand):
    """Shows detailed information about the entity."""

    @abc.abstractproperty
    def columns(self):
        """Names of columns in the resulting table."""
        pass

    def get_parser(self, prog_name):
        parser = super(BaseShowCommand, self).get_parser(prog_name)

        parser.add_argument('id', type=int,
                            help='Id of the {0}.'.format(self.entity_name))

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_by_id(parsed_args.id)
        data = data_utils.get_display_data_single(self.columns, data)

        return (self.columns, data)


@six.add_metaclass(abc.ABCMeta)
class BaseDeleteCommand(BaseCommand):
    """Deletes entity with the specified id."""

    def get_parser(self, prog_name):
        parser = super(BaseDeleteCommand, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='Id of the {0} to delete.'.format(self.entity_name))

        return parser

    def take_action(self, parsed_args):
        self.client.delete_by_id(parsed_args.id)

        msg = '{ent} with id {ent_id} was deleted\n'

        self.app.stdout.write(
            msg.format(
                ent=self.entity_name.capitalize(),
                ent_id=parsed_args.id))


@six.add_metaclass(abc.ABCMeta)
class BaseTasksExecuteCommand(BaseCommand):

    def get_parser(self, prog_name):
        parser = super(BaseTasksExecuteCommand, self).get_parser(prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='Id of the environment'
        )
        parser.add_argument(
            '--force',
            action="store_true",
            default=False,
            help='Force run all deployment tasks without skipping.')

        parser.add_argument(
            '--trace',
            action="store_true",
            default=False,
            help='Enable debugging mode in tasks executor.'
        )
        parser.add_argument(
            '--format',
            choices=['json', 'yaml'],
            help='Select output format, by default text message will produce.'
        )

        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            '--dry-run',
            action="store_true",
            default=False,
            help='Specifies to dry-run a deployment by configuring '
                 'task executor to dump the deployment graph to a dot file.'
        )
        mode_group.add_argument(
            '--noop',
            action="store_true",
            default=False,
            help='Specifies noop-run deployment configuring tasks executor '
                 'to run all tasks in noop mode. '
                 'Execution result summary can be got via history of tasks.')

        return parser

    def take_action(self, parsed_args):
        task = self.client.execute(
            env_id=parsed_args.env,
            dry_run=parsed_args.dry_run,
            noop_run=parsed_args.noop,
            force=parsed_args.force,
            debug=parsed_args.trace,
            **self.get_options(parsed_args)
        )
        if parsed_args.format:
            msg = Serializer(parsed_args.format).serialize(task.data) + '\n'
        else:
            msg = (
                'Deployment task with id {0} for the environment {1} '
                'has been started.\n'
                .format(task.data['id'], task.data['cluster'])
            )
        self.app.stdout.write(msg)

    def get_options(self, parsed_args):
        """Produce additional options from cmdline arguments."""
        raise NotImplementedError
