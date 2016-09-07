# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

import os

from fuelclient.cli.serializers import Serializer
from fuelclient.commands import base
from fuelclient.common import data_utils


class SequenceMixIn(object):
    entity_name = 'sequences'


class SequenceCreate(SequenceMixIn, base.show.ShowOne, base.BaseCommand):
    """Create a new deployment sequence."""

    columns = ("id", "name")

    def get_parser(self, prog_name):
        parser = super(SequenceCreate, self).get_parser(prog_name)
        sub_parser = parser.add_mutually_exclusive_group(required=True)

        sub_parser.add_argument(
            '-f', '--file',
            help='YAML file that contains deployment sequence data.'
        )
        group = sub_parser.add_argument_group()
        group.add_argument(
            '-n', '--name',
            required=True,
            help='The unique name for sequence'
        )
        group.add_argument(
            '-t', '--graph-type',
            dest='graph_types',
            nargs='+',
            required=True,
            help='Graph types, which will be included to sequence.\n'
                 'Note: Order is important'
        )
        return parser

    def take_action(self, args):
        if args.file:
            new_sequence = self.client.create_from(
                Serializer().read_from_full_path(args.file)
            )
        else:
            new_sequence = self.client.create(args.name, args.graph_types)

        self.app.stdout.write("Sequence was successfully created:\n")
        data = data_utils.get_display_data_single(self.columns, new_sequence)

        return self.columns, data


class SequenceUpdate(SequenceMixIn, base.BaseShowCommand):
    """Update existing sequence"""

    columns = ("id", "name")

    def get_parser(self, prog_name):
        parser = super(SequenceUpdate, self).get_parser(prog_name)
        sub_parser = parser.add_mutually_exclusive_group(required=False)
        sub_parser.add_argument(
            '-f', '--file',
            help='YAML file that contains deployment sequence data.'
        )
        group = sub_parser.add_argument_group()
        group.add_argument(
            '-n', '--name',
            required=False,
            help='The unique name for sequence'
        )
        group.add_argument(
            '-t', '--graph-type',
            dest='graph_types',
            nargs='+',
            required=False,
            help='Graph types, which will be included to sequence.\n'
                 'Note: Order is important'
        )
        return parser

    def take_action(self, args):
        if args.file:
            sequence = self.client.update_from(
                args.id, Serializer().read_from_full_path(args.file)
            )
        else:
            sequence = self.client.update(
                args.id, name=args.name, graph_types=args.graph_types
            )

        if sequence:
            self.app.stdout.write("Sequence was successfully updated:\n")
            data = data_utils.get_display_data_single(self.columns, sequence)
            return self.columns, data
        else:
            self.app.stdout.write("Nothing to update.\n")


class SequenceDelete(SequenceMixIn, base.BaseDeleteCommand):
    """Delete existing sequence"""


class SequenceShow(SequenceMixIn, base.BaseShowCommand):
    """Display information about sequence"""
    columns = ("id", "name", "graphs")


class SequenceList(SequenceMixIn, base.BaseListCommand):
    """Delete existing sequence"""
    columns = ("id", "name")


class SequenceExecute(SequenceMixIn, base.BaseCommand):
    """Executes sequence on specified cluster."""

    def get_parser(self, prog_name):
        parser = super(SequenceExecute, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            type=int,
            required=True,
            help='Id of the Sequence.'
        )
        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='Id of the environment'
        )
        parser.add_argument(
            '-d', '--dry-run',
            action="store_true",
            required=False,
            default=False,
            help='Specifies to dry-run a deployment by configuring '
                 'task executor to dump the deployment graph to a dot file.')
        parser.add_argument(
            '-f', '--force',
            action="store_true",
            required=False,
            default=False,
            help='Force run all deployment tasks '
                 'without evaluating conditions.'
        )
        parser.add_argument(
            '--noop',
            action="store_true",
            required=False,
            default=False,
            help='Specifies noop-run deployment configuring '
            'tasks executor to run puppet and shell tasks in '
            'noop mode and skip all other. Stores noop-run '
            'result summary in nailgun database.'
        )
        return parser

    def take_action(self, args):
        result = self.client.execute(
            sequence_id=args.id,
            env_id=args.env,
            dry_run=args.dry_run,
            noop_run=args.noop,
            force=args.force
        )
        msg = 'Deployment task with id {t} for the environment {e} ' \
              'has been started.\n'.format(t=result.data['id'],
                                           e=result.data['cluster'])
        self.app.stdout.write(msg)
