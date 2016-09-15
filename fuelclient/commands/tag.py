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
import os

from oslo_utils import fileutils
import six

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils


class TagMixIn(object):

    entity_name = 'tag'
    supported_file_formats = ('json', 'yaml')

    @staticmethod
    def get_file_path(directory, tag_id, file_format):
        return os.path.join(os.path.abspath(directory),
                            'tag_{}.{}'.format(tag_id, file_format))


@six.add_metaclass(abc.ABCMeta)
class BaseUploadCommand(TagMixIn, base.BaseCommand):
    """Base class for uploading metadata of a tag."""

    @abc.abstractproperty
    def action(self):
        """String with the name of the action."""
        pass

    def upload(self, data, parsed_args):
        """Base Method for uploading data."""
        pass

    def process_data(self, file_path, parsed_args):
        """Base method for uploading data."""
        with open(file_path, 'r') as stream:
            data = data_utils.safe_load(parsed_args.format, stream)
            self.upload(data, parsed_args)

    def get_command_file_path(self, parsed_args):
        return self.get_file_path(parsed_args.directory,
                                  parsed_args.tag_id,
                                  parsed_args.format)

    def get_parser(self, prog_name):
        parser = super(BaseUploadCommand, self).get_parser(prog_name)
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
                            help='Destination/Source directory. Defaults to '
                                 'the current directory.')
        return parser

    def take_action(self, parsed_args):
        file_path = self.get_command_file_path(parsed_args)

        try:
            self.process_data(file_path, parsed_args)
        except (OSError, IOError):
            msg = "Could not read tag's description at {}.".format(file_path)
            raise error.InvalidFileException(msg)

        msg = ("Description of tag was {action}"
               " {file_path}.\n".format(action=self.action,
                                        file_path=file_path))
        self.app.stdout.write(msg)


class TagList(TagMixIn, base.BaseListCommand):
    """Show list of all available tags."""

    columns = ("id",
               "tag",
               "owner_type",
               "owner_id")


class TagDownload(BaseUploadCommand):
    """Download full tag description to file."""
    action = "downloaded to"

    def process_data(self, file_path, parsed_args):
        data = self.client.get_by_id(parsed_args.tag_id)

        fileutils.ensure_tree(os.path.dirname(file_path))
        fileutils.delete_if_exists(file_path)

        with open(file_path, 'w') as stream:
            data_utils.safe_dump(parsed_args.format, stream, data)


class TagUpdate(BaseUploadCommand):
    """Update a tag from file description."""

    action = "updated from"

    def upload(self, data, parsed_args):
        return self.client.update(data, tag_id=parsed_args.tag_id)


class TagCreate(BaseUploadCommand):
    """Create a tag from file description."""

    action = "created from"

    def get_command_file_path(self, parsed_args):
        return parsed_args.file_path

    def upload(self, data, parsed_args):
        return self.client.create(data)

    def get_parser(self, prog_name):
        parser = super(BaseUploadCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-p',
            '--file_path',
            required=True,
            help="Full path to the file that contains tag's data."
        )
        parser.add_argument(
            '-f',
            '--format',
            required=True,
            choices=self.supported_file_formats,
            help='Format of serialized tag description.')
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
                            help='List of tags to {}.'.format(self.action))

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
