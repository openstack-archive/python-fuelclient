# -*- coding:utf8 -*-
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

from six import moves as six_moves


def get_fake_plugin(**kwargs):
    """Creates a fake plugin

    Returns the serialized and parametrized representation of a dumped Fuel
    Plugin. Represents the average amount of data.

    """
    plugin_id = kwargs.get('plugin_id', 1)
    return {'id': plugin_id,
            'name': kwargs.get('name', 'plugin_name_{0}'.format(plugin_id)),
            'title': kwargs.get('title', 'plugin_title'),
            'version': kwargs.get('version', '1.0.0'),
            'description': kwargs.get('description', 'plugin_description'),
            'authors': kwargs.get('authors', ['author1', 'author2']),
            'package_version': kwargs.get('package_version', '3.0.0'),
            'releases': kwargs.get('releases', [{'os': 'ubuntu',
                                                 'version': 'liberty-8.0'},
                                                {'os': 'ubuntu',
                                                 'version': 'mitaka-9.0'}]),
            'is_hotpluggable': kwargs.get('is_hotpluggable', True)}


def get_fake_plugins(plugins_number, **kwargs):
    """Creates fake plugins list."""
    return [get_fake_plugin(plugin_id=i, **kwargs)
            for i in six_moves.range(1, plugins_number + 1)]
