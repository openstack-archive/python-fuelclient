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

from argparse import Namespace

from fuelclient.cli.translator import translate_node_list_params
from fuelclient.tests.unit.v1 import base


class TestTranslator(base.UnitTestCase):

    def test_translate_node_list_params_with_expected_params(self):
        env_id = 1
        group_id = 2
        roles = ['role1', 'role2']
        status = 'error'
        online = True
        ns = Namespace(env=env_id, group=group_id, role=roles,
                       status=status, online=online)

        translated = translate_node_list_params(ns)

        self.assertEqual(
            translated,
            {
                'cluster_id': env_id,
                'group_id': group_id,
                'roles': roles,
                'status': status,
                'online': online
            })

    def test_translate_node_list_params_with_unexpected_params(self):
        """All extra params should be absent in the result."""
        env_id = 1
        group_id = 2
        roles = ['role1', 'role2']
        status = 'error'
        online = True
        ns = Namespace(env=env_id, group=group_id, role=roles,
                       status=status, online=online)

        translated = translate_node_list_params(ns)

        self.assertEqual(
            translated,
            {
                'cluster_id': env_id,
                'group_id': group_id,
                'roles': roles,
                'status': status,
                'online': online
            })

    def test_translate_node_list_params_include_only_not_none(self):
        """In the result params with `None` values should be absent."""
        env_id = 1
        group_id = None
        roles = ['role1', 'role2']
        status = None
        online = True
        ns = Namespace(env=env_id, group=group_id, role=roles,
                       status=status, online=online)

        translated = translate_node_list_params(ns)

        self.assertEqual(
            translated,
            {
                'cluster_id': env_id,
                'roles': roles,
                'online': online
            })
