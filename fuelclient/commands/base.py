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

from cliff import command
from cliff import lister
from cliff import show
import six

import fuelclient
from fuelclient.common import data_utils


VERSION = 'v1'


@six.add_metaclass(abc.ABCMeta)
class BaseCommand(command.Command):
    """Base Fuel Client command."""

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.client = fuelclient.get_client(self.entity_name, VERSION)

    @abc.abstractproperty
    def entity_name(self):
        """Name of the Fuel entity."""
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseListCommand(lister.Lister, BaseCommand):
    """Lists all entities showing some information."""

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
                           default=['id'],
                           help='Space separated list of keys for sorting '
                                'the data. Defaults to id. Wrong values '
                                'are ignored.')

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all()
        data = data_utils.get_display_data_multi(self.columns, data)

        scolumn_ids = [self.columns.index(col)
                       for col in parsed_args.sort_columns]

        data.sort(key=lambda x: [x[scolumn_id] for scolumn_id in scolumn_ids])

        return (self.columns, data)


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
