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


from fuelclient.objects.base import BaseObject


class Tag(BaseObject):

    class_api_path = "tags/"
    instance_api_path = "tags/{tag_id}/"
    assign_api_path = 'nodes/{node_id}/tags/assign/'
    unassign_api_path = 'nodes/{node_id}/tags/unassign/'

    @classmethod
    def get_all(cls):
        return cls.connection.get_request(cls.class_api_path)

    @classmethod
    def get_one(cls, tag_id):
        return cls.connection.get_request(
            cls.instance_api_path.format(tag_id=tag_id))

    @classmethod
    def update(cls, tag_id, data):
        return cls.connection.put_request(
            cls.instance_api_path.format(tag_id=tag_id), data)

    @classmethod
    def create(cls, release_id, data):
        return cls.connection.post_request(
            cls.class_api_path.format(release_id=release_id), data)

    @classmethod
    def delete(cls, tag_id):
        return cls.connection.delete_request(
            cls.instance_api_path.format(tag_id=tag_id))

    @classmethod
    def assign(cls, tag_ids, node_id):
        return cls.connection.post_request(
            cls.assign_api_path.format(node_id=node_id), tag_ids)

    @classmethod
    def unassign(cls, tag_ids, node_id):
        return cls.connection.post_request(
            cls.unassign_api_path.format(node_id=node_id), tag_ids)
