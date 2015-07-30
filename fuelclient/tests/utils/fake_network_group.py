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


def get_fake_network_group(
        name=None, release=None, vlan=None, cidr=None, gateway=None,
        group_id=None, meta=None, net_id=None):
    """Create a random fake network group

    Returns the serialized and parametrized representation of a dumped Fuel
    environment. Represents the average amount of data.

    """
    return {
        'name': name or 'testng',
        'release': release or 24,
        'vlan_start': vlan or 10,
        'cidr': cidr or '10.0.0.0/24',
        'gateway': gateway or '10.0.0.1',
        'group_id': group_id or 42,
        'meta': meta or {'notation': 'cidr'},
        'id': net_id or 42,
    }
