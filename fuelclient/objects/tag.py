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

    class_api_path = "{}/{}/tags/"
    instance_api_path = "tags/{}/"
    assign_api_path = "nodes/{}/tags/"

    def get_tag(self):
        return self.connection.get_request(
            self.instance_api_path.format(self.id))

    def update_tag(self, data):
        return self.connection.put_request(
            self.instance_api_path.format(self.id), data)

    def delete_tag(self):
        return self.connection.delete_request(
            self.instance_api_path.format(self.id))

    @classmethod
    def get_all(cls, owner_type, owner_id):
        return cls.connection.get_request(
            cls.class_api_path.format(owner_type, owner_id))

    @classmethod
    def create_tag(cls, owner_type, owner_id, data):
        return cls.connection.post_request(
            cls.class_api_path.format(owner_type, owner_id),
            data)

    @classmethod
    def assign_tags(cls, tag_ids, node_id):
        return cls.connection.post_request(
            cls.assign_api_path.format(node_id), tag_ids)

    @classmethod
    def unassign_tags(cls, tag_ids, node_id):
        return cls.connection.delete_request(
            cls.assign_api_path.format(node_id), tag_ids)
