# -*- coding: utf-8 -*-

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

import mock

from fuelclient.cli.actions import node
from fuelclient.cli import error
from fuelclient.tests.unit.v1 import base


class TestNodeSetAction(base.UnitTestCase):

    def setUp(self):
        super(TestNodeSetAction, self).setUp()
        self.node_action = node.NodeAction()
        self.node_id = 1
        self.params = mock.Mock()
        self.params.node = [self.node_id]

    def test_more_than_one_node(self):
        mput = self.m_request.put('/api/v1/nodes/{0}/'.format(self.node_id))
        self.params.hostname = 'whatever'
        self.params.name = 'whatever2'
        self.params.node = [1, 2]

        error_msg = r"You should select only one node to change\."
        with self.assertRaisesRegexp(error.ArgumentException, error_msg):
            self.node_action.set_hostname(self.params)

        with self.assertRaisesRegexp(error.ArgumentException, error_msg):
            self.node_action.set_name(self.params)

        self.assertFalse(mput.called)

    def test_set_name(self):
        test_cases = ('new-name', 'New Name', u'śćż∑ Pó', u'测试 测试')
        for name in test_cases:
            self.params.name = name
            mput = self.m_request.put(
                '/api/v1/nodes/{0}/'.format(self.node_id),
                json={})
            with mock.patch.object(self.node_action.serializer,
                                   'print_to_output') as mprint:
                self.node_action.set_name(self.params)

            self.assertEqual(mput.call_count, 1)
            self.assertEqual({'name': name}, mput.last_request.json())
            mprint.assert_called_once_with(
                {},
                u"Name for node with id {0} has been changed to {1}.".format(
                    self.node_id, name)
            )

    def test_set_hostname(self):
        new_hostname = 'new_hostname'
        self.params.hostname = new_hostname

        mput = self.m_request.put(
            '/api/v1/nodes/{0}/'.format(self.node_id),
            json={})

        with mock.patch.object(self.node_action.serializer,
                               'print_to_output') as mprint:
            self.node_action.set_hostname(self.params)

        self.assertEqual(mput.call_count, 1)
        self.assertEqual({'hostname': new_hostname}, mput.last_request.json())
        mprint.assert_called_once_with(
            {},
            "Hostname for node with id {0} has been changed to {1}.".format(
                self.node_id, new_hostname)
        )
