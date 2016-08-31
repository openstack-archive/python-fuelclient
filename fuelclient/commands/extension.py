# -*- coding: utf-8 -*-

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

from fuelclient.commands import base
from fuelclient.common import data_utils


class ExtensionMixIn(object):
    entity_name = 'extension'


class ExtensionList(ExtensionMixIn, base.BaseListCommand):
    """Show list of all available extensions."""

    columns = ("name",
               "version",
               "description",
               "provides")


class EnvExtensionMixIn(ExtensionMixIn, base.BaseCommand):

    def get_parser(self, prog_name):
        parser = super(EnvExtensionMixIn, self).get_parser(prog_name)

        parser.add_argument('-e',
                            '--env',
                            required=True,
                            type=int,
                            help='Id of the environment.')

        return parser


class EnvExtensionList(EnvExtensionMixIn, base.BaseListCommand):
    """Show list of enabled extensions for environment with given id."""
    columns = ("extensions",
               )

    def take_action(self, parsed_args):
        data = self.client.get_extensions(parsed_args.env)
        data = [{'extensions': data}]
        data = data_utils.get_display_data_multi(self.columns, data)

        return self.columns, data


class EnvExtensionEnable(EnvExtensionMixIn):
    """Enable specified extensions for a specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvExtensionEnable, self).get_parser(prog_name)

        parser.add_argument('-E',
                            '--extensions',
                            required=True,
                            nargs='+',
                            help='Names of extensions to enable.')

        return parser

    def take_action(self, parsed_args):
        enabled_exts = self.client.enable_extensions(
            parsed_args.env, parsed_args.extensions)

        msg = ('Fhe following extensions {e} have been enabled for '
               'the environment with id {id}.\n'.format(
                   e=', '.join(enabled_exts), id=parsed_args.env))

        self.app.stdout.write(msg)


class EnvExtensionDisable(EnvExtensionMixIn):
    """Disable specified extensions for a specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvExtensionDisable, self).get_parser(prog_name)

        parser.add_argument('-E',
                            '--extensions',
                            required=True,
                            nargs='+',
                            help='Names of extensions to disable.')

        return parser

    def take_action(self, parsed_args):
        enabled_exts = self.client.disable_extensions(
            parsed_args.env, parsed_args.extensions)

        msg = ('Fhe following extensions {e} have been enabled for '
               'the environment with id {id}.\n'.format(
                   e=', '.join(enabled_exts), id=parsed_args.env))

        self.app.stdout.write(msg)
