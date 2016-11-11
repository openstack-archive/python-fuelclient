# -*- coding: utf-8 -*-
#
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


from fuelclient import objects
from fuelclient.v1 import base_v1


class TagClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Tag

    def get_all(self, owner_type, owner_id):
        """Get all available tags for specific release or cluster.

        :param owner_type: release or cluster
        :type owner_id: int
        :return: tags data as a list of dict
        :rtype: list
        """
        tags = self._entity_wrapper(owner_type, owner_id).get_all()
        return tags

    def get_tag(self, owner_type, owner_id, tag_name=''):
        tag = self._entity_wrapper(owner_type, owner_id)
        return tag.get_tag(tag_name)

    def update(self, data, **kwargs):
        tag = self._entity_wrapper(owner_type=kwargs['owner_type'],
                                   owner_id=kwargs['owner_id'])
        return tag.update_tag(kwargs['tag_name'], data)

    def create(self, data, **kwargs):
        tag = self._entity_wrapper(owner_type=kwargs['owner_type'],
                                   owner_id=kwargs['owner_id'])
        return tag.create_tag(data)

    def delete(self, owner_type, owner_id, tag_name):
        tag = self._entity_wrapper(owner_type=owner_type, owner_id=owner_id)
        return tag.delete_tag(tag_name)


def get_client(connection):
    return TagClient(connection)
