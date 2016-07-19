# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

import yaml


CLUSTER_SETTINGS = '''---
  editable:
    service_user:
      name:
        type: "hidden"
        value: "fuel"
      sudo:
        type: "hidden"
        value: "ALL=(ALL) NOPASSWD: ALL"
      homedir:
        type: "hidden"
        value: "/var/lib/fuel"
'''

DEPLOYMENT_INFO = '''---
glance_glare:
  user_password: yBw0bY60owLC1C0AplHpEiEX
user_node_name: Untitled (5e:89)
uid: '5'
aodh:
  db_password: JnEjYacrjxU2TLdTUQE9LdKq
  user_password: 8MhyQgtWjWkl0Dv1r1worTjK
mysql:
  root_password: bQhzpWjWIOTHOwEA4qNI8X4K
  wsrep_password: 01QSoq3bYHgA7oS0OPYQurgX
murano-cfapi:
  db_password: hGrAhxUjv3kAPEjiV7uYNwgZ
  user_password: 43x0pvQMXugwd8JBaRSQXX4l
  enabled: false
  rabbit_password: ZqTnnw7lsGQNOFJRN6pTaI8t
'''

NETWORK_CONF = '''---
  vips:
    vrouter_pub:
      network_role: "public/vip"
      ipaddr: "10.109.3.2"
      namespace: "vrouter"
      is_user_defined: false
      vendor_specific:
        iptables_rules:
          ns_start:
            - "iptables -t nat -A POSTROUTING -o <%INT%> -j MASQUERADE"
'''


def get_fake_yaml_cluster_settings():
    """Create a fake cluster settings

    Returns the serialized and parametrized representation of a dumped Fuel
    Cluster Settings. Represents the average amount of data.

    """
    return CLUSTER_SETTINGS


def get_fake_yaml_deployment_info():
    """Create a fake cluster settings

    Returns the serialized and parametrized representation of a dumped Fuel
    Deployment Info. Represents the average amount of data.

    """
    return DEPLOYMENT_INFO


def get_fake_yaml_network_conf():
    """Create a fake cluster settings

    Returns the serialized and parametrized representation of a dumped Fuel
    Network Conf. Represents the average amount of data.

    """
    return NETWORK_CONF


def get_fake_env_network_conf():
    return yaml.load(get_fake_yaml_network_conf())
