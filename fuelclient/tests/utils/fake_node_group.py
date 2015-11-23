# -*- coding: utf-8 -*-
#
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


def get_fake_node_group(name=None, cluster_id=None, id=None):
    """Create a random fake network node group

    Returns the serialized and parametrized representation of a dumped Fuel
    nodegroup. Represents the average amount of data.

    """
    return {
        'name': name or 'testng',
        'id': id or 42,
        'cluster_id': cluster_id or 5,
    }


def get_fake_node_groups():
    """Create a fake network node group list

    Returns the serialized and parametrized representation of a dumped Fuel
    nodegroups list.

    """
    return [
        {"cluster_id": 1, "id": 1, "name": "default"},
        {"cluster_id": 1, "id": 2, "name": "custom-group"}
    ]
