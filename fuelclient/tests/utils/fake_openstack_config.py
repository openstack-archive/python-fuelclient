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


def get_fake_openstack_config(**kwargs):
    config = {
        'id': 42,
        'is_active': True,
        'config_type': 'cluster',
        'cluster_id': 84,
        'node_id': None,
        'node_role': None,
        'configuration': {
            'nova_config': {
                'DEFAULT/debug': {
                    'value': True,
                },
            },
            'keystone_config': {
                'DEFAULT/debug': {
                    'value': True,
                },
            },
        },
    }
    config.update(kwargs)
    return config
