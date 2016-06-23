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
import sys

import six

from fuelclient.cli import error
from fuelclient.objects import base


def _deprecated(msg):
    def decorator(func):
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            six.print_("DEPRECATION WARNING: {}".format(msg), file=sys.stderr)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class BasePlugin(base.BaseObject):

    class_api_path = 'plugins'
    instance_api_path = 'plugins/{id}'
    install_api_path = 'plugins/upload'
    sync_api_path = 'plugins/sync'

    @classmethod
    def install(cls, path, force=False):
        """Installs a plugin package and updates data in API service.

        :param str path: Path to plugin file
        :param bool force: Updates existent plugin even if it is not updatable
        :return: Plugin information
        :rtype: dict
        """
        return cls.connection.post_upload_file_raw(
            cls.install_api_path, path, data={'force': force})

    @classmethod
    def remove(cls, name, version):
        """Removes a plugin package and updates data in API service.

        :param str name: Plugin name
        :param str version: Plugin version
        :return: Result of deleting
        :rtype: dict
        """
        plugin = cls._get_plugin(name, version)
        return cls.connection.delete_request(
            cls.instance_api_path.format(**plugin))

    @classmethod
    def sync(cls, plugin_ids=None):
        """Checks all of the plugins on file systems,
        and makes sure that they have consistent information in API service.

        :param plugin_ids: List of plugins IDs which should be synced
        :type plugin_ids: list
        """
        data = None
        if plugin_ids is not None:
            data = {'ids': plugin_ids}
        return cls.connection.post_request(cls.sync_api_path, data=data)

    @classmethod
    def _get_plugin(cls, name, version):
        """Returns plugin fetched by name and version.

        :param str name: Plugin name
        :param str version: Plugin version
        :return: Plugin data
        :rtype: dict
        :raises: error.BadDataException if no plugin was found
        """
        plugins = [p for p in cls.get_all_data()
                   if (p['name'], p['version']) == (name, version)]
        if not plugins:
            raise error.BadDataException(
                "Plugin '{0}' with version '{1}' does not exist.".format(
                    name, version))

        return plugins[0]


class PluginV1(BasePlugin):

    msg_deprecation = "The plugin has old 1.0 package format. " \
        "This format does not support many features, such as updating " \
        "plugins. Find plugin in new format or migrate and rebuild this one.\n"

    @classmethod
    @_deprecated(msg_deprecation)
    def install(cls, *args, **kwargs):
        return super(PluginV1, cls).install(*args, **kwargs)


class PluginV2(BasePlugin):
    pass


class Plugins(object):

    def __getattr__(self, attr):
        def wrapper(*args, **kwargs):
            return getattr(BasePlugin, attr)(*args, **kwargs)

        return wrapper

    def install(self, path, force=False):
        obj = self._get_obj(path)
        return obj.install(path, force=force)

    @staticmethod
    def _get_obj(path):
        """Finds appropriate class of plugin handler by file extension.

        :param str path: Path to plugin file
        :return: Plugin class
        :raises: error.BadDataException for unsupported package version
        """
        pv = {'fp': PluginV1, 'rpm': PluginV2}
        ext = os.path.splitext(path)[1][1:].lower()
        if ext not in pv:
            raise error.BadDataException(
                "Plugin '{0}' has unsupported format '{1}'.".format(
                    os.path.basename(path), ext))

        return pv[ext]
