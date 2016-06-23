#    Copyright 2015 Mirantis, Inc.
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
import re

from cliff import argparse

from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient import utils


class PluginsMixIn(object):
    entity_name = 'plugins'


class PluginsList(PluginsMixIn, base.BaseListCommand):
    """Show list of all available plugins."""

    columns = ('id',
               'name',
               'version',
               'package_version',
               'releases')

    def take_action(self, parsed_args):
        data = self.client.get_all()
        data = data_utils.get_display_data_multi(self.columns, data)

        return self.columns, data


class PluginsInstall(PluginsMixIn, base.BaseCommand):
    """Install, upgrade or downgrade plugin and register it in API service."""

    def get_parser(self, prog_name):
        parser = super(PluginsInstall, self).get_parser(prog_name)

        def _plugin_file(path):
            if not utils.file_exists(path):
                raise argparse.ArgumentTypeError(
                    'File "{0}" does not exists'.format(path))
            return path

        parser.add_argument(
            'path',
            type=_plugin_file,
            help='Path to plugin file')

        parser.add_argument(
            '-f', '--force',
            action='store_true',
            help='Used for reinstall or downgrade a plugin')

        return parser

    def take_action(self, parsed_args):
        result = self.client.install(parsed_args.path, force=parsed_args.force)
        self.app.stdout.write("Plugin '{0}' was successfully {1}.\n".format(
            os.path.basename(parsed_args.path), result.get('action')))


class PluginsRemove(PluginsMixIn, base.BaseCommand):
    """Remove plugin from file system and from API service."""

    def get_parser(self, prog_name):
        parser = super(PluginsRemove, self).get_parser(prog_name)

        def _plugin_attrs(string):
            attrs = string.split('==')
            if len(attrs) != 2 or not re.search('^\d+\.\d+\.\d+$', attrs[1]):
                raise argparse.ArgumentTypeError(
                    "wrong format. Please set it as 'fuel_plugin==1.0.0'")
            return attrs

        parser.add_argument(
            'plugin',
            type=_plugin_attrs,
            help="Plugin to remove in format 'name==version'")

        return parser

    def take_action(self, parsed_args):
        self.client.remove(*parsed_args.plugin)
        self.app.stdout.write(
            "Plugin '{0}=={1}' was successfully removed.\n".format(
                *parsed_args.plugin))


class PluginsSync(PluginsMixIn, base.BaseCommand):
    """Synchronise plugins on file system with plugins in API service."""

    def get_parser(self, prog_name):
        parser = super(PluginsSync, self).get_parser(prog_name)
        parser.add_argument(
            'ids',
            type=int,
            nargs='*',
            metavar='plugin-id',
            help='Synchronise only plugins with specified ids')

        return parser

    def take_action(self, parsed_args):
        ids = parsed_args.ids if len(parsed_args.ids) > 0 else None
        self.client.sync(ids=ids)
        self.app.stdout.write("Plugins were successfully synchronized.\n")
