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


def translate_node_list_params(parsed_args):
    """Translate node list params.

    Translate command line params for node list to the params which are
    used by API.

    :param parsed_args: parsed arguments by argparse
    :type parsed_args: Namespace
    :returns: dict - translated values, where each key is the param name \
              which is used by API and a value is a value for that param.
    """

    result = {}

    params_map = {
        'env': 'cluster_id',
        'group': 'group_id',
        'role': 'roles',
        'status': 'status',
        'online': 'online'
    }

    for cmd_param_name, api_param_name in six.iteritems(params_map):
        value = getattr(parsed_args, cmd_param_name)
        if value is not None:
            result[api_param_name] = value

    return result
