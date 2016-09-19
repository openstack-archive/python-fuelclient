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

    instance_api_path = "releases/{0}/roles/"
    role_api_path = "releases/{0}/roles/{1}/"

    def get_role(self, role_name):
        return self.connection.get_request(
            self.role_api_path.format(self.id, role_name))

    def update_role(self, role_name, data):
        return self.connection.put_request(
            self.role_api_path.format(self.id, role_name), data)

    def create_role(self, data):
        return self.connection.post_request(
            self.instance_api_path.format(self.id), data)

    def delete_role(self, role_name):
        return self.connection.delete_request(
            self.role_api_path.format(self.id, role_name))
