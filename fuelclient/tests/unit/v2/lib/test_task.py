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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestTaskFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestTaskFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/transactions/'\
                       .format(version=self.version)

        self.fake_task = utils.get_fake_task()
        self.fake_tasks = [utils.get_fake_task() for _ in range(10)]

        self.client = fuelclient.get_client('task', self.version)

    def test_task_list(self):

        matcher = self.m_request.get(self.res_uri, json=self.fake_tasks)

        self.client.get_all()

        self.assertTrue(self.res_uri, matcher.called)

    def test_task_list_w_parameters(self):
        env_id = 36
        statuses = ['ready', 'error']
        names = ['dump', 'provision']
        fake_tasks = [
            utils.get_fake_task(task_id=45, cluster=env_id,
                                status=statuses[0], name=names[0]),
            utils.get_fake_task(task_id=46, cluster=env_id,
                                status=statuses[0], name=names[1]),
            utils.get_fake_task(task_id=49, cluster=env_id,
                                status=[1], name=names[1]),
        ]
        params = ('?cluster_id={env_id}'
                  '&statuses={statuses}'
                  '&transaction_types={names}')
        expected_url = self.res_uri + params.format(
            env_id=env_id,
            statuses=','.join(statuses),
            names=','.join(names))

        matcher = self.m_request.get(expected_url, json=fake_tasks)

        tasks = self.client.get_all(cluster_id=env_id,
                                    statuses=statuses,
                                    transaction_types=names)

        self.assertTrue(matcher.called)
        self.assertEqual(3, len(tasks))

    def test_task_show(self):
        task_id = 42
        expected_uri = self.get_object_uri(self.res_uri, task_id)

        matcher = self.m_request.get(expected_uri, json=self.fake_task)

        self.client.get_by_id(task_id)

        self.assertTrue(matcher.called)

    def test_task_delete(self):
        task_id = 42
        expected_uri = self.get_object_uri(self.res_uri, task_id)
        matcher = self.m_request.delete(expected_uri, json=self.fake_task)

        self.client.delete_by_id(task_id, force=False)

        self.assertTrue(matcher.called)
        self.assertEqual(['0'], matcher.last_request.qs.get('force'))

    def test_task_delete_force(self):
        task_id = 42
        expected_uri = self.get_object_uri(self.res_uri, task_id)
        matcher = self.m_request.delete(expected_uri, json=self.fake_task)

        self.client.delete_by_id(task_id, force=True)

        self.assertTrue(matcher.called)
        self.assertEqual(['1'], matcher.last_request.qs.get('force'))
