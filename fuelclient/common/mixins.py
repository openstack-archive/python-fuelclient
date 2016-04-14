#    Copyright 2016 Mirantis, Inc.
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
from oslo_utils import fileutils

from fuelclient.cli import error
from fuelclient import utils

import json
import yaml


class FileOperationsCommand(object):
    """Adds common methods for file operations for a command."""

    serializers = {
        'json': {
            'w': lambda d: json.dumps(d, indent=4),
            'r': utils.safe_deserialize(json.loads)
        },
        'yaml': {
            'w': lambda d: yaml.safe_dump(d, default_flow_style=False),
            'r': utils.safe_deserialize(yaml.load)
        }
    }

    def _get_serializer(self, data_format, mode):
        try:
            return self.serializers[data_format][mode]
        except KeyError:
            msg = ('Could not find a serializer to {mod} the {fmt} '
                   'format').format(mod='read' if mode == 'r' else 'write',
                                    fmt=data_format)
            raise error.BadSerializer(msg)

    def get_network_data_path(self, env_id, directory=os.curdir):
        """Return data directory that stores network configuration."""

        return os.path.join(os.path.abspath(directory),
                            "network_{0}".format(env_id))

    def read_network_data(self, env_id,
                          serializer_format='json', directory=os.curdir):
        """Read network configuration

        Reads network configuration from the specified directory
        and de-serializes is using specified serializer.

        :param env_id:            ID of an environment
        :param serializer_format: Serializer that is going to be used for
                                  de-serialization. Should be either json
                                  or yaml.
                                  Default: json.
        :param directory:         The directory where serialized network
                                  configuration is stored at.
        :return:                  dict that represents network configuration
                                  for the specified environment.

        """
        if not os.path.isdir(directory):
            msg = ('"{0}" does not exists or is not a '
                   'directory').format(directory)
            raise error.InvalidDirectoryException(msg)

        data_path = self.get_network_data_path(env_id, directory)
        serializer = self._get_serializer(serializer_format, 'r')

        with open(data_path, 'r') as f:
            return serializer(f.read())

    def write_network_data(self, env_id, network_data,
                           serializer_format='json', directory=os.curdir):
        """Write network configuration

        Serializes network configuration using the specified
        serializer and stores in at the specified location.

        :param env_id:            ID of an environment
        :param serializer_format: Serializer that is going to be used for
                                  serialization. Should be either json or yaml.
                                  Default: json.
        :param directory:         The directory where serialized network
                                  configuration will be stored at.

        """
        try:
            fileutils.ensure_tree(directory)

            data_path = self.get_network_data_path(env_id, directory)
            serializer = self._get_serializer(serializer_format, 'w')

            with open(data_path, 'w') as f:
                f.write(serializer(network_data))
        except (IOError, OSError):
            msg = ('Cannot write to "{0}". The path is not writable '
                   'or is not a directory.'.format(directory))
            raise error.InvalidDirectoryException(msg)
