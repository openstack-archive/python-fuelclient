# -*- coding:utf8 -*-
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

from six import moves as six_moves


def get_fake_plugin(plugin_id=None, name=None, title=None, version=None,
                    description=None, authors=None, package_version=None,
                    releases=None, is_hotpluggable=None):
    """Creates a fake plugin

    Returns the serialized and parametrized representation of a dumped Fuel
    Plugin. Represents the average amount of data.

    """
    return {'id': plugin_id or 1,
            'names': name or 'plugin_name',
            'title': title or 'plugin_title',
            'version': version or '1.0.0',
            'description': description or 'plugin_description',
            'authors': authors or ['author1', 'author2'],
            'package_version': package_version or '3.0.0',
            'releases': releases or [{'os': 'ubuntu',
                                      'version': 'liberty-8.0'},
                                     {'os': 'ubuntu',
                                      'version': 'mitaka-9.0'}],
            'is_hotpluggable': is_hotpluggable or True}


def get_fake_plugins(plugins_number):
    """Creates fake plugins list."""

    return [get_fake_plugin(plugin_id=i, name='plugin_name_{0}'.format(i))
            for i in six_moves.range(1, plugins_number + 1)]
