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

# DO NOT PUT ANY IMPORTS HERE BECAUSE THIS FILE IS USED
# DURING THE INSTALLATION.

try:
    import pkg_resources
    try:
        __version__ = pkg_resources.get_distribution(
            "python-fuelclient").version
    except pkg_resources.DistributionNotFound:
        __version__ = ""
except ImportError:
    __version__ = ""


def get_client(resource, version='v1'):
    """Gets an API client for a resource

    python-fuelclient provides access to Fuel's API
    through a set of per-resource facades. In order to
    get a proper facade it's necessary to specify the name
    of the API resource and the version of Fuel's API.

    :param resource: Name of the resource to get a facade for.
    :type resource:  str
                     Valid values are environment, node and task
    :param version:  Version of the Fuel's API
    :type version:   str,
                     Available: v1. Default: v1.
    :return:         Facade to the specified resource that wraps
                     calls to the specified version of the API.

    """
    from fuelclient import v1

    version_map = {
        'v1': {
            'cluster-settings': v1.cluster_settings,
            'deployment_history': v1.deployment_history,
            'deployment-info': v1.deployment_info,
            'environment': v1.environment,
            'fuel-version': v1.fuelversion,
            'graph': v1.graph,
            'network-configuration': v1.network_configuration,
            'network-group': v1.network_group,
            'node': v1.node,
            'openstack-config': v1.openstack_config,
            'plugins': v1.plugins,
            'task': v1.task,
            'vip': v1.vip
        }
    }

    try:
        return version_map[version][resource].get_client()
    except KeyError:
        msg = 'Cannot load API client for "{r}" in the API version "{v}".'
        raise ValueError(msg.format(r=resource, v=version))
