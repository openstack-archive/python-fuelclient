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


class Role(BaseObject):

    class_api_path = "roles/"
    instance_api_path = "roles/{role_id}/"

    @classmethod
    def get_all(self):
        return self.connection.get_request(self.class_api_path)

    @classmethod
    def get_one(self, role_id):
        return self.connection.get_request(
            self.instance_api_path.format(role_id=role_id))

    @classmethod
    def update(self, role_id, data):
        return self.connection.put_request(
            self.instance_api_path.format(role_id=role_id), data)

    @classmethod
    def create(self, data):
        return self.connection.post_request(self.class_api_path, data)
