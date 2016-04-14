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

class FileOperationsCommand(object):
    """Adds common methods for file operations."""

    def get_network_data_path(self, network_id, directory=os.curdir):
        return os.path.join(os.path.abspath(directory),
                            "network_{0}".format(network_id))

    def read_network_data(self, network_id, serializer, directory=os.curdir):
        if not os.path.isdir(directory):
            raise error.InvalidDirectoryException('"{0}" does not exists or '
                                                  'is not a directory')
        network_file_path = self.get_network_data_path(network_id, directory)

        return serializer.read_from_file(network_file_path)

    def write_network_data(self, network_id, network_data,
                           serializer, directory=os.curdir):
        try:
            fileutils.ensure_tree(directory)
        except OSError as e:
            raise error.InvalidDirectoryException('Cannot write to "{0}". '
                                                  'The path is not writable '
                                                  'or is not a directory.')

        return serializer.write_to_path(self.get_network_data_path(directory),
                                        network_data)

