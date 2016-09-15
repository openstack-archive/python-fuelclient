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

import abc
import argparse
import os

from oslo_utils import fileutils
import six

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient import utils


class TagMixIn(object):

    entity_name = 'tag'
    supported_file_formats = ('json', 'yaml')

    @staticmethod
    def check_file_path(file_path):
        if not utils.file_exists(file_path):
            raise argparse.ArgumentTypeError(
                'File "{0}" does not exist'.format(file_path))
        return file_path

    @staticmethod
    def get_file_path(directory, tag_id, file_format):
        return os.path.join(os.path.abspath(directory),
                            'tag_{}.{}'.format(tag_id, file_format))

    @staticmethod
    def read_tag_data(file_format, file_path):
        try:
            with open(file_path, 'r') as stream:
                data = data_utils.safe_load(file_format, stream)
        except (OSError, IOError):
            msg = "Could not read tag's description at {}.".format(file_path)
            raise error.InvalidFileException(msg)
        return data


class TagList(TagMixIn, base.BaseListCommand):
    """Show list of all available tags."""

    columns = ("id",
               "tag",
               "owner_type",
               "owner_id")


class TagDownload(TagMixIn, base.BaseCommand):
    """Download full tag description to file."""

    def get_parser(self, prog_name):
        parser = super(TagDownload, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tag_id',
                            type=int,
                            required=True,
                            help='Id of the tag.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized tag description.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.path.curdir,
                            help='Destination. Defaults to '
                                 'the current directory.')
        return parser

    def take_action(self, parsed_args):
        file_path = self.get_file_path(parsed_args.directory,
                                       parsed_args.tag_id,
                                       parsed_args.format)
        data = self.client.get_by_id(parsed_args.tag_id)
        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format, stream, data)
        except (OSError, IOError):
            msg = ("Could not store description data "
                   "for tag {} at {}".format(parsed_args.tag_id, file_path))
            raise error.InvalidFileException(msg)

        msg = ("Description data of tag with id '{}'"
               "was stored in {}\n".format(parsed_args.tag_id,
                                           file_path))
        self.app.stdout.write(msg)


class TagUpdate(TagMixIn, base.BaseCommand):
    """Update a tag from file description."""

    def get_parser(self, prog_name):
        parser = super(TagUpdate, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tag_id',
                            type=int,
                            required=True,
                            help='Id of the tag.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized tag description.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.path.curdir,
                            help='Source directory. Defaults to '
                                 'the current directory.')
        return parser

    def take_action(self, parsed_args):
        file_path = self.get_file_path(parsed_args.directory,
                                       parsed_args.tag_id,
                                       parsed_args.format)

        data = self.read_tag_data(parsed_args.format, file_path)
        self.client.update(parsed_args.tag_id, data)

        msg = ("Description of tag with id {} was updated from"
               "{}.\n".format(parsed_args.tag_id, file_path))
        self.app.stdout.write(msg)


class TagCreate(TagMixIn, base.BaseCommand):
    """Create a tag from file description."""

    def get_parser(self, prog_name):
        parser = super(TagCreate, self).get_parser(prog_name)
        parser.add_argument(
            '-f',
            '--file_path',
            required=True,
            type=self.check_file_path,
            help="Full path to the file in {} format that contains tag's "
                 "data.".format("/".join(self.supported_file_formats))
        )
        return parser

    def take_action(self, parsed_args):
        file_path = parsed_args.file_path
        file_format = os.path.splitext(file_path)[1].lstrip('.')

        data = self.read_tag_data(file_format, file_path)
        self.client.create(data)

        msg = ("Description of tag was created from "
               " {file_path}.\n".format(file_path=file_path))
        self.app.stdout.write(msg)


class TagDelete(base.BaseDeleteCommand):
    """Delete a tag by id."""

    entity_name = 'tag'


@six.add_metaclass(abc.ABCMeta)
class BaseTagAssignee(TagMixIn, base.BaseCommand):
    """Base class for tags assignment."""

    @abc.abstractproperty
    def action(self):
        """String with the name of the action."""
        pass

    @abc.abstractproperty
    def assignee(self):
        """Assignment method."""
        pass

    def get_parser(self, prog_name):
        parser = super(BaseTagAssignee, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tags',
                            type=str,
                            nargs='+',
                            required=True,
                            help='List of tags to be {} '
                                 'node.'.format(self.action))

        parser.add_argument('-n',
                            '--node',
                            type=int,
                            required=True,
                            help='Id of the node.')

        return parser

    def take_action(self, parsed_args):
        self.assignee(node=parsed_args.node,
                      tag_ids=parsed_args.tags)

        self.app.stdout.write('Tags {t} were {a} the node {n}.'
                              '\n'.format(t=parsed_args.tags,
                                          a=self.action,
                                          n=parsed_args.node))


class TagAssign(BaseTagAssignee):
    """Assign tags to the node."""

    action = 'assigned to'

    @property
    def assignee(self):
        return self.client.assign


class TagUnassign(BaseTagAssignee):
    """Unassign tags from the node."""

    action = 'unassigned from'

    @property
    def assignee(self):
        return self.client.unassign
