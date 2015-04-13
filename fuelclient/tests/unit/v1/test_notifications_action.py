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

from mock import Mock
from mock import patch

from fuelclient.tests import base


@patch('fuelclient.client.requests')
class TestNotificationsActions(base.UnitTestCase):
    def test_notification_send(self, mrequests):
        response_mock = Mock(status_code=201)
        mrequests.post.return_value = response_mock

        self.execute(
            ['fuel', 'notifications', '--send', 'test message'])
        self.assertEqual(mrequests.post.call_count, 1)
        request = json.loads(mrequests.post.call_args[1]['data'])
        self.assertEqual('test message', request['message'])
        self.assertEqual('done', request['topic'])

        self.execute(
            ['fuel', 'notify', '-m', 'test message 2'])
        self.assertEqual(mrequests.post.call_count, 2)
        request = json.loads(mrequests.post.call_args[1]['data'])
        self.assertEqual('test message 2', request['message'])
        self.assertEqual('done', request['topic'])

    def test_notification_send_with_topic(self, mrequests):
        response_mock = Mock(status_code=201)
        mrequests.post.return_value = response_mock

        self.execute(
            ['fuel', 'notifications', '--send', 'test error',
             '--topic', 'error'])
        self.assertEqual(mrequests.post.call_count, 1)
        request = json.loads(mrequests.post.call_args[1]['data'])
        self.assertEqual('test error', request['message'])
        self.assertEqual('error', request['topic'])

        self.execute(
            ['fuel', 'notify', '-m', 'test error 2', '--topic', 'error'])
        self.assertEqual(mrequests.post.call_count, 2)
        request = json.loads(mrequests.post.call_args[1]['data'])
        self.assertEqual('test error 2', request['message'])
        self.assertEqual('error', request['topic'])

    def test_notification_send_no_message(self, mrequests):
        response_mock = Mock(status_code=201)
        mrequests.post.return_value = response_mock

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notifications', '--send']
        )
        self.assertEqual(mrequests.post.call_count, 0)

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notify', '-m']
        )
        self.assertEqual(mrequests.post.call_count, 0)

    def test_notification_send_invalid_topic(self, mrequests):
        response_mock = Mock(status_code=201)
        mrequests.post.return_value = response_mock

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notifications', '--send', 'test message',
             '--topic', 'x']
        )
        self.assertEqual(mrequests.post.call_count, 0)

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notify', '-m', 'test message', '--topic', 'x']
        )
        self.assertEqual(mrequests.post.call_count, 0)

    def test_mark_as_read(self, mrequests):
        m1 = Mock(status=200)
        m1.json.return_value = {
            'id': 1,
            'message': 'test message',
            'status': 'unread',
            'topic': 'done',
        }
        m2 = Mock(status=200)
        m2.json.return_value = {
            'id': 2,
            'message': 'test message 2',
            'status': 'unread',
            'topic': 'done',
        }
        mrequests.get.side_effect = [m1, m2]

        mrequests.put.return_value = Mock(status_code=200)
        self.execute(
            ['fuel', 'notifications', '-r', '1'])

        self.assertEqual(mrequests.get.call_count, 1)
        self.assertEqual(mrequests.put.call_count, 1)
        request = m1.json.return_value
        self.assertEqual('test message', request['message'])
        self.assertEqual('read', request['status'])
        request = m2.json.return_value
        self.assertEqual('test message 2', request['message'])
        self.assertEqual('unread', request['status'])

        mrequests.get.side_effect = [m1, m2]

        self.execute(
            ['fuel', 'notifications', '-r', '1', '2'])

        self.assertEqual(mrequests.get.call_count, 3)
        self.assertEqual(mrequests.put.call_count, 2)
        request = m1.json.return_value
        self.assertEqual('test message', request['message'])
        self.assertEqual('read', request['status'])
        request = m2.json.return_value
        self.assertEqual('test message 2', request['message'])
        self.assertEqual('read', request['status'])

    def test_mark_all_as_read(self, mrequests):
        m = Mock(status=200)
        m.json.return_value = [
            {
                'id': 1,
                'message': 'test message',
                'status': 'unread',
                'topic': 'done',
            },
            {
                'id': 2,
                'message': 'test message 2',
                'status': 'unread',
                'topic': 'done',
            }
        ]
        mrequests.get.return_value = m

        mrequests.put.return_value = Mock(status_code=200)
        self.execute(
            ['fuel', 'notifications', '-r', '*'])

        self.assertEqual(mrequests.get.call_count, 1)
        self.assertEqual(mrequests.put.call_count, 1)
        request = m.json.return_value
        self.assertEqual('test message', request[0]['message'])
        self.assertEqual('read', request[0]['status'])
        self.assertEqual('test message 2', request[1]['message'])
        self.assertEqual('read', request[1]['status'])

    @patch('fuelclient.cli.actions.notifications.format_table')
    def test_list_notifications(self, mformat_table, mrequests):
        m = Mock(status=200)
        m.json.return_value = [
            {
                'id': 1,
                'message': 'test message',
                'status': 'unread',
                'topic': 'done',
            },
            {
                'id': 2,
                'message': 'test message 2',
                'status': 'read',
                'topic': 'done',
            }
        ]
        mrequests.get.return_value = m

        mrequests.put.return_value = Mock(status_code=200)
        self.execute(['fuel', 'notifications'])

        self.assertEqual(mrequests.get.call_count, 1)
        notifications = mformat_table.call_args[0][0]
        self.assertEqual(len(notifications), 1)
        self.assertDictEqual(notifications[0], m.json.return_value[0])

    @patch('fuelclient.cli.actions.notifications.format_table')
    def test_list_all_notifications(self, mformat_table, mrequests):
        m = Mock(status=200)
        m.json.return_value = [
            {
                'id': 1,
                'message': 'test message',
                'status': 'unread',
                'topic': 'done',
            },
            {
                'id': 2,
                'message': 'test message 2',
                'status': 'read',
                'topic': 'done',
            }
        ]
        mrequests.get.return_value = m

        mrequests.put.return_value = Mock(status_code=200)
        self.execute(['fuel', 'notifications', '-a'])

        self.assertEqual(mrequests.get.call_count, 1)
        notifications = mformat_table.call_args[0][0]
        self.assertEqual(len(notifications), 2)
        self.assertListEqual(notifications, m.json.return_value)
