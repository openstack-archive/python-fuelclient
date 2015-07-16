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
import re

import requests_mock as rm

import fuelclient
from fuelclient.tests import utils
from fuelclient.tests.v2.unit.lib import test_api


class TestTaskFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestTaskFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/tasks/'.format(version=self.version)
        single_regexp = re.compile('{0}\d+/?$'.format(self.res_uri))

        fake_tasks = [utils.get_fake_task() for i in range(5)]
        self.multiple_matcher = self.m_request.get(self.res_uri,
                                                   text=json.dumps(fake_tasks))

        fake_task = utils.get_fake_task()
        self.single_matcher = self.m_request.get(single_regexp,
                                                 text=json.dumps(fake_task))

        self.client = fuelclient.get_client('task', self.version)

    def test_task_list(self):
        self.client.get_all()

        self.assertEqual(rm.GET, self.multiple_matcher.last_request.method)
        self.assertEqual(self.res_uri, self.multiple_matcher.last_request.path)

    def test_task_show(self):
        task_id = 42
        expected_uri = self.get_object_uri(self.res_uri, task_id)

        self.client.get_by_id(task_id)

        self.assertEqual(rm.GET, self.single_matcher.last_request.method)
        self.assertEqual(expected_uri, self.single_matcher.last_request.path)
