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
import six

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class NodeClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Node
    _updatable_attributes = ('hostname',)

    def get_all(self, environment_id=None):
        result = self._entity_wrapper.get_all_data()

        if environment_id is not None:
            result = filter(lambda n: n['cluster'] == environment_id, result)

        return result

    def get_node_vms_conf(self, node_id):
        node = self._entity_wrapper(node_id)
        return node.get_node_vms_conf()

    def node_vms_create(self, node_id, config):
        node = self._entity_wrapper(node_id)
        return node.node_vms_create(config)

    def update(self, node_id, **kwargs):
        allowed_changes = {}
        extra_args = {}

        for i in six.iterkeys(kwargs):
            if i in self._updatable_attributes:
                allowed_changes[i] = kwargs[i]
            else:
                extra_args[i] = kwargs[i]

        if extra_args != {}:
            msg = 'Only {0} are updatable'.format(self._updatable_attributes)
            raise error.ArgumentException(msg)

        node = self._entity_wrapper(obj_id=node_id)
        return node.set(allowed_changes)


def get_client():
    return NodeClient()
