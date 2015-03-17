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
import sys

import six
import yaml

from fuelclient.cli import error


_SETTINGS = None


class FuelClientSettings(object):
    """Represents a model of Fuel Clients settings

    Default settigs file are distributed with the source code in
    the <DIST_DIR>/fuelclient_settings.yaml. Those settings can be
    overriden by /etc/fuel/client/config.yaml file.

    User-specific settings may be stored in any YAML-formatted file
    the path to which should be supplied via the FUELCLIENT_CUSTOM_SETTINGS
    environment variable. Custom settins override the default ones.

    Top level values may also be set as environment variables, e.g.
    export SERVER_PORT=8080.

    """
    def __init__(self):
        settings_files = []

        # Look up for a default file distributed with the source code
        project_path = os.path.dirname(__file__)
        project_settings_file = os.path.join(project_path,
                                             'fuelclient_settings.yaml')
        external_default_settings = '/etc/fuel/client/config.yaml'
        external_user_settings = os.environ.get('FUELCLIENT_CUSTOM_SETTINGS')

        # NOTE(romcheg): when external default settings file is removed
        # this deprecation warning should be removed as well.
        if os.path.exists(external_default_settings) and \
                external_default_settings != external_user_settings:
            six.print_('DEPRECATION WARNING: {0} exists and will be '
                       'used as the source for settings. This behavior is '
                       'deprecated. Please specify the path to your custom '
                       'settings file in the FUELCLIENT_CUSTOM_SETTINGS '
                       'environment variable.'.format(
                           external_default_settings),
                       file=sys.stderr)

        self._add_file_if_exists(project_settings_file, settings_files)
        self._add_file_if_exists(external_default_settings, settings_files)

        # Add a custom settings file specified by user
        self._add_file_if_exists(external_user_settings, settings_files)

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
        for k in six.iterkeys(self.config):
            if k in os.environ:
                self.config[k] = os.environ[k]

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
