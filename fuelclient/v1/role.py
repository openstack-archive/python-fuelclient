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

    def get_all(self, owner_type, owner_id):
        """Get all available roles for specific release or cluster.

        :param owner_type: release or cluster
        :type owner_id: int
        :return: roles data as a list of dict
        :rtype: list
        """

        data = self._entity_wrapper(owner_type, owner_id).get_all()

        # Retrieve nested data from 'meta' and add it as a new key-value pair
        for role in data:
            role_meta = role.pop('meta')
            role['group'] = role_meta.get('group')
            role['conflicts'] = role_meta.get('conflicts')
            role['description'] = role_meta.get('description')

        return data

    def get_one(self, owner_type, owner_id, role_name):
        role = self._entity_wrapper(owner_type, owner_id)
        return role.get_role(role_name)

    def update(self, data, **kwargs):
        role = self._entity_wrapper(owner_type=kwargs['owner_type'],
                                    owner_id=kwargs['owner_id'])
        return role.update_role(kwargs['role_name'], data)

    def create(self, data, **kwargs):
        role = self._entity_wrapper(owner_type=kwargs['owner_type'],
                                    owner_id=kwargs['owner_id'])
        return role.create_role(data)

    def delete(self, owner_type, owner_id, role_name):
        role = self._entity_wrapper(owner_type=owner_type,
                                    owner_id=owner_id)
        return role.delete_role(role_name)


def get_client(connection):
    return RoleClient(connection)
