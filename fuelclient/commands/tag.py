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
    fields_mapper = (
        ('env', 'clusters'),
        ('release', 'releases')
    )

    def parse_model(self, args):
        for param, tag_class in self.fields_mapper:
            model_id = getattr(args, param)
            if model_id:
                return tag_class, model_id

    @staticmethod
    def get_file_path(directory, owner_type, owner_id, tag_name, file_format):
        return os.path.join(os.path.abspath(directory),
                            '{owner}_{id}'.format(owner=owner_type,
                                                  id=owner_id),
                            '{}.{}'.format(tag_name, file_format))


@six.add_metaclass(abc.ABCMeta)
class BaseUploadCommand(TagMixIn, base.BaseCommand):
    """Base class for uploading metadata of a tag."""

    @abc.abstractproperty
    def action(self):
        """String with the name of the action."""
        pass

    @abc.abstractproperty
    def uploader(self):
        """Callable for uploading data."""
        pass

    def get_parser(self, prog_name):
        parser = super(BaseUploadCommand, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-r',
                           '--release',
                           type=int,
                           help='Id of the release')
        group.add_argument('-e',
                           '--env',
                           type=int,
                           help='Id of the environment')
        parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Name of tag.')
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
        model, model_id = self.parse_model(parsed_args)
        params = {"owner_type": model,
                  "owner_id": model_id,
                  "tag_name": parsed_args.name}

        file_path = self.get_file_path(parsed_args.directory,
                                       model,
                                       model_id,
                                       parsed_args.name,
                                       parsed_args.format)

        try:
            with open(file_path, 'r') as stream:
                data = data_utils.safe_load(parsed_args.format, stream)
                self.uploader(data, **params)
        except (OSError, IOError):
            msg = "Could not read description for tag '{}' at {}".format(
                parsed_args.name, file_path)
            raise error.InvalidFileException(msg)

        msg = ("Description of tag '{tag}' for {owner} with id {id} was "
               "{action}d from {file_path}\n".format(tag=parsed_args.name,
                                                     owner=model,
                                                     id=model_id,
                                                     action=self.action,
                                                     file_path=file_path))
        self.app.stdout.write(msg)


class TagList(TagMixIn, base.BaseListCommand):
    """Show list of all available tags for release or cluster."""

    columns = ("name",
               "group",
               "conflicts",
               "description")

    @property
    def default_sorting_by(self):
        return ['name']

    def get_parser(self, prog_name):
        parser = super(TagList, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-r',
                           '--release',
                           type=int,
                           help='Id of the release')
        group.add_argument('-e',
                           '--env',
                           type=int,
                           help='Id of the environment')
        return parser

    def take_action(self, parsed_args):
        model, model_id = self.parse_model(parsed_args)
        data = self.client.get_all(model, model_id)

        data = data_utils.get_display_data_multi(self.columns, data)
        data = self._sort_data(parsed_args, data)
        return self.columns, data


class TagDownload(TagMixIn, base.BaseCommand):
    """Download full tag description to file."""

    def get_parser(self, prog_name):
        parser = super(TagDownload, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-r',
                           '--release',
                           type=int,
                           help='Id of the release')
        group.add_argument('-e',
                           '--env',
                           type=int,
                           help='Id of the environment')
        parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Name of tag.')
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
        model, model_id = self.parse_model(parsed_args)
        file_path = self.get_file_path(parsed_args.directory,
                                       model,
                                       model_id,
                                       parsed_args.name,
                                       parsed_args.format)
        data = self.client.get_tag(model,
                                   model_id,
                                   parsed_args.name)

        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format, stream, data)
        except (OSError, IOError):
            msg = ("Could not store description data "
                   "for tag {} at {}".format(parsed_args.name, file_path))
            raise error.InvalidFileException(msg)

        msg = ("Description data of tag '{}' within {} id {} "
               "was stored in {}\n".format(parsed_args.name,
                                           model,
                                           model_id,
                                           file_path))
        self.app.stdout.write(msg)


class TagUpdate(BaseUploadCommand):
    """Update a tag from file description."""

    action = "update"

    @property
    def uploader(self):
        return self.client.update


class TagCreate(BaseUploadCommand):
    """Create a tag from file description"""

    action = "create"

    @property
    def uploader(self):
        return self.client.create


class TagDelete(TagMixIn, base.BaseCommand):
    """Delete a tag from release or cluster"""

    def get_parser(self, prog_name):
        parser = super(TagDelete, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-r',
                           '--release',
                           type=int,
                           help='Id of the release')
        group.add_argument('-e',
                           '--env',
                           type=int,
                           help='Id of the environment')
        parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Name of tag.')
        return parser

    def take_action(self, parsed_args):
        model, model_id = self.parse_model(parsed_args)
        self.client.delete(model,
                           model_id,
                           parsed_args.name)

        msg = "Tag '{}' was deleted from {} with id {}\n".format(
            parsed_args.name, model, model_id)
        self.app.stdout.write(msg)
