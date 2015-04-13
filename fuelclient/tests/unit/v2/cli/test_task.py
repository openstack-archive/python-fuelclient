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

import mock

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_task


class TestTaskCommand(test_engine.BaseCLITest):

    def setUp(self):
        super(TestTaskCommand, self).setUp()

        self.m_client.get_all.return_value = [fake_task.get_fake_task()
                                              for i in range(10)]
        self.m_client.get_by_id.return_value = fake_task.get_fake_task()

    def test_task_list(self):
        args = 'task list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_task_show(self):
        task_id = 42
        args = 'task show {task_id}'.format(task_id=task_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('task', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(task_id)
