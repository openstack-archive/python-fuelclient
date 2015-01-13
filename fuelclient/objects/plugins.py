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

import os
import shutil
import tarfile

import yaml

from fuelclient.cli import error
from fuelclient.objects import base


EXTRACT_PATH = "/var/www/nailgun/plugins/"
VERSIONS_PATH = '/etc/fuel/version.yaml'


class Plugins(base.BaseObject):

    class_api_path = "plugins/"
    class_instance_path = "plugins/{id}"

    metadata_config = 'metadata.yaml'

    @classmethod
    def validate_environment(cls):
        return os.path.exists(VERSIONS_PATH)

    @classmethod
    def get_metadata(cls, plugin_tar):
        for member_name in plugin_tar.getnames():
            if cls.metadata_config in member_name:
                return yaml.load(plugin_tar.extractfile(member_name).read())
        raise error.BadDataException(
            "Tarfile {name} doesn't have {config}".format(
                name=plugin_tar.name, config=cls.metadata_config))

    @classmethod
    def get_plugin(cls, plugin_name, plugin_version=None):
        """Returns plugin fetched by name and optionally by version.

        If multiple plugin versions are found and version is not specified
        error is returned.

        :returns: dictionary with plugin data
        """
        checker = lambda p: p['name'] == plugin_name
        if plugin_version is not None:
            checker = lambda p: \
                (p['name'], p['version']) == (plugin_name, plugin_version)
        plugins = filter(checker, cls.get_all_data())
        if len(plugins) == 0:
            if plugin_version is None:
                raise error.BadDataException(
                    'Plugin {plugin_name} does not exist'.format(
                        plugin_name=plugin_name)
                )
            else:
                raise error.BadDataException(
                    'Plugin {plugin_name}, version {plugin_version} does '
                    'not exist'.format(
                        plugin_name=plugin_name,
                        plugin_version=plugin_version)
                )
        if len(plugins) > 1:
            if plugin_version is None:
                raise error.BadDataException(
                    'Multiple versions of plugin {plugin_name} found. '
                    'Please consider specifying a version in the '
                    '{plugin_name}==<version> format'.format(
                        plugin_name=plugin_name)
                )
        return plugins[0]

    @classmethod
    def add_plugin(cls, plugin_meta, plugin_tar):
        return plugin_tar.extractall(EXTRACT_PATH)

    @classmethod
    def install_plugin(cls, plugin_path, force=False):
        if not cls.validate_environment():
            raise error.WrongEnvironmentError(
                'Plugin can be installed only from master node.')
        plugin_tar = tarfile.open(plugin_path, 'r')
        try:
            metadata = cls.get_metadata(plugin_tar)
            resp = cls.connection.post_request_raw(
                cls.class_api_path, metadata)
            if resp.status_code == 409 and force:
                url = cls.class_instance_path.format(id=resp.json()['id'])
                resp = cls.connection.put_request(
                    url, metadata)
            else:
                resp.raise_for_status()
            cls.add_plugin(metadata, plugin_tar)
        finally:
            plugin_tar.close()
        return resp

    @classmethod
    def remove_plugin(cls, plugin_name, plugin_version=None):
        if not cls.validate_environment():
            raise error.WrongEnvironmentError(
                'Plugin can be removed only from master node.')
        plugin = cls.get_plugin(plugin_name, plugin_version)

        resp = cls.connection.delete_request(
            cls.class_instance_path.format(**plugin)
        )

        plugin_path = os.path.join(
            EXTRACT_PATH,
            '{name}-{version}'.format(**plugin)
        )
        shutil.rmtree(plugin_path)

        return resp
