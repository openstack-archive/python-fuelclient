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

import abc
import os
import shutil
import sys
import tarfile

from distutils.version import StrictVersion

import six
import yaml

from fuelclient.cli import error
from fuelclient.objects import base
from fuelclient import utils


PLUGINS_PATH = '/var/www/nailgun/plugins/'
METADATA_MASK = '/var/www/nailgun/plugins/*/metadata.yaml'
VERSIONS_PATH = '/etc/fuel/version.yaml'


def raise_error_if_not_master():
    """Raises error if it's not Fuel master

    :raises: error.WrongEnvironmentError
    """
    if not os.path.exists(VERSIONS_PATH):
        raise error.WrongEnvironmentError(
            'Action can be performed from Fuel master node only.')


def master_only(f):
    """Decorator for the method, which raises error, if method
    is called on the node which is not Fuel master
    """
    @six.wraps(f)
    def print_message(*args, **kwargs):
        raise_error_if_not_master()
        return f(*args, **kwargs)

    return print_message


@six.add_metaclass(abc.ABCMeta)
class BasePlugin(object):

    @abc.abstractmethod
    def install(cls, plugin_path, force=False):
        """Installs plugin package
        """

    @abc.abstractmethod
    def update(cls, plugin_path):
        """Updates the plugin
        """

    @abc.abstractmethod
    def remove(cls, plugin_name, plugin_version):
        """Removes the plugin from file system
        """

    @abc.abstractmethod
    def downgrade(cls, plugin_path):
        """Downgrades the plugin
        """

    @abc.abstractmethod
    def name_from_file(cls, file_path):
        """Retrieves name from plugin package
        """

    @abc.abstractmethod
    def version_from_file(cls, file_path):
        """Retrieves version from plugin package
        """


class PluginV1(BasePlugin):

    metadata_config = 'metadata.yaml'

    def deprecated(f):
        """Prints deprecation warning for old plugins
        """
        @six.wraps(f)
        def print_message(*args, **kwargs):
            six.print_(
                'DEPRECATION WARNING: The plugin has old 1.0 package format, '
                'this format does not support many features, such as '
                'plugins updates, find plugin in new format or migrate '
                'and rebuild this one.', file=sys.stderr)
            return f(*args, **kwargs)

        return print_message

    @classmethod
    @master_only
    @deprecated
    def install(cls, plugin_path, force=False):
        plugin_tar = tarfile.open(plugin_path, 'r')
        try:
            plugin_tar.extractall(PLUGINS_PATH)
        finally:
            plugin_tar.close()

    @classmethod
    @master_only
    @deprecated
    def remove(cls, plugin_name, plugin_version):
        plugin_path = os.path.join(
            PLUGINS_PATH, '{0}-{1}'.format(plugin_name, plugin_version))
        shutil.rmtree(plugin_path)

    @classmethod
    def update(cls, _):
        raise error.BadDataException(
            'Update action is not supported for old plugins with '
            'package version "1.0.0", you can install your plugin '
            'or use newer plugin format.')

    @classmethod
    def downgrade(cls, _):
        raise error.BadDataException(
            'Downgrade action is not supported for old plugins with '
            'package version "1.0.0", you can install your plugin '
            'or use newer plugin format.')

    @classmethod
    def name_from_file(cls, file_path):
        """Retrieves plugin name from plugin archive.

        :param str plugin_path: path to the plugin
        :returns: plugin name
        """
        return cls._get_metadata(file_path)['name']

    @classmethod
    def version_from_file(cls, file_path):
        """Retrieves plugin version from plugin archive.

        :param str plugin_path: path to the plugin
        :returns: plugin version
        """
        return cls._get_metadata(file_path)['version']

    @classmethod
    def _get_metadata(cls, plugin_path):
        """Retrieves metadata from plugin archive

        :param str plugin_path: path to the plugin
        :returns: metadata from the plugin
        """
        plugin_tar = tarfile.open(plugin_path, 'r')

        try:
            for member_name in plugin_tar.getnames():
                if cls.metadata_config in member_name:
                    return yaml.load(
                        plugin_tar.extractfile(member_name).read())
        finally:
            plugin_tar.close()


class PluginV2(BasePlugin):

    @classmethod
    @master_only
    def install(cls, plugin_path, force=False):
        if force:
            utils.exec_cmd(
                'yum -y install {0} || yum -y reinstall {0}'
                .format(plugin_path))
        else:
            utils.exec_cmd('yum -y install {0}'.format(plugin_path))

    @classmethod
    @master_only
    def remove(cls, name, version):
        rpm_name = '{0}-{1}'.format(name, utils.major_plugin_version(version))
        utils.exec_cmd('yum -y remove {0}'.format(rpm_name))

    @classmethod
    @master_only
    def update(cls, plugin_path):
        utils.exec_cmd('yum -y update {0}'.format(plugin_path))

    @classmethod
    @master_only
    def downgrade(cls, plugin_path):
        utils.exec_cmd('yum -y downgrade {0}'.format(plugin_path))

    @classmethod
    def name_from_file(cls, file_path):
        """Retrieves plugin name from RPM. RPM name contains
        the version of the plugin, which should be removed.

        :param str file_path: path to rpm file
        :returns: name of the plugin
        """
        for line in utils.exec_cmd_iterator(
                "rpm -qp --queryformat '%{{name}}' {0}".format(file_path)):
            name = line
            break

        return cls._remove_major_plugin_version(name)

    @classmethod
    def version_from_file(cls, file_path):
        """Retrieves plugin version from RPM.

        :param str file_path: path to rpm file
        :returns: version of the plugin
        """
        for line in utils.exec_cmd_iterator(
                "rpm -qp --queryformat '%{{version}}' {0}".format(file_path)):
            version = line
            break

        return version

    @classmethod
    def _remove_major_plugin_version(cls, name):
        """Removes the version from plugin name.
        Here is an example: "name-1.0" -> "name"

        :param str name: plugin name
        :returns: the name withot version
        """
        name_wo_version = name

        if '-' in name_wo_version:
            name_wo_version = '-'.join(name.split('-')[:-1])

        return name_wo_version


class Plugins(base.BaseObject):

    class_api_path = 'plugins/'
    class_instance_path = 'plugins/{id}'

    @classmethod
    def register(cls, name, version, force=False):
        """Tries to find plugin on file system, creates
        it in API service if it exists.

        :param str name: plugin name
        :param str version: plugin version
        :param str force: if True updates meta information
                          about the plugin even it does not
                          support updates
        """
        metadata = None
        for m in utils.glob_and_parse_yaml(METADATA_MASK):
            if m.get('version') == version and \
               m.get('name') == name:
                metadata = m
                break

        if not metadata:
            raise error.BadDataException(
                'Plugin {0} with version {1} does '
                'not exist, install it and try again'.format(
                    name, version))

        return cls.update_or_create(metadata, force=force)

    @classmethod
    def sync(cls, plugin_ids=None):
        """Checks all of the plugins on file systems,
        and makes sure that they have consistent information
        in API service.

        :params plugin_ids: list of ids for plugins which should be synced
        :type plugin_ids: list
        :returns: None
        """
        post_data = None
        if plugin_ids:
            post_data = {'ids': plugin_ids}

        cls.connection.post_request(
            api='plugins/sync/', data=post_data)

    @classmethod
    def unregister(cls, name, version):
        """Removes the plugin from API service

        :param str name: plugin name
        :param str version: plugin version
        """
        plugin = cls.get_plugin(name, version)
        return cls.connection.delete_request(
            cls.class_instance_path.format(**plugin))

    @classmethod
    def install(cls, plugin_path, force=False):
        """Installs the package, and creates data in API service

        :param str name: plugin name
        :param str version: plugin version
        """
        plugin = cls.make_obj_by_file(plugin_path)

        name = plugin.name_from_file(plugin_path)
        version = plugin.version_from_file(plugin_path)

        plugin.install(plugin_path, force=force)
        response = cls.register(name, version, force=force)
        cls.sync(plugin_ids=[response['id']])

        return response

    @classmethod
    def remove(cls, plugin_name, plugin_version):
        """Removes the package, and updates data in API service

        :param str name: plugin name
        :param str version: plugin version
        """
        plugin = cls.make_obj_by_name(plugin_name, plugin_version)
        cls.unregister(plugin_name, plugin_version)
        return plugin.remove(plugin_name, plugin_version)

    @classmethod
    def update(cls, plugin_path):
        """Updates the package, and updates data in API service

        :param str plugin_path: path to the plugin
        """
        plugin = cls.make_obj_by_file(plugin_path)

        name = plugin.name_from_file(plugin_path)
        version = plugin.version_from_file(plugin_path)

        plugin.update(plugin_path)
        return cls.register(name, version)

    @classmethod
    def downgrade(cls, plugin_path):
        """Downgrades the package, and updates data in API service

        :param str plugin_path: path to the plugin
        """
        plugin = cls.make_obj_by_file(plugin_path)

        name = plugin.name_from_file(plugin_path)
        version = plugin.version_from_file(plugin_path)

        plugin.downgrade(plugin_path)
        return cls.register(name, version)

    @classmethod
    def make_obj_by_name(cls, name, version):
        """Finds appropriate plugin class version,
        by plugin version and name.

        :param str name:
        :param str version:
        :returns: plugin class
        :raises: error.BadDataException unsupported package version
        """
        plugin = cls.get_plugin(name, version)
        package_version = plugin['package_version']

        if StrictVersion('1.0.0') <= \
           StrictVersion(package_version) < \
           StrictVersion('2.0.0'):
            return PluginV1
        elif StrictVersion('2.0.0') <= StrictVersion(package_version):
            return PluginV2

        raise error.BadDataException(
            'Plugin {0}=={1} has unsupported package version {2}'.format(
                name, version, package_version))

    @classmethod
    def make_obj_by_file(cls, file_path):
        """Finds appropriate plugin class version,
        by plugin file.

        :param str file_path: plugin path
        :returns: plugin class
        :raises: error.BadDataException unsupported package version
        """
        _, ext = os.path.splitext(file_path)

        if ext == '.fp':
            return PluginV1
        elif ext == '.rpm':
            return PluginV2

        raise error.BadDataException(
            'Plugin {0} has unsupported format {1}'.format(
                file_path, ext))

    @classmethod
    def update_or_create(cls, metadata, force=False):
        """Try to update existent plugin or create new one.

        :param dict metadata: plugin information
        :param bool force: updates existent plugin even if
                           it is not updatable
        """
        # Try to update plugin
        plugin_for_update = cls.get_plugin_for_update(metadata)
        if plugin_for_update:
            url = cls.class_instance_path.format(id=plugin_for_update['id'])
            resp = cls.connection.put_request(url, metadata)
            return resp

        # If plugin is not updatable it means that we should
        # create new instance in Nailgun
        resp_raw = cls.connection.post_request_raw(
            cls.class_api_path, metadata)
        resp = resp_raw.json()

        if resp_raw.status_code == 409 and force:
            # Replace plugin information
            url = cls.class_instance_path.format(id=resp['id'])
            resp = cls.connection.put_request(url, metadata)
        else:
            resp_raw.raise_for_status()

        return resp

    @classmethod
    def get_plugin_for_update(cls, metadata):
        """Retrieves plugins which can be updated

        :param dict metadata: plugin metadata
        :returns: dict with plugin which can be updated or None
        """
        if not cls.is_updatable(metadata['package_version']):
            return

        plugins = filter(
            lambda p: p['name'] == metadata['name'] and
            cls.is_updatable(p['package_version']) and
            utils.major_plugin_version(metadata['version']) ==
            utils.major_plugin_version(p['version']),
            cls.get_all_data())

        plugin = None
        if plugins:
            # List should contain only one plugin, but just
            # in case we make sure that we get plugin with
            # higher version
            plugin = sorted(
                plugins,
                key=lambda p: StrictVersion(p['version']))[0]

        return plugin

    @classmethod
    def is_updatable(cls, package_version):
        """Checks if plugin's package version supports updates.

        :param str package_version: package version of the plugin
        :returns: True if plugin can be updated
                  False if plugin cannot be updated
        """
        return StrictVersion('2.0.0') <= StrictVersion(package_version)

    @classmethod
    def get_plugin(cls, name, version):
        """Returns plugin fetched by name and version.

        :param str name: plugin name
        :param str version: plugin version
        :returns: dictionary with plugin data
        :raises: error.BadDataException if no plugin was found
        """
        plugins = filter(
            lambda p: (p['name'], p['version']) == (name, version),
            cls.get_all_data())

        if not plugins:
            raise error.BadDataException(
                'Plugin "{name}" with version {version}, does '
                'not exist'.format(name=name, version=version))

        return plugins[0]
