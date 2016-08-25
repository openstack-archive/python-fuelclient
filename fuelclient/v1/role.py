# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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


from fuelclient import objects
from fuelclient.v1 import base_v1


class RoleClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Role

    def get_all(self, release_id):
        """Get all available roles for specific release.

        :param release_id: Id of release
        :type release_id: int
        :return: roles data as a list of dict
        :rtype: list
        """
        data = self._entity_wrapper.get_all(release_id=release_id)
        # Retrieve nested data from 'meta' and add it as a new key-value pair
        for role in data:
            role_meta = role.pop('meta')
            role['group'] = role_meta.get('group')
            role['conflicts'] = role_meta.get('conflicts')
            role['description'] = role_meta.get('description')

        return data

    def get_one(self, release_id, role_name):
        return self._entity_wrapper.get_one(release_id, role_name)

    def update(self, data, **kwargs):
        return self._entity_wrapper.update(kwargs['release_id'],
                                           kwargs['role_name'],
                                           data)

    def create(self, data, **kwargs):
        return self._entity_wrapper.create(kwargs['release_id'], data)

    def delete(self, release_id, role_name):
        return self._entity_wrapper.delete(release_id, role_name)


def get_client(connection):
    return RoleClient(connection)
