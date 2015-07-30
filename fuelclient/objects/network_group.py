#    Copyright 2014 Mirantis, Inc.
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

from operator import attrgetter

from fuelclient.objects.base import BaseObject


class NetworkGroup(BaseObject):

    class_api_path = "networks/"
    instance_api_path = "networks/{0}/"

    @property
    def name(self):
        return self.get_fresh_data()["name"]

    @classmethod
    def create(cls, name, release, vlan, cidr, gateway,
               group_id, meta=None):

        metadata = {
            'notation': 'cidr',
            'render_type': None,
            'map_priority': 2,
            'configurable': True,
            'use_gateway': False,
            'name': name,
            'cidr': cidr,
            'vlan_start': vlan
        }
        if meta:
            metadata.update(meta)

        network_group = {
            'name': name,
            'release': release,
            'vlan_start': vlan,
            'cidr': cidr,
            'gateway': gateway,
            'meta': metadata,
            'group_id': group_id,
        }

        data = cls.connection.post_request(
            cls.class_api_path,
            network_group,
        )
        return cls.init_with_data(data)

    def set(self, data):
        vlan = data.pop('vlan', None)
        if vlan is not None:
            data['vlan_start'] = vlan

        return self.connection.put_request(
            self.instance_api_path.format(self.id), data)

    def delete(self):
        return self.connection.delete_request(
            self.instance_api_path.format(self.id)
        )


class NetworkGroupCollection(object):

    def __init__(self, networks):
        self.collection = networks

    @classmethod
    def init_with_ids(cls, ids):
        return cls(map(NetworkGroup, ids))

    @classmethod
    def init_with_data(cls, data):
        return cls(map(NetworkGroup.init_with_data, data))

    def __str__(self):
        return "{0} [{1}]".format(
            self.__class__.__name__,
            ", ".join(map(lambda n: str(n.id), self.collection))
        )

    def __iter__(self):
        return iter(self.collection)

    @property
    def data(self):
        return map(attrgetter("data"), self.collection)

    @classmethod
    def get_all(cls):
        return cls(NetworkGroup.get_all())

    def filter_by_group_id(self, group_id):
        self.collection = filter(lambda net: net.data['group_id'] == group_id,
                                 self.collection)
