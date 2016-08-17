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

from fuelclient.cli.serializers import Serializer
from fuelclient.client import DefaultAPIClient


class BaseObject(object):
    """BaseObject class - base class for fuelclient.objects object classes

    'class_api_path' - url path to object handler on Nailgun server.
    'instance_api_path' - url path template which formatted with object id
    returns only one serialized object.
    'connection' - 'APIClient' class instance from fuelclient.client
    """
    class_api_path = None
    instance_api_path = None
    connection = DefaultAPIClient

    def __init__(self, obj_id, **kwargs):
        self.connection = DefaultAPIClient
        self.serializer = Serializer.from_params(kwargs.get('params'))
        self.id = obj_id
        self._data = None

    @classmethod
    def init_with_data(cls, data):
        instance = cls(data["id"])
        instance._data = data
        return instance

    @classmethod
    def get_by_ids(cls, ids):
        return map(cls, ids)

    def update(self):
        self._data = self.connection.get_request(
            self.instance_api_path.format(self.id))

    def get_fresh_data(self):
        self.update()
        return self.data

    @property
    def data(self):
        if self._data is None:
            return self.get_fresh_data()
        else:
            return self._data

    @classmethod
    def get_all_data(cls):
        return cls.connection.get_request(cls.class_api_path)

    @classmethod
    def get_all(cls):
        return map(cls.init_with_data, cls.get_all_data())

    @classmethod
    def get_filtered_data(cls, **filters):
        """Get filtered data by specified filters

        :param filters: key-value params passed to GET request, e.g.
                        {'filter1': 'value1', 'filter2': 'value1,value2'}
        :type filters: dict
        :return: Filtered data
        :rtype: list
        """
        return cls.connection.get_request(cls.class_api_path, params=filters)
