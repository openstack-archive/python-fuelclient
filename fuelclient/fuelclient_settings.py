# -*- coding: utf-8 -*-

#    Copyright 2013-2014 Mirantis, Inc.
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
import pkg_resources
import shutil

import six
import yaml

from fuelclient.cli import error


_SETTINGS = None


class FuelClientSettings(object):
    """Represents a model of Fuel Clients settings

    Default settings are saved to $XDG_CONFIG_HOME/fuel/fuel_client.yaml on
    the first run. If $XDG_CONFIG_HOME is not set, ~/.config/ directory is
    used by default.

    Custom settings may be stored in any YAML-formatted file the path to
    which should be supplied via the $FUELCLIENT_CUSTOM_SETTINGS environment
    variable. Custom settings override default ones.

    Top level values may also be set as environment variables, e.g.
    export SERVER_PORT=8080. These values have the highest priority.

    """
    def __init__(self):
        settings_files = []

        user_conf_dir = os.getenv('XDG_CONFIG_HOME',
                                  os.path.expanduser('~/.config/'))

        # Look up for a default file distributed with the source code
        default_settings = pkg_resources.resource_filename('fuelclient',
                                                           'fuel_client.yaml')

        user_settings = os.path.join(user_conf_dir, 'fuel', 'fuel_client.yaml')
        custom_settings = os.getenv('FUELCLIENT_CUSTOM_SETTINGS')

        if not os.path.exists(user_settings) and not custom_settings:
            self.populate_default_settings(default_settings, user_settings)
            six.print_('Settings for Fuel Client have been saved to {0}.\n'
                       'Consider changing default values to the ones which '
                       'are appropriate for you.'.format(user_settings))

        self._add_file_if_exists(default_settings, settings_files)
        self._add_file_if_exists(user_settings, settings_files)

        # Add a custom settings file specified by user
        self._add_file_if_exists(custom_settings, settings_files)

        self.config = {}
        for sf in settings_files:
            try:
                self._update_from_file(sf)
            except Exception as e:
                msg = ('Error while reading config file '
                       '%(file)s: %(err)s') % {'file': sf, 'err': str(e)}

                raise error.SettingsException(msg)

        self._update_from_env()

    def _add_file_if_exists(self, path_to_file, file_list):
        if path_to_file and os.access(path_to_file, os.R_OK):
            file_list.append(path_to_file)

    def _update_from_file(self, path):
        with open(path, 'r') as custom_config:
            self.config.update(
                yaml.load(custom_config.read())
            )

    def _update_from_env(self):
        for k in self.config:
            if k in os.environ:
                self.config[k] = os.environ[k]

    def populate_default_settings(self, source, destination):
        """Puts default configuration file to a user's home directory."""

        try:
            dst_dir = os.path.dirname(destination)

            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir, 0o700)

            shutil.copy(source, destination)
            os.chmod(destination, 0o600)
        except (IOError, OSError):
            msg = ('Could not save settings to {0}. Please make sure the '
                   'directory is writable')
            raise error.SettingsException(msg.format(dst_dir))

    def dump(self):
        return yaml.dump(self.config)

    def __getattr__(self, name):
        return self.config.get(name, None)

    def __repr__(self):
        return '<settings object>'


def _init_settings():
    global _SETTINGS
    _SETTINGS = FuelClientSettings()


def get_settings():
    if _SETTINGS is None:
        _init_settings()

    return _SETTINGS
