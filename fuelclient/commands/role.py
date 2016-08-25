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

import os

from oslo_utils import fileutils

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils


class RoleMixIn(object):

    entity_name = 'role'
    supported_file_formats = ('json', 'yaml')

    @staticmethod
    def add_release_arg(parser):
        parser.add_argument('-r',
                            '--release',
                            type=int,
                            required=True,
                            help='Id of the release')

    @staticmethod
    def get_file_path(directory, release_id, role_name, file_format):
        return os.path.join(os.path.abspath(directory),
                            'release_{id}'.format(id=release_id),
                            '{}.{}'.format(role_name, file_format))


class RoleList(RoleMixIn, base.BaseListCommand):
    """Show list of all available roles for specific release."""

    columns = ("name",
               "group",
               "conflicts",
               "description")

    def get_parser(self, prog_name):
        parser = super(RoleList, self).get_parser(prog_name)
        self.add_release_arg(parser)
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all(parsed_args.release)

        data = data_utils.get_display_data_multi(self.columns, data)
        return self.columns, data


class RoleDownload(RoleMixIn, base.BaseCommand):
    """Download full role description to file."""

    def get_parser(self, prog_name):
        parser = super(RoleDownload, self).get_parser(prog_name)
        self.add_release_arg(parser)
        parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Name of role.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized role data.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.path.curdir,
                            help='Destination directory. Defaults to '
                                 'the current directory.')
        return parser

    def take_action(self, parsed_args):
        file_path = self.get_file_path(parsed_args.directory,
                                       parsed_args.release,
                                       parsed_args.name,
                                       parsed_args.format)
        data = self.client.get_one(parsed_args.release, parsed_args.name)

        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format, stream, data)
        except (OSError, IOError):
            msg = 'Could not store description data for role {} at {}'
            raise error.InvalidFileException(msg.format(parsed_args.name,
                                                        file_path))

        msg = ("Description data for role '{}' "
               "was stored in {}\n".format(parsed_args.name, file_path))
        self.app.stdout.write(msg)


class RoleUpdate(RoleMixIn, base.BaseCommand):
    pass
