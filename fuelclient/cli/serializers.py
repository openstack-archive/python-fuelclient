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
from __future__ import print_function

from itertools import ifilter
from itertools import imap
import json
import os

import yaml

from fuelclient.cli import error
from fuelclient import consts


class Serializer(object):
    """Serializer class - contains all logic responsible for
    printing to stdout, reading and writing files to file system.
    """
    serializers = {
        "json": {
            "w": lambda d: json.dumps(d, indent=4),
            "r": lambda d: json.loads(d)
        },
        "yaml": {
            "w": lambda d: yaml.safe_dump(d, default_flow_style=False),
            "r": lambda d: yaml.load(d)
        }
    }

    format_flags = False
    default_format = "yaml"
    format = default_format

    def __init__(self, format=None):
        if format and format in self.serializers:
            self.format = format
            self.format_flags = True

    @property
    def serializer(self):
        """Returns dicts with methods for loadin/dumping current fromat.

        Returned dict's keys:
            * 'w' - from 'writing', method for serializing/dumping data
            * 'r' - from 'reading', method for deserializing/loading data
        """
        return self.serializers[self.format]

    def serialize(self, data):
        """Shortcut for serializing data with current format."""
        return self.serializer['w'](data)

    def deserialize(self, data):
        """Shortcut for deserializing data with current format."""
        return self.serializer['r'](data)

    @classmethod
    def from_params(cls, params):
        return cls(format=getattr(params,
                                  consts.SERIALIZATION_FORMAT_FLAG, None))

    def print_formatted(self, data):
            print(self.serializer["w"](data))

    def print_to_output(self, formatted_data, arg, print_method=print):
        if self.format_flags:
            self.print_formatted(formatted_data)
        else:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            print_method(arg)

    def prepare_path(self, path):
        return "{0}.{1}".format(
            path, self.format
        )

    def write_to_path(self, path, data):
        full_path = self.prepare_path(path)
        with open(full_path, "w+") as file_to_write:
            self.write_to_file(file_to_write, data)
        return full_path

    def read_from_file(self, path):
        return self.read_from_full_path(self.prepare_path(path))

    def read_from_full_path(self, full_path):
        with open(full_path, "r") as file_to_read:
            return self.serializer["r"](file_to_read.read())

    def write_to_file(self, file_obj, data):
        """Writes to opened file or file like object
        :param file_obj: opened file
        :param data: any serializable object
        """
        serialized = self.serializer["w"](data)
        file_obj.write(serialized)


class FileFormatBasedSerializer(Serializer):

    def get_serializer(self, path):
        extension = os.path.splitext(path)[1][1:]
        if extension not in self.serializers:
            raise error.BadDataException(
                'No serializer for provided file {0}'.format(path))
        return self.serializers[extension]

    def write_to_file(self, full_path, data):
        serializer = self.get_serializer(full_path)
        with open(full_path, "w+") as f:
            f.write(serializer["w"](data))
        return full_path

    def read_from_file(self, full_path):
        serializer = self.get_serializer(full_path)
        with open(full_path, "r") as f:
            return serializer["r"](f.read())


def listdir_without_extensions(dir_path):
    return ifilter(
        lambda f: f != "",
        imap(
            lambda f: f.split(".")[0],
            os.listdir(dir_path)
        )
    )
