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

    def __init__(self, owner_type, owner_id, **kwargs):
        super(Role, self).__init__(owner_id, **kwargs)
        self.owner_type = owner_type
        self.instance_api_path = "{owner_type}/{owner_id}/roles/"
        self.role_api_path = "{owner_type}/{owner_id}/roles/{role_name}/"

    def get_role(self, role_name):
        return self.connection.get_request(
            self.role_api_path.format(
                owner_type=self.owner_type,
                owner_id=self.id,
                role_name=role_name))

    def update_role(self, role_name, data):
        return self.connection.put_request(
            self.role_api_path.format(
                owner_type=self.owner_type,
                owner_id=self.id,
                role_name=role_name),
            data)

    def create_role(self, data):
        return self.connection.post_request(
            self.instance_api_path.format(
                owner_type=self.owner_type, owner_id=self.id), data)

    def delete_role(self, role_name):
        return self.connection.delete_request(
            self.role_api_path.format(
                owner_type=self.owner_type,
                owner_id=self.id,
                role_name=role_name))

    def update(self):
        """This method was overridden to add additional
        argument in API called and he does not update the object.
           """
        self._data = self.connection.get_request(
            self.instance_api_path.format(owner_type=self.owner_type,
                                          owner_id=self.id))
