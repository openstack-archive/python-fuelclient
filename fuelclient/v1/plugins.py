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

import collections
import os

import six

from fuelclient.cli import error
from fuelclient.v1 import base_v1


class PluginBase(object):

    @staticmethod
    def pre_install(path='/', ext=''):
        raise error.BadDataException(
            "Plugin '{0}' has unsupported format '{1}'.".format(
                os.path.basename(path), ext))


class PluginFP(object):

    msg_deprecation = "The plugin has old 1.0 package format. " \
        "This format does not support many features, such as updating " \
        "plugins. Find plugin in new format or migrate and rebuild this one.\n"

    def pre_install(self, *args, **kwargs):
        if kwargs.get('ext') == 'fp':
            error.print_deprecation_warning(self.msg_deprecation)
            return
        super(PluginFP, self).pre_install(*args, **kwargs)


class PluginRPM(object):

    def pre_install(self, *args, **kwargs):
        if kwargs.get('ext') == 'rpm':
            return
        super(PluginRPM, self).pre_install(*args, **kwargs)


class PluginsClient(PluginRPM, PluginFP, PluginBase, base_v1.BaseV1Client):

    class_api_path = 'plugins'
    instance_api_path = 'plugins/{id}'
    install_api_path = 'plugins/upload'
    sync_api_path = 'plugins/sync'

    def _get_all_data(self):
        return self.connection.get_request(self.class_api_path)

    def get_all(self):
        """Get plugins data and re-format 'releases' info to display
         supported 'os', 'version' in a user-friendly way, e.g.:
                ubuntu (liberty-8.0, liberty-9.0, mitaka-9.0)
                centos (liberty-8.0), ubuntu (liberty-8.0)

        :returns: list of plugins
        :rtype: list
        """
        # Replace original nested 'releases' dictionary (from plugins meta
        # dictionary) to a new user-friendly form with releases info, i.e.
        # 'os', 'version' that specific plugin supports
        plugins = self._get_all_data()
        for plugin in plugins:
            releases = collections.defaultdict(list)
            for key in plugin['releases']:
                releases[key['os']].append(key['version'])
            plugin['releases'] = ', '.join('{} ({})'.format(k, ', '.join(v))
                                           for k, v in six.iteritems(releases))
        return plugins

    def install(self, path, force=False):
        """Installs a plugin package and updates data in API service.

        :param path: Path to plugin file
        :type path: str
        :param force: Updates existent plugin even if it is not updatable
        :type force: bool
        :return: Plugin information
        :rtype: dict
        """
        self.pre_install(path=path, ext=os.path.splitext(path)[1][1:].lower())

        return self.connection.post_upload_file_raw(
            self.install_api_path, path, data={'force': force})

    def remove(self, name, version):
        """Removes a plugin package and updates data in API service.

        :param name: Plugin name
        :type name: str
        :param version: Plugin version
        :type version: str
        :return: Result of deleting
        :rtype: dict
        :raise: error.BadDataException if no plugin was found
        """
        plugins = [p for p in self._get_all_data()
                   if (p['name'], p['version']) == (name, version)]
        if not plugins:
            raise error.BadDataException(
                "Plugin '{0}' with version '{1}' does not exist.".format(
                    name, version))

        return self.connection.delete_request(
            self.instance_api_path.format(**plugins[0]))

    def sync(self, ids=None):
        """Synchronise plugins on file system with plugins in API service.

        :param ids: List of plugins IDs which should be synced
        :type ids: list
        :return: Result of syncing
        :rtype: dict
        """
        data = None
        if ids is not None:
            data = {'ids': ids}

        return self.connection.post_request(self.sync_api_path, data=data)


def get_client(connection):
    return PluginsClient(connection)
