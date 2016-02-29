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

from fuelclient.cli import error


def get_display_data_single(fields, data):
    """Performs slicing of data by set of given fields

    :param fields: Iterable containing names of fields to be retrieved
                   from data
    :param data:   Collection of JSON objects representing some
                   external entities

    :return:       list containing the collection of values of the
                   supplied attributes.

    """
    try:
        return [data[field] for field in fields]
    except KeyError as e:
        raise error.BadDataException('{} is not found in the supplied '
                                     'data.'.format(e.args[0]))


def get_display_data_multi(fields, data):
    """Performs slice of data by set of given fields for multiple objects."""

    return [get_display_data_single(fields, elem) for elem in data]
