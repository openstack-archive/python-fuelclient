# -*- coding: utf-8 -*-
#
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

import json
import requests_mock as rm

import fuelclient
from fuelclient.tests.v2.unit.lib import test_api


class TestNodeFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestNodeFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/nodes/'.format(version=self.version)

        self.client = fuelclient.get_client('node', self.version)

    def test_node_list(self):
        self.client.get_all()

        self.assertEqual(rm.GET, self.session_adapter.last_request.method)
        self.assertEqual(self.res_uri, self.session_adapter.last_request.path)

    def test_node_show(self):
        node_id = 42
        expected_uri = self.get_object_uri(self.res_uri, node_id)

        self.client.get_by_id(node_id)

        self.assertEqual(rm.GET, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

    def test_node_vms_list(self):
        node_id = 42
        expected_uri = "/api/v1/nodes/vm/{0}".format(node_id)

        self.client.get_node_vms_list(node_id)

        self.assertEqual(rm.GET, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)

    def test_node_vms_create(self):
        config = [{'opt1': 'val1', 'opt2': 'val2'},
                  {'opt3': 'val3', 'opt4': 'val4'}]
        node_id = 42

        expected_uri = "/api/v1/nodes/vm/{0}".format(node_id)
        expected_body = json.dumps({'params': config})

        self.client.node_vms_create(node_id, config)

        self.assertEqual(rm.POST, self.session_adapter.last_request.method)
        self.assertEqual(expected_uri, self.session_adapter.last_request.path)
        self.assertEqual(expected_body, self.session_adapter.last_request.body)
