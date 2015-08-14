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

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class NetworkGroupClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.NetworkGroup

    updatable_attributes = (
        'name', 'vlan', 'cidr', 'gateway', 'group_id', 'meta')

    def create(self, name, release, vlan, cidr,
               gateway, group_id, meta=None):
        net_group = self._entity_wrapper.create(
            name, release, vlan, cidr, gateway, group_id, meta)
        return net_group.data

    def update(self, network_id, **kwargs):
        for attr in kwargs:
            if attr not in self.updatable_attributes:
                raise error.BadDataException(
                    'Update of attribute "{0}" is not allowed'.format(attr))

        net_group = self._entity_wrapper(network_id)
        net_group.set(kwargs)

        return net_group.data

    def delete_by_id(self, network_id):
        env_obj = self._entity_wrapper(network_id)
        env_obj.delete()


def get_client():
    return NetworkGroupClient()
