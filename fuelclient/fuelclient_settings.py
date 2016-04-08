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
import sys

import six
import yaml

from fuelclient.cli import error


_SETTINGS = None

# Format: old parameter: new parameter or None
DEPRECATION_TABLE = {'LISTEN_PORT': 'SERVER_PORT',
                     'KEYSTONE_USER': 'OS_USERNAME',
                     'KEYSTONE_PASS': 'OS_PASSWORD'}

# Format: parameter: fallback parameter
FALLBACK_TABLE = {DEPRECATION_TABLE[p]: p for p in DEPRECATION_TABLE}


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

        self.user_settings = os.path.join(user_conf_dir, 'fuel',
                                          'fuel_client.yaml')
        custom_settings = os.getenv('FUELCLIENT_CUSTOM_SETTINGS')

        if not os.path.exists(self.user_settings) and not custom_settings:
            self.populate_default_settings(default_settings,
                                           self.user_settings)
            six.print_('Settings for Fuel Client have been saved to {0}.\n'
                       'Consider changing default values to the ones which '
                       'are appropriate for you.'.format(self.user_settings))

        self._add_file_if_exists(default_settings, settings_files)
        self._add_file_if_exists(self.user_settings, settings_files)

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
        self._check_deprecated()

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

    def _print_deprecation_warning(self, old_option, new_option=None):
        """Print deprecation warning for an option."""

        deprecation_tpl = ('DEPRECATION WARNING: {} parameter was '
                           'deprecated and will not be supported in the next '
                           'version of python-fuelclient.')
        replace_tpl = ' Please replace this parameter with {}'

        deprecation = deprecation_tpl.format(old_option)
        replace = '' if new_option is None else replace_tpl.format(new_option)

        six.print_(deprecation, end='', file=sys.stderr)
        six.print_(replace, file=sys.stderr)

    def _check_deprecated(self):
        """Looks for deprecated options in user's configuration."""

        dep_opts = [opt for opt in self.config if opt in DEPRECATION_TABLE]

        for opt in dep_opts:

            new_opt = DEPRECATION_TABLE.get(opt)

            # Clean up new option if it was not set by a user
            # Produce a warning, if both old and new options are set.
            if self.config.get(new_opt) is None:
                self.config.pop(new_opt, None)
            else:
                six.print_('WARNING: configuration contains both {old} and '
                           '{new} options set. Since {old} was deprecated, '
                           'only the value of {new} '
                           'will be used.'.format(old=opt, new=new_opt),
                           file=sys.stderr
                           )

            self._print_deprecation_warning(opt, new_opt)

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

    def update_from_command_line_options(self, options):
        """Update parameters from valid command line options."""

        for param in self.config:
            opt_name = param.lower()

            value = getattr(options, opt_name, None)
            if value is not None:
                self.config[param] = value

    def dump(self):
        return yaml.dump(self.config)

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]

        if name in FALLBACK_TABLE:
            return self.config[FALLBACK_TABLE[name]]

        raise error.SettingsException('Value for {0} option is not '
                                      'configured'.format(name))

    def __repr__(self):
        return '<settings object>'


def _init_settings():
    global _SETTINGS
    _SETTINGS = FuelClientSettings()


def get_settings():
    if _SETTINGS is None:
        _init_settings()

    return _SETTINGS
