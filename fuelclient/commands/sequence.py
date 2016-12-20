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

from fuelclient.cli import serializers
from fuelclient.commands import base
from fuelclient.common import data_utils


class SequenceMixIn(object):
    entity_name = 'sequence'


class SequenceCreate(SequenceMixIn, base.show.ShowOne, base.BaseCommand):
    """Create a new deployment sequence."""

    columns = ("id", "release_id", "name")

    def get_parser(self, prog_name):
        parser = super(SequenceCreate, self).get_parser(prog_name)

        parser.add_argument(
            "-r", "--release",
            type=int,
            required=True,
            help="Release object id, sequence will be linked to."
        )
        parser.add_argument(
            '-n', '--name',
            required=True,
            help='The unique name for sequence.'
        )
        parser.add_argument(
            '-t', '--graph-type',
            dest='graph_types',
            nargs='+',
            required=True,
            help='Graph types, which will be included to sequence.\n'
                 'Note: Order is important.'
        )
        return parser

    def take_action(self, args):
        new_sequence = self.client.create(
            args.release, args.name, args.graph_types
        )
        self.app.stdout.write("Sequence was successfully created:\n")
        data = data_utils.get_display_data_single(self.columns, new_sequence)

        return self.columns, data


class SequenceUpload(SequenceMixIn, base.show.ShowOne, base.BaseCommand):
    """Upload a new deployment sequence."""

    columns = ("id", "release_id", "name")

    def get_parser(self, prog_name):
        parser = super(SequenceUpload, self).get_parser(prog_name)

        parser.add_argument(
            "-r", "--release",
            type=int,
            required=True,
            help="Release object id, sequence will be linked to."
        )
        parser.add_argument(
            '--file',
            required=True,
            help='YAML file which contains deployment sequence properties.'
        )
        return parser

    def take_action(self, args):
        serializer = serializers.FileFormatBasedSerializer()
        new_sequence = self.client.upload(
            args.release, serializer.read_from_file(args.file)
        )
        self.app.stdout.write("Sequence was successfully created:\n")
        data = data_utils.get_display_data_single(self.columns, new_sequence)
        return self.columns, data


class SequenceDownload(SequenceMixIn, base.BaseCommand):
    """Download deployment sequence data."""

    def get_parser(self, prog_name):
        parser = super(SequenceDownload, self).get_parser(prog_name)

        parser.add_argument(
            "id",
            type=int,
            help="Sequence ID."
        )
        parser.add_argument(
            '--file',
            help='The file path where data will be saved.'
        )
        return parser

    def take_action(self, args):
        data = self.client.download(args.id)
        if args.file:
            serializer = serializers.FileFormatBasedSerializer()
            serializer.write_to_file(args.file, data)
        else:
            serializer = serializers.Serializer("yaml")
            serializer.write_to_file(self.app.stdout, data)


class SequenceUpdate(SequenceMixIn, base.BaseShowCommand):
    """Update existing sequence."""

    columns = ("id", "name")

    def get_parser(self, prog_name):
        parser = super(SequenceUpdate, self).get_parser(prog_name)
        parser.add_argument(
            '-n', '--name',
            required=False,
            help='The unique name for sequence.'
        )
        parser.add_argument(
            '-t', '--graph-type',
            dest='graph_types',
            nargs='+',
            required=False,
            help='Graph types, which will be included to sequence.\n'
                 'Note: Order is important.'
        )
        return parser

    def take_action(self, args):
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
    """Delete existing sequence."""


class SequenceShow(SequenceMixIn, base.BaseShowCommand):
    """Display information about sequence."""
    columns = ("id", "release_id", "name", "graphs")


class SequenceList(SequenceMixIn, base.BaseListCommand):
    """Show list of all existing sequences."""
    columns = ("id", "release_id", "name")
    filters = {'release': 'release', 'cluster': 'env'}

    def get_parser(self, prog_name):
        parser = super(SequenceList, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-r', '--release',
            type=int,
            help='The Release object ID.'
        )
        group.add_argument(
            '-e', '--env',
            type=int,
            help='The environment object id.'
        )
        return parser


class SequenceExecute(SequenceMixIn, base.BaseTasksExecuteCommand):
    """Executes sequence on specified environment."""

    def get_parser(self, prog_name):
        parser = super(SequenceExecute, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            type=int,
            help='Id of the Sequence.'
        )
        return parser

    def get_options(self, parsed_args):
        return {
            'sequence_id': parsed_args.id,
        }
