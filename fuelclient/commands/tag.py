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
from cliff import show
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
    fields_mapper = (
        ('env', 'clusters'),
        ('release', 'releases'),
        ('plugin', 'plugins'),
    )

    def parse_model(self, args):
        for param, tag_class in self.fields_mapper:
            model_id = getattr(args, param)
            if model_id:
                return tag_class, model_id

    @staticmethod
    def check_file_path(file_path):
        if not utils.file_exists(file_path):
            raise argparse.ArgumentTypeError(
                'File "{0}" does not exist.'.format(file_path))
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


class TagShow(TagMixIn, base.BaseShowCommand):
    """Show single tag by id."""
    columns = ("id", "tag", "has_primary")


class TagList(TagMixIn, base.BaseListCommand):
    """Show list of available tags for release, cluster or plugin."""
    columns = TagShow.columns

    def get_parser(self, prog_name):
        parser = super(TagList, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-r',
            '--release',
            type=int,
            help='release id')
        group.add_argument(
            '-e',
            '--env',
            type=int,
            help='environment id')
        group.add_argument(
            '-p',
            '--plugin',
            type=int,
            help='plugin id')

        return parser

    def take_action(self, parsed_args):
        model, model_id = self.parse_model(parsed_args)
        data = self.client.get_all(model, model_id)
        display_data = data_utils.get_display_data_multi(self.columns, data)
        return self.columns, display_data


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
               " was stored in {}\n".format(parsed_args.tag_id,
                                            file_path))
        self.app.stdout.write(msg)


@six.add_metaclass(abc.ABCMeta)
class BaseTagUpdater(TagMixIn, base.BaseShowCommand):
    """Update a tag from file description."""
    columns = TagShow.columns

    @abc.abstractmethod
    def upload(self, parsed_args, data):
        """String with the name of the action."""
        pass

    def get_parser(self, prog_name):
        parser = show.ShowOne.get_parser(self, prog_name)
        parser.add_argument(
            '--file_path',
            required=True,
            type=self.check_file_path,
            help="Full path to the file in {} format that contains tag's "
                 "data.".format("/".join(self.supported_file_formats)))

        return parser

    def take_action(self, parsed_args):
        file_path = parsed_args.file_path
        file_format = os.path.splitext(file_path)[1].lstrip('.')
        if file_format not in self.supported_file_formats:
            raise argparse.ArgumentTypeError(
                "File format '{}' is not supported.".format(file_format))

        data = self.read_tag_data(file_format, file_path)
        display_data = data_utils.get_display_data_single(
            self.columns,
            self.upload(parsed_args, data))

        return self.columns, display_data


class TagUpdate(BaseTagUpdater):
    """Update a tag from file description."""

    def upload(self, parsed_args, data):
        return self.client.update(parsed_args.tag_id, data)

    def get_parser(self, prog_name):
        parser = super(TagUpdate, self).get_parser(prog_name)
        parser.add_argument(
            '-t',
            '--tag_id',
            type=int,
            required=True,
            help='Id of the tag.')

        return parser


class TagCreate(BaseTagUpdater):
    """Create a tag from file description."""

    def upload(self, parsed_args, data):
        model, model_id = self.parse_model(parsed_args)
        return self.client.create(model, model_id, data)

    def get_parser(self, prog_name):
        parser = super(TagCreate, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-r',
            '--release',
            type=int,
            help='release id')
        group.add_argument(
            '-e',
            '--env',
            type=int,
            help='environment id')
        group.add_argument(
            '-p',
            '--plugin',
            type=int,
            help='plugin id')

        return parser


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
