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

import six

from fuelclient import objects
from fuelclient.v1 import base_v1


class TagClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Tag

    def get_all(self, **filters):
        """Get all available tags.

        :param filters: list of output filters
        :return: tags data as a list of dict
        :rtype: list
        """
        data = self._entity_wrapper.get_all()
        for item in data:
            for f_name, f_value in six.iteritems(filters):
                if f_value and item.get(f_name) != f_value:
                    break
            else:
                yield item

    def get_one(self, tag_id):
        return self._entity_wrapper.get_one(tag_id)

    def upload(self, data, tag_id):
        return self._entity_wrapper.upload(tag_id, data)

    def create(self, data, **kwargs):
        return self._entity_wrapper.create(data)

    def delete(self, tag_id):
        return self._entity_wrapper.delete(tag_id)

    def assign(self, tag_ids, node):
        return self._entity_wrapper.assign(tag_ids, node)

    def unassign(self, tag_ids, node):
        return self._entity_wrapper.unassign(tag_ids, node)


def get_client(connection):
    return TagClient(connection)
