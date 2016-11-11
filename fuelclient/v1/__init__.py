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

from fuelclient.v1 import cluster_settings
from fuelclient.v1 import deployment_history
from fuelclient.v1 import deployment_info
from fuelclient.v1 import environment
from fuelclient.v1 import extension
from fuelclient.v1 import fuelversion
from fuelclient.v1 import graph
from fuelclient.v1 import health
from fuelclient.v1 import network_configuration
from fuelclient.v1 import network_group
from fuelclient.v1 import node
from fuelclient.v1 import openstack_config
from fuelclient.v1 import release
from fuelclient.v1 import role
from fuelclient.v1 import plugins
from fuelclient.v1 import sequence
from fuelclient.v1 import snapshot
from fuelclient.v1 import task
from fuelclient.v1 import tag
from fuelclient.v1 import vip

# Please keeps the list in alphabetical order
__all__ = ('cluster_settings',
           'deployment_history',
           'deployment_info',
           'environment',
           'extension',
           'fuelversion',
           'graph',
           'health',
           'network_configuration',
           'network_group',
           'node',
           'openstack_config',
           'plugins',
           'release',
           'role',
           'sequence',
           'snapshot',
           'task',
           'tag',
           'vip')
