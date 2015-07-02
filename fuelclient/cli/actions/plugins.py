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
    )

    def __init__(self):
        super(PluginAction, self).__init__()
        self.args = [
            Args.group(
                Args.get_list_arg(
                    "List of all registered plugins."),
                Args.get_plugin_install_arg(
                    "Install and register plugin package"),
                Args.get_plugin_remove_arg(
                    "Remove and unregister plugin"),
                Args.get_plugin_register_arg(
                    "Register installed plugin"),
                Args.get_plugin_unregister_arg(
                    "Unregister plugin"),
                Args.get_plugin_update_arg(
                    "Update installed plugin"),
                Args.get_plugin_downgrade_arg(
                    "Downgrade installed plugin"),
                Args.get_plugin_sync_arg(
                    "Synchronise plugins with API service")),
            Args.get_plugin_arg("Plugin id."),
            Args.get_force_arg("Force action")
        ]
        self.flag_func_map = (
            ("install", self.install),
            ("remove", self.remove),
            ("update", self.update),
            ("downgrade", self.downgrade),
            ("sync", self.sync),
            ("register", self.register),
            ("unregister", self.unregister),
            (None, self.list),
        )

    def list(self, params):
        """Print all available plugins

                fuel plugins
                fuel plugins --list
        """
        plugins = Plugins.get_all_data()
        self.serializer.print_to_output(
            plugins,
            format_table(plugins, acceptable_keys=self.acceptable_keys))

    def install(self, params):
        """Install plugin archive and register in API service

               fuel plugins --install plugin-name-2.0-2.0.1-0.noarch.rpm
        """
        file_path = params.install
        self.check_file(file_path)
        results = Plugins.install(file_path, force=params.force)
        self.serializer.print_to_output(
            results,
            "Plugin {0} was successfully installed.".format(
                params.install))

    def remove(self, params):
        """Remove plugin from file system and from API service

               fuel plugins --remove plugin-name==1.0.1
        """
        name, version = self.parse_name_version(params.remove)
        results = Plugins.remove(name, version)

        self.serializer.print_to_output(
            results,
            "Plugin {0} was successfully removed.".format(params.remove))

    def update(self, params):
        """Update plugin from one minor version to another.
           For example if there is a plugin with version 2.0.0,
           plugin with version 2.0.1 can be used as update. But
           plugin with version 2.1.0, cannot be used to update
           plugin. Note that update is supported for plugins
           beginning from package_version 2.0.0

               fuel plugins --update plugin-name-2.0-2.0.1-0.noarch.rpm
        """
        plugin_path = params.update
        self.check_file(plugin_path)
        result = Plugins.update(plugin_path)
        self.serializer.print_to_output(
            result,
            "Plugin {0} was successfully updated.".format(plugin_path))

    def downgrade(self, params):
        """Downgrade plugin from one minor version to another.
           For example if there is a plugin with version 2.0.1,
           plugin with version 2.0.0 can be used to perform downgrade.
           Plugin with version 1.0.0, cannot be used to perform downgrade
           plugin. Note that downgrade is supported for plugins
           beginning from package_version 2.0.0

               fuel plugins --downgrade plugin-name-2.0-2.0.1-0.noarch.rpm
        """
        plugin_path = params.downgrade
        self.check_file(plugin_path)
        result = Plugins.downgrade(plugin_path)
        self.serializer.print_to_output(
            result,
            "Plugin {0} was successfully downgraded.".format(plugin_path))

    def sync(self, params):
        """Synchronise plugins on file system with plugins in
           API service, creates plugin if it is not exists,
           updates existent plugins

               fuel plugins --sync
               fuel plugins --sync --plugin-id=1,2
        """
        Plugins.sync(plugin_ids=params.plugin)
        self.serializer.print_to_output(
            None, "Plugins were successfully synchronized.")

    def register(self, params):
        """Register plugin in API service

               fuel plugins --register plugin-name==1.0.1
        """
        name, version = self.parse_name_version(params.register)
        result = Plugins.register(name, version, force=params.force)
        self.serializer.print_to_output(
            result,
            "Plugin {0} was successfully registered.".format(params.register))

    def unregister(self, params):
        """Deletes plugin from API service

               fuel plugins --unregister plugin-name==1.0.1
        """
        name, version = self.parse_name_version(params.unregister)
        result = Plugins.unregister(name, version)
        self.serializer.print_to_output(
            result,
            "Plugin {0} was successfully unregistered."
            "".format(params.unregister))

    def parse_name_version(self, param):
        """Takes the string and returns name and version

        :param str param: string with name and version
        :raises: error.ArgumentException if version is not specified
        """
        attrs = param.split('==')

        if len(attrs) != 2:
            raise error.ArgumentException(
                'Syntax: fuel plugins <action> fuel_plugin==1.0.0')

        return attrs

    def check_file(self, file_path):
        """Checks if file exists

        :param str file_path: path to the file
        :raises: error.ArgumentException if file does not exist
        """
        if not utils.file_exists(file_path):
            raise error.ArgumentException(
                'File "{0}" does not exists'.format(file_path))
