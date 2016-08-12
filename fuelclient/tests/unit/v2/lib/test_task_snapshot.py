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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api


class TestTaskSnapshotCreateFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestTaskSnapshotCreateFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/logs/package'.format(
            version=self.version)
        self.client = fuelclient.get_client('snapshot', self.version)

    def test_task_snapshot_config_download(self):
        fake_resp = {'test_key': 'test_value'}
        expected_uri = '/api/{version}/logs/package/config/default/'.format(
            version=self.version)

        matcher = self.m_request.get(expected_uri, json=fake_resp)

        conf = self.client.get_default_config()
        self.assertTrue(matcher.called)
        self.assertEqual(conf, fake_resp)

    def test_task_snapshot_create(self):
        pass

    def test_task_snapshot_create_w_config(self):
        pass


