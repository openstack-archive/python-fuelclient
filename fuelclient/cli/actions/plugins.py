#    Copyright 2014 Mirantis, Inc.
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

import collections
import os
import six

import fuelclient.cli.arguments as Args

from fuelclient.cli.actions.base import Action
from fuelclient.cli import error
from fuelclient.cli.formatting import format_table
from fuelclient.objects.plugins import Plugins
from fuelclient import utils


class PluginAction(Action):
    """List and modify currently available releases
    """
    action_name = "plugins"

    acceptable_keys = (
        "id",
        "name",
        "version",
        "package_version",
        "releases"
    )

    def __init__(self):
        super(PluginAction, self).__init__()
        self.args = [
            Args.group(
                Args.get_list_arg(
                    "List of all registered plugins."),
                Args.get_plugin_install_arg(
                    "Install plugin package"),
                Args.get_plugin_remove_arg(
                    "Remove plugin"),
                Args.get_plugin_sync_arg(
                    "Synchronise plugins with API service")),
            Args.get_plugin_arg("Plugin id."),
            Args.get_force_arg("Force action")
        ]
        self.flag_func_map = (
            ("install", self.install),
            ("remove", self.remove),
            ("sync", self.sync),
            (None, self.list),
        )

    def list(self, params):
        """Print all available plugins

              fuel plugins
              fuel plugins --list
        """
        plugins = Plugins().get_all_data()
        # Replace original nested 'release' dictionary (from plugins meta
        # dictionary) to flat one with necessary release info (os, version)
        for plugin in plugins:
            releases = collections.defaultdict(list)
            for key in plugin['releases']:
                releases[key['os']].append(key['version'])
            plugin['releases'] = ', '.join('{} ({})'.format(k, ', '.join(v))
                                           for k, v in six.iteritems(releases))
        self.serializer.print_to_output(
            plugins,
            format_table(plugins, acceptable_keys=self.acceptable_keys))

    def install(self, params):
        """Install, upgrade or downgrade plugin and register it in API service.
            Upgrade or downgrade plugin is allowed from one minor version
            to another:
            2.0.0 -> 2.0.1 - allowed
            2.0.0 -> 2.1.0 - cannot be used to perform upgrade,
                a new version of a plugin will be installed
            2.0.1 -> 2.0.0 - allowed
            2.0.1 -> 1.0.0 - cannot be used to perform downgrade,
                a new version of a plugin will be installed

              fuel plugins --install plugin-name-2.0-2.0.1-0.noarch.rpm

            Note: upgrade and downgrade is supported for plugins beginning
            from package_version 2.0.0

            To reinstall plugin with the same version is used '--force' flag:

              fuel plugins --install plugin-name-2.0-2.0.1-0.noarch.rpm --force

        """
        file_path = params.install
        self.check_file(file_path)
        result = Plugins().install(file_path, force=params.force)
        self.serializer.print_to_output(
            result,
            "Plugin '{0}' was successfully {1}.".format(
                os.path.basename(file_path), result['action']))

    def remove(self, params):
        """Remove plugin from file system and from API service.

              fuel plugins --remove plugin-name==1.0.1
        """
        name, version = self.parse_name_version(params.remove)
        result = Plugins().remove(name, version)
        self.serializer.print_to_output(
            result,
            "Plugin '{0}' was successfully removed.".format(params.remove))

    def sync(self, params):
        """Synchronise plugins on file system with plugins in API service,
            creates plugin if it is not exists, updates existent plugins.

              fuel plugins --sync
              fuel plugins --sync --plugin-id=1,2
        """
        Plugins().sync(plugin_ids=params.plugin)
        self.serializer.print_to_output(
            None, "Plugins were successfully synchronized.")

    @staticmethod
    def parse_name_version(param):
        """Takes the string and returns name and version.

        :param str param: string with name and version
        :raises: error.ArgumentException if version is not specified
        """
        attrs = param.split('==')

        if len(attrs) != 2:
            raise error.ArgumentException(
                'Syntax: fuel plugins <action> fuel_plugin==1.0.0')

        return attrs

    @staticmethod
    def check_file(file_path):
        """Checks if file exists.

        :param str file_path: path to the file
        :raises: error.ArgumentException if file does not exist
        """
        if not utils.file_exists(file_path):
            raise error.ArgumentException(
                'File "{0}" does not exists'.format(file_path))
