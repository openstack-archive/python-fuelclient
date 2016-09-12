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

import json
import os
import yaml

from fuelclient import utils


def get_display_data_single(fields, data, missing_field_value=None):
    """Performs slicing of data by set of given fields

    :param fields: Iterable containing names of fields to be retrieved
                   from data
    :param data:   Collection of JSON objects representing some
                   external entities
    :param missing_field_value: the value will be used for all missing fields

    :return:       list containing the collection of values of the
                   supplied attributes.

    """
    return [data.get(field, missing_field_value) for field in fields]


def get_display_data_multi(fields, data):
    """Performs slice of data by set of given fields for multiple objects."""

    return [get_display_data_single(fields, elem) for elem in data]


def safe_load(data_format, stream):
    loaders = {'json': utils.safe_deserialize(json.load),
               'yaml': utils.safe_deserialize(yaml.safe_load)}

    if data_format not in loaders:
        raise ValueError('Unsupported data format.')

    loader = loaders[data_format]
    return loader(stream)


def safe_dump(data_format, stream, data):
    # The reason these dumpers are assigned to individual variables is
    # making PEP8 check happy.
    yaml_dumper = lambda data, stream: yaml.safe_dump(data,
                                                      stream,
                                                      default_flow_style=False)
    json_dumper = lambda data, stream: json.dump(data, stream, indent=4)
    dumpers = {'json': json_dumper,
               'yaml': yaml_dumper}

    if data_format not in dumpers:
        raise ValueError('Unsupported data format.')

    dumper = dumpers[data_format]
    dumper(data, stream)


def read_from_file(file_path):
    data_format = os.path.splitext(file_path)[1].lstrip('.')
    with open(file_path, 'r') as stream:
        return safe_load(data_format, stream)


def write_to_file(file_path, data):
    data_format = os.path.splitext(file_path)[1].lstrip('.')
    with open(file_path, 'w') as stream:
        safe_dump(data_format, stream, data)
