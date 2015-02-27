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

    class_api_path = "releases/{release_id}/roles/"
    instance_api_path = "releases/{release_id}/roles/{role_name}/"

    @classmethod
    def get_all(cls, release_id):
        return cls.connection.get_request(
            cls.class_api_path.format(release_id=release_id))

    @classmethod
    def get_one(cls, release_id, role_name):
        return cls.connection.get_request(
            cls.instance_api_path.format(
                release_id=release_id, role_name=role_name))

    @classmethod
    def update(cls, release_id, role_name, data):
        return cls.connection.put_request(
            cls.instance_api_path.format(
                release_id=release_id, role_name=role_name), data)

    @classmethod
    def create(cls, release_id, data):
        return cls.connection.post_request(
            cls.class_api_path.format(release_id=release_id), data)

    @classmethod
    def delete(cls, release_id, role_name):
        return cls.connection.delete_request(
            cls.instance_api_path.format(
                release_id=release_id, role_name=role_name))
