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

import os

import six

from fuelclient.cli import error
from fuelclient.cli.serializers import Serializer
from fuelclient.objects.base import BaseObject


class OpenstackConfig(BaseObject):

    class_api_path = 'openstack-config/'
    instance_api_path = 'openstack-config/{0}/'
    execute_api_path = 'openstack-config/execute/'

    @classmethod
    def _prepare_params(cls, filters):
        return dict((k, v) for k, v in six.iteritems(filters) if v is not None)

    @classmethod
    def create(cls, **kwargs):
        params = cls._prepare_params(kwargs)
        data = cls.connection.post_request(cls.class_api_path, params)
        return [cls.init_with_data(item) for item in data]

    def delete(self):
        return self.connection.delete_request(
            self.instance_api_path.format(self.id))

    @classmethod
    def execute(cls, **kwargs):
        params = cls._prepare_params(kwargs)
        return cls.connection.put_request(cls.execute_api_path, params)

    @classmethod
    def get_filtered_data(cls, **kwargs):
        url = cls.class_api_path
        params = cls._prepare_params(kwargs)

        node_ids = params.get('node_ids')
        if node_ids is not None:
            params['node_ids'] = ','.join([str(n) for n in node_ids])

        return cls.connection.get_request(url, params=params)

    @classmethod
    def read_file(cls, path):
        if not os.path.exists(path):
            raise error.InvalidFileException(
                "File '{0}' doesn't exist.".format(path))

        serializer = Serializer()
        return serializer.read_from_full_path(path)

    @classmethod
    def write_file(cls, path, data):
        serializer = Serializer()
        return serializer.write_to_full_path(path, data)
