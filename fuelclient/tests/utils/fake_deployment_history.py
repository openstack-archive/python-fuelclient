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
import itertools


def get_fake_deployment_history(
        add_task_data=False, convert_legacy_fields=False,
        include_summary=False):
    """Create a fake deployment history.

    Returns the serialized and parametrized representation of a dumped Fuel
    Deployment History. Represents the average amount of data.

    :param add_task_data: add task description to history records using
                          Fuel 10.0 history output format
    :type add_task_data: bool
    :param convert_legacy_fields: Fuel 9.0 output fields are renamed to 10.0
                                  if True
    :type convert_legacy_fields: True
    :returns: fake deployment fixtures
    :rtype: list[dict]
    """
    if add_task_data:
        result = list(itertools.chain(*[[
            {
                'status': 'ready',
                'time_start': '2016-03-25T17:22:10.687135',
                'time_end': '2016-03-25T17:22:30.830701',
                'node_id': node_id,
                'task_name': 'controller-remaining-tasks',
                'type': 'puppet',
                'role': ['controller'],
                'version': '2.0.0',
                'parameters': {
                    'puppet_manifest': '/etc/puppet/modules/osnailyfacter'
                                       '/modular/globals/globals.pp',
                    'puppet_modules': '/etc/puppet/modules',
                    'timeout': 3600
                },
            },
            {
                'status': 'skipped',
                'time_start': '2016-03-25T17:23:37.313212',
                'time_end': '2016-03-25T17:23:37.313234',
                'node_id': node_id,
                'task_name': 'ironic-compute',
                'type': 'puppet',
                'role': ['controller'],
                'version': '2.0.0',
                'parameters': {
                    'puppet_manifest': '/etc/puppet/modules/osnailyfacter'
                                       '/modular/globals/globals.pp',
                    'puppet_modules': '/etc/puppet/modules',
                    'timeout': 3600
                }
            },
            {
                'status': 'pending',
                'time_start': None,
                'node_id': node_id,
                'task_name': 'pending-task',
                'type': 'puppet',
                'role': ['controller'],
                'version': '2.0.0',
                'parameters': {
                    'puppet_manifest': '/etc/puppet/modules/osnailyfacter'
                                       '/modular/globals/globals.pp',
                    'puppet_modules': '/etc/puppet/modules',
                    'timeout': 3600
                }
            }
        ] for node_id in ['1', '2']]))
    else:
        result = list(itertools.chain(*[[
            {
                'status': 'ready',
                'time_start': '2016-03-25T17:22:10.687135',
                'time_end': '2016-03-25T17:22:30.830701',
                'node_id': node_id,
                'deployment_graph_task_name': 'controller-remaining-tasks',
            },
            {
                'status': 'skipped',
                'time_start': '2016-03-25T17:23:37.313212',
                'time_end': '2016-03-25T17:23:37.313234',
                'node_id': node_id,
                'deployment_graph_task_name': 'ironic-compute'
            },
            {
                'status': 'pending',
                'time_start': None,
                'node_id': node_id,
                'deployment_graph_task_name': 'pending-task'
            }
        ] for node_id in ['1', '2']]))

        if convert_legacy_fields:
            for record in result:
                record['task_name'] = record['deployment_graph_task_name']
                record.pop('deployment_graph_task_name', None)
    if include_summary:
        for record in result:
            record['summary'] = '{}'
    return result


def get_fake_deployment_history_w_params():
    return [
        {
            'task_name': 'controller-remaining-tasks',
            'task_parameters': 'parameters: {puppet_manifest: /etc/puppet/'
                               'modules/osnailyfacter/modular/globals/'
                               'globals.pp,\n  puppet_modules: /etc/'
                               'puppet/modules, timeout: 3600}\nrole: '
                               '[controller]\ntype: puppet\nversion: 2.0.0'
                               '\n',
            'status_by_node': '1 - ready - 2016-03-25T17:22:10 - '
                              '2016-03-25T17:22:30\n'
                              '2 - ready - 2016-03-25T17:22:10 - '
                              '2016-03-25T17:22:30'
        },
        {
            'task_name': 'pending-task',
            'task_parameters': 'parameters: {puppet_manifest: /etc/puppet/'
                               'modules/osnailyfacter/modular/globals/'
                               'globals.pp,\n  puppet_modules: /etc/puppet'
                               '/modules, timeout: 3600}\nrole: '
                               '[controller]\ntype: puppet\nversion: 2.0.0'
                               '\n',
            'status_by_node': '1 - pending - not started - not ended\n'
                              '2 - pending - not started - not ended'
        },
        {
            'task_name': 'ironic-compute',
            'status_by_node': '1 - skipped - 2016-03-25T17:23:37 - '
                              '2016-03-25T17:23:37\n2 - skipped - '
                              '2016-03-25T17:23:37 - 2016-03-25T17:23:37',
            'task_parameters': 'parameters: {puppet_manifest: /etc/puppet/'
                               'modules/osnailyfacter/modular/globals/'
                               'globals.pp,\n  puppet_modules: /etc/'
                               'puppet/modules, timeout: 3600}\nrole: '
                               '[controller]\ntype: puppet\nversion: 2.0.0\n'},
    ]
