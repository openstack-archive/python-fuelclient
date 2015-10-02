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

from mock import patch
import requests_mock as rm

from fuelclient.tests.unit.v1 import base


class TestNotificationsActions(base.UnitTestCase):
    def test_notification_send(self):
        post = self.m_request.post(rm.ANY, json={})

        self.execute(
            ['fuel', 'notifications', '--send', 'test message'])
        self.assertEqual(post.call_count, 1)

        request = post.last_request.json()
        self.assertEqual('test message', request['message'])
        self.assertEqual('done', request['topic'])

        self.execute(
            ['fuel', 'notify', '-m', 'test message 2'])
        self.assertEqual(post.call_count, 2)

        request = post.last_request.json()
        self.assertEqual('test message 2', request['message'])
        self.assertEqual('done', request['topic'])

    def test_notification_send_with_topic(self):
        post = self.m_request.post(rm.ANY, json={})

        self.execute(
            ['fuel', 'notifications', '--send', 'test error',
             '--topic', 'error'])
        self.assertEqual(post.call_count, 1)
        request = post.last_request.json()
        self.assertEqual('test error', request['message'])
        self.assertEqual('error', request['topic'])

        self.execute(
            ['fuel', 'notify', '-m', 'test error 2', '--topic', 'error'])
        self.assertEqual(post.call_count, 2)
        request = post.last_request.json()
        self.assertEqual('test error 2', request['message'])
        self.assertEqual('error', request['topic'])

    def test_notification_send_no_message(self):
        post = self.m_request.post(rm.ANY, json={})

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notifications', '--send']
        )
        self.assertFalse(post.called)

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notify', '-m']
        )
        self.assertFalse(post.called)

    def test_notification_send_invalid_topic(self):
        post = self.m_request.post(rm.ANY, json={})

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notifications', '--send', 'test message',
             '--topic', 'x']
        )
        self.assertFalse(post.called)

        self.assertRaises(
            SystemExit,
            self.execute,
            ['fuel', 'notify', '-m', 'test message', '--topic', 'x']
        )
        self.assertFalse(post.called)

    def test_mark_as_read(self):
        results = [{'id': 1,
                    'message': 'test message',
                    'status': 'unread',
                    'topic': 'done'},
                   {'id': 2,
                    'message': 'test message 2',
                    'status': 'unread',
                    'topic': 'done'}]
        results.extend(results)

        get = self.m_request.get(rm.ANY, [{'json': r} for r in results])
        put = self.m_request.put(rm.ANY, json={})

        self.execute(
            ['fuel', 'notifications', '-r', '1'])

        self.assertEqual(get.call_count, 1)
        self.assertEqual(put.call_count, 1)

        messages = put.last_request.json()
        self.assertEqual(1, len(messages))

        msg = messages.pop()
        self.assertEqual('test message', msg['message'])
        self.assertEqual('read', msg['status'])
        self.assertEqual(1, msg['id'])

        self.execute(
            ['fuel', 'notifications', '-r', '1', '2'])

        self.assertEqual(get.call_count, 3)
        self.assertEqual(put.call_count, 2)

        messages = put.last_request.json()
        self.assertEqual(2, len(messages))

        msg = messages.pop()
        self.assertEqual('test message', msg['message'])
        self.assertEqual('read', msg['status'])
        self.assertEqual(1, msg['id'])

        msg = messages.pop()
        self.assertEqual('test message 2', msg['message'])
        self.assertEqual('read', msg['status'])
        self.assertEqual(2, msg['id'])

    def test_mark_all_as_read(self):
        result = [{'id': 1,
                   'message': 'test message',
                   'status': 'unread',
                   'topic': 'done'},
                  {'id': 2,
                   'message': 'test message 2',
                   'status': 'unread',
                   'topic': 'done'}]

        get = self.m_request.get(rm.ANY, json=result)
        put = self.m_request.put(rm.ANY, json={})

        self.execute(
            ['fuel', 'notifications', '-r', '*'])

        self.assertEqual(get.call_count, 1)
        self.assertEqual(put.call_count, 1)
        request = put.last_request.json()
        self.assertEqual('test message', request[0]['message'])
        self.assertEqual('read', request[0]['status'])
        self.assertEqual('test message 2', request[1]['message'])
        self.assertEqual('read', request[1]['status'])

    @patch('fuelclient.cli.actions.notifications.format_table')
    def test_list_notifications(self, mformat_table):
        test_notifications = [{'id': 1,
                               'message': 'test message',
                               'status': 'unread',
                               'topic': 'done'},
                              {'id': 2,
                               'message': 'test message 2',
                               'status': 'read',
                               'topic': 'done'}]
        get = self.m_request.get(rm.ANY, json=test_notifications)
        self.m_request.put(rm.ANY, json={})

        self.execute(['fuel', 'notifications'])

        self.assertEqual(get.call_count, 1)
        notifications = mformat_table.call_args[0][0]
        self.assertEqual(len(notifications), 1)
        self.assertDictEqual(notifications[0], test_notifications[0])

    @patch('fuelclient.cli.actions.notifications.format_table')
    def test_list_all_notifications(self, mformat_table):
        test_notifications = [
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
        get = self.m_request.get(rm.ANY, json=test_notifications)
        self.m_request.put(rm.ANY, json={})

        self.execute(['fuel', 'notifications', '-a'])

        self.assertEqual(get.call_count, 1)
        notifications = mformat_table.call_args[0][0]
        self.assertEqual(len(notifications), 2)
        self.assertListEqual(notifications, test_notifications)
