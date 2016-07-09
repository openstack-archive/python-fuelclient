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


class ReleaseClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Release

    def update_attributes_metadata_by_id(self, release_id, data):
        release_obj = self._entity_wrapper(obj_id=release_id)
        release_obj.update_attributes_metadata(data)

    def get_attributes_metadata_by_id(self, release_id):
        release_obj = self._entity_wrapper(obj_id=release_id)
        return release_obj.get_attributes_metadata()

    def get_components_by_id(self, release_id):
        release_obj = self._entity_wrapper(obj_id=release_id)
        return release_obj.get_components()


def get_client(connection):
    return ReleaseClient(connection)
