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

from cliff import show

from fuelclient.commands import base


class ExtensionMixIn(object):
    entity_name = 'extension'


class ExtensionList(ExtensionMixIn, base.BaseListCommand):
    """Show list of all available extensions."""

    columns = ("name",
               "version",
               "description",
               "provides")
    default_sorting_by = ["name"]


class EnvExtensionShow(ExtensionMixIn, base.BaseShowCommand):
    """Show list of enabled extensions for environment with given id."""

    columns = ("extensions", )

    def get_parser(self, prog_name):
        # Avoid adding id argument by BaseShowCommand
        # Because it adds 'id' with wrong help message for this class
        parser = show.ShowOne.get_parser(self, prog_name)

        parser.add_argument('id', type=int, help='Id of the environment.')

        return parser


class EnvExtensionEnable(ExtensionMixIn, base.BaseCommand):
    """Enable specified extensions for environment with given id."""

    def get_parser(self, prog_name):
        parser = super(EnvExtensionEnable, self).get_parser(prog_name)

        parser.add_argument('id', type=int, help='Id of the environment.')
        parser.add_argument('-E',
                            '--extensions',
                            required=True,
                            nargs='+',
                            help='Names of extensions to enable.')

        return parser

    def take_action(self, parsed_args):
        self.client.enable_extensions(parsed_args.id, parsed_args.extensions)

        msg = ('The following extensions: {e} have been enabled for '
               'the environment with id {id}.\n'.format(
                   e=', '.join(parsed_args.extensions), id=parsed_args.id))

        self.app.stdout.write(msg)


class EnvExtensionDisable(ExtensionMixIn, base.BaseCommand):
    """Disable specified extensions for environment with given id."""

    def get_parser(self, prog_name):
        parser = super(EnvExtensionDisable, self).get_parser(prog_name)

        parser.add_argument('id', type=int, help='Id of the environment.')
        parser.add_argument('-E',
                            '--extensions',
                            required=True,
                            nargs='+',
                            help='Names of extensions to disable.')

        return parser

    def take_action(self, parsed_args):
        self.client.disable_extensions(parsed_args.id, parsed_args.extensions)

        msg = ('The following extensions: {e} have been disabled for '
               'the environment with id {id}.\n'.format(
                   e=', '.join(parsed_args.extensions), id=parsed_args.id))

        self.app.stdout.write(msg)
