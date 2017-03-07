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

from fuelclient.commands import base


class PluginsMixIn(object):
    entity_name = 'plugins'

    @staticmethod
    def add_plugin_file_argument(parser):
        parser.add_argument(
            'file',
            type=str,
            help='Path to plugin file to install'
        )

    @staticmethod
    def add_plugin_name_argument(parser):
        parser.add_argument(
            'name',
            type=str,
            help='Name of plugin to remove'
        )

    @staticmethod
    def add_plugin_version_argument(parser):
        parser.add_argument(
            'version',
            type=str,
            help='Version of plugin to remove'
        )

    @staticmethod
    def add_plugin_ids_argument(parser):
        parser.add_argument(
            'ids',
            type=int,
            nargs='*',
            metavar='plugin-id',
            help='Synchronise only plugins with specified ids'
        )

    @staticmethod
    def add_plugin_install_force_argument(parser):
        parser.add_argument(
            '-f', '--force',
            action='store_true',
            help='Used for reinstall plugin with the same version'
        )


class PluginsList(PluginsMixIn, base.BaseListCommand):
    """Show list of all available plugins."""

    columns = ('id',
               'name',
               'version',
               'package_version',
               'releases')


class PluginsSync(PluginsMixIn, base.BaseCommand):
    """Synchronise plugins on file system with plugins in API service."""

    def get_parser(self, prog_name):
        parser = super(PluginsSync, self).get_parser(prog_name)
        self.add_plugin_ids_argument(parser)
        return parser

    def take_action(self, parsed_args):
        ids = parsed_args.ids if len(parsed_args.ids) > 0 else None
        self.client.sync(ids=ids)
        self.app.stdout.write("Plugins were successfully synchronized.\n")


class PluginInstall(PluginsMixIn, base.BaseCommand):
    """Install plugin archive and register in API service."""

    def get_parser(self, prog_name):
        parser = super(PluginInstall, self).get_parser(prog_name)
        self.add_plugin_file_argument(parser)
        self.add_plugin_install_force_argument(parser)
        return parser

    def take_action(self, parsed_args):
        self.client.install(parsed_args.file, force=parsed_args.force)
        self.app.stdout.write(
            "Plugin {0} was successfully installed.\n".format(parsed_args.file)
        )


class PluginRemove(PluginsMixIn, base.BaseCommand):
    """Remove the plugin package, and update data in API service."""

    def get_parser(self, prog_name):
        parser = super(PluginRemove, self).get_parser(prog_name)
        self.add_plugin_name_argument(parser)
        self.add_plugin_version_argument(parser)
        return parser

    def take_action(self, parsed_args):
        self.client.remove(parsed_args.name, parsed_args.version)
        self.app.stdout.write(
            "Plugin {0} was successfully removed.\n".format(parsed_args.name)
        )
