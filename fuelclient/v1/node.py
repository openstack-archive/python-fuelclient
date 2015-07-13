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

from fuelclient import objects
from fuelclient.v1 import base_v1


class NodeClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Node

    def get_all(self, environment_id=None):
        result = self._entity_wrapper.get_all_data()

        if environment_id is not None:
            result = filter(lambda n: n['cluster'] == environment_id, result)

        return result

    def set_hostname(self, node_id, hostname):
        node = self._entity_wrapper(node_id)
        return node.set_hostname(hostname)


def get_client():
    return NodeClient()
