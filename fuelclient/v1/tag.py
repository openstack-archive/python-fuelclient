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

    def update(self, tag_id, data):
        tag = self._entity_wrapper(obj_id=tag_id)
        return tag.update_tag(data)

    def create(self, data):
        return self._entity_wrapper.create_tag(data)

    def delete_by_id(self, tag_id):
        tag = self._entity_wrapper(obj_id=tag_id)
        return tag.delete_tag()

    def assign(self, tag_ids, node):
        return self._entity_wrapper.assign_tags(tag_ids, node)

    def unassign(self, tag_ids, node):
        return self._entity_wrapper.unassign_tags(tag_ids, node)


def get_client(connection):
    return TagClient(connection)
