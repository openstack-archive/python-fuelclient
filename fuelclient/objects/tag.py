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


from fuelclient.objects.base import BaseObject


class Tag(BaseObject):

    instance_api_path = "{owner_type}/{owner_id}/tags/"
    class_api_path = "{owner_type}/{owner_id}/tags/{tag_name}/"

    def __init__(self, owner_type, owner_id, **kwargs):
        super(Tag, self).__init__(owner_id, **kwargs)
        self.owner_type = owner_type

    def get_all(self):
        return self.connection.get_request(
            self.instance_api_path.format(owner_type=self.owner_type,
                                          owner_id=self.id))

    def get_tag(self, tag_name):
        return self.connection.get_request(
            self.class_api_path.format(owner_type=self.owner_type,
                                       owner_id=self.id,
                                       tag_name=tag_name))

    def update_tag(self, tag_name, data):
        return self.connection.put_request(
            self.class_api_path.format(owner_type=self.owner_type,
                                       owner_id=self.id,
                                       tag_name=tag_name),
            data)

    def create_tag(self, data):
        return self.connection.post_request(
            self.instance_api_path.format(owner_type=self.owner_type,
                                          owner_id=self.id),
            data)

    def delete_tag(self, tag_name):
        return self.connection.delete_request(
            self.class_api_path.format(owner_type=self.owner_type,
                                       owner_id=self.id,
                                       tag_name=tag_name))
