# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

    @abc.abstractmethod
    def upload(self, data, parsed_args):
        """Method for uploading data."""
        pass

    @abc.abstractmethod
    def get_command_file_path(self, parsed_args):
        """Method for generating path to file."""
        pass

    def get_parser(self, prog_name):
        parser = super(BaseUploadCommand, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tag_id',
                            type=int,
                            required=True,
                            help='Id of the tag')
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
        file_path = self.get_command_file_path(parsed_args)

        try:
            with open(file_path, 'r') as stream:
                data = data_utils.safe_load(parsed_args.format, stream)
                self.upload(data, parsed_args)
        except (OSError, IOError):
            msg = "Could not read tag's description at {}".format(file_path)
            raise error.InvalidFileException(msg)

        msg = ("Description of tag was {action}d from"
               "{file_path}\n".format(action=self.action,
                                      file_path=file_path))
        self.app.stdout.write(msg)


class TagList(TagMixIn, base.BaseListCommand):
    """Show list of all available tags for release."""

    columns = ("id",
               "tag",
               "owner_type",
               "owner_id")

    def get_parser(self, prog_name):
        parser = super(TagList, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--owner_type',
                            type=str,
                            choices=['release', 'environment', 'plugin'],
                            help='Owner of the tag')

        parser.add_argument('-i',
                            '--owner_id',
                            type=int,
                            help='Owner id')

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all(owner_type=parsed_args.owner_type,
                                   owner_id=parsed_args.owner_id)

        data = data_utils.get_display_data_multi(self.columns, data)
        return self.columns, data


class TagDownload(TagMixIn, base.BaseCommand):
    """Download full tag description to file."""

    def get_parser(self, prog_name):
        parser = super(TagDownload, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tag_id',
                            type=int,
                            required=True,
                            help='Id of the tag')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized tag description.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.path.curdir,
                            help='Destination directory. Defaults to '
                                 'the current directory.')
        return parser

    def take_action(self, parsed_args):
        file_path = self.get_file_path(parsed_args.directory,
                                       parsed_args.tag_id,
                                       parsed_args.format)
        data = self.client.get_one(parsed_args.tag_id)
        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format, stream, data)
        except (OSError, IOError):
            msg = ("Could not store description data "
                   "for tag {} at {}".format(parsed_args.tag_id, file_path))
            raise error.InvalidFileException(msg)

        msg = ("Description data of tag '{}'"
               "was stored in {}\n".format(parsed_args.tag_id,
                                           file_path))
        self.app.stdout.write(msg)


class TagUpload(BaseUploadCommand):
    """Update a tag from file description."""

    action = "upload"

    def upload(self, data, parsed_args):
        return self.client.upload(data, parsed_args.tag_id)

    def get_command_file_path(self, parsed_args):
        return self.get_file_path(parsed_args.directory,
                                  parsed_args.tag_id,
                                  parsed_args.format)


class TagCreate(BaseUploadCommand):
    """Create a tag from file description"""

    action = "create"

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
            default=None,
            help="Full path to the YAML file that contains tag's data."
        )
        parser.add_argument(
            '-f',
            '--format',
            required=True,
            choices=self.supported_file_formats,
            help='Format of serialized tag description.')
        return parser


class TagDelete(TagMixIn, base.BaseCommand):
    """Delete a tag by id"""

    def get_parser(self, prog_name):
        parser = super(TagDelete, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tag_id',
                            type=int,
                            required=True,
                            help='Id of the tag')
        return parser

    def take_action(self, parsed_args):
        self.client.delete(parsed_args.tag_id)

        msg = "Tag '{}' was deleted\n".format(parsed_args.tag_id)
        self.app.stdout.write(msg)


class TagAssign(TagMixIn, base.BaseCommand):
    """Assign tags to the node."""

    def get_parser(self, prog_name):
        parser = super(TagAssign, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tags',
                            type=str,
                            nargs='+',
                            required=True,
                            help='Target tags of the node.')

        parser.add_argument('-n',
                            '--node',
                            type=int,
                            required=True,
                            help='Id of the node for assignment.')

        return parser

    def take_action(self, parsed_args):
        self.client.assign(node=parsed_args.node,
                           tag_ids=parsed_args.tags)

        msg = 'Tags {t} were assigned to the node {n}\n'
        self.app.stdout.write(msg.format(t=parsed_args.tags,
                                         n=parsed_args.node))


class TagUnassign(TagMixIn, base.BaseCommand):
    """Unassign tags from the node."""

    def get_parser(self, prog_name):
        parser = super(TagUnassign, self).get_parser(prog_name)
        parser.add_argument('-t',
                            '--tags',
                            type=str,
                            nargs='+',
                            required=True,
                            help='Tags ids to be removed from nodes.')

        parser.add_argument('-n',
                            '--node',
                            type=int,
                            help='Id of the node to unassign tags.')

        return parser

    def take_action(self, parsed_args):
        self.client.unassign(node=parsed_args.node,
                             tag_ids=parsed_args.tags)

        msg = 'Tags {t} were unassigned from the node {n}\n'
        self.app.stdout.write(msg.format(t=parsed_args.tags,
                                         n=parsed_args.node))
