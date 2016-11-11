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

from fuelclient.tests.utils.random_data import random_string
from fuelclient.tests.utils.fake_additional_info \
    import get_fake_yaml_cluster_settings
from fuelclient.tests.utils.fake_additional_info \
    import get_fake_yaml_deployment_info
from fuelclient.tests.utils.fake_additional_info \
    import get_fake_yaml_network_conf
from fuelclient.tests.utils.fake_additional_info \
    import get_fake_env_network_conf
from fuelclient.tests.utils.fake_deployment_history \
    import get_fake_deployment_history
from fuelclient.tests.utils.fake_deployment_history \
    import get_fake_deployment_history_w_params
from fuelclient.tests.utils.fake_net_conf import get_fake_interface_config
from fuelclient.tests.utils.fake_net_conf import get_fake_network_config
from fuelclient.tests.utils.fake_network_group import get_fake_network_group
from fuelclient.tests.utils.fake_node import get_fake_node
from fuelclient.tests.utils.fake_env import get_fake_env
from fuelclient.tests.utils.fake_extension import get_fake_env_extensions
from fuelclient.tests.utils.fake_extension import get_fake_extension
from fuelclient.tests.utils.fake_extension import get_fake_extensions
from fuelclient.tests.utils.fake_fuel_version import get_fake_fuel_version
from fuelclient.tests.utils.fake_health import get_fake_test_set
from fuelclient.tests.utils.fake_health import get_fake_test_sets
from fuelclient.tests.utils.fake_health import get_fake_test_set_item
from fuelclient.tests.utils.fake_health import get_fake_test_set_items
from fuelclient.tests.utils.fake_task import get_fake_task
from fuelclient.tests.utils.fake_node_group import get_fake_node_group
from fuelclient.tests.utils.fake_node_group import get_fake_node_groups
from fuelclient.tests.utils.fake_openstack_config  \
    import get_fake_openstack_config
from fuelclient.tests.utils.fake_plugin import get_fake_plugin
from fuelclient.tests.utils.fake_plugin import get_fake_plugins
from fuelclient.tests.utils.fake_release import get_fake_release
from fuelclient.tests.utils.fake_release import get_fake_releases
from fuelclient.tests.utils.fake_release import get_fake_attributes_metadata
from fuelclient.tests.utils.fake_release import get_fake_release_component
from fuelclient.tests.utils.fake_release import get_fake_release_components
from fuelclient.tests.utils.fake_role import get_fake_role
from fuelclient.tests.utils.fake_role import get_fake_roles
from fuelclient.tests.utils.fake_tag import get_fake_tag
from fuelclient.tests.utils.fake_tag import get_fake_tags


__all__ = (get_fake_deployment_history,
           get_fake_deployment_history_w_params,
           get_fake_yaml_cluster_settings,
           get_fake_yaml_deployment_info,
           get_fake_yaml_network_conf,
           get_fake_env,
           get_fake_env_network_conf,
           get_fake_test_set,
           get_fake_test_sets,
           get_fake_test_set_item,
           get_fake_test_set_items,
           get_fake_release,
           get_fake_releases,
           get_fake_attributes_metadata,
           get_fake_release_component,
           get_fake_release_components,
           get_fake_role,
           get_fake_roles,
           get_fake_fuel_version,
           get_fake_interface_config,
           get_fake_network_group,
           get_fake_node,
           get_fake_network_config,
           get_fake_task,
           random_string,
           get_fake_node_group,
           get_fake_node_groups,
           get_fake_openstack_config,
           get_fake_plugin,
           get_fake_plugins,
           get_fake_tag,
           get_fake_tags)
