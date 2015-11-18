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


def get_fake_openstack_config(
        id=None, config_type=None, cluster_id=None, node_id=None,
        node_role=None, configuration=None):
    config = {
        'id': id or 42,
        'is_active': True,
        'config_type': config_type or 'cluster',
        'cluster_id': cluster_id or 84,
        'node_id': node_id or None,
        'node_role': node_role or None,
        'configuration': configuration or {
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
    return config
