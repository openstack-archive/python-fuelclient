# -*- coding: utf-8 -*-
#
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


def get_fake_env(name=None, status=None, release_id=None,
                 fuel_version=None, pending_release=None, env_id=None,
                 net_provider=None):
    """Create a random fake environment

    Returns the serialized and parametrized representation of a dumped Fuel
    environment. Represents the average amount of data.

    """
    return {'status': status or 'new',
            'is_customized': False,
            'release_id': release_id or 2,
            'name': name or 'fake_env',
            'net_provider': net_provider or 'neutron',
            'net_segment_type': 'gre',
            'fuel_version': fuel_version or '5.1',
            'pending_release_id': pending_release,
            'id': env_id or 1,
            'changes': [],
            'mode': 'multinode'}
