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

from fuelclient.cli import error

from fuelclient.objects import base


class Notifications(base.BaseObject):

    class_api_path = "notifications/"
    instance_api_path = "notifications/{0}"

    default_topic = 'done'

    @classmethod
    def mark_as_read(cls, ids=None):
        if not ids:
            raise error.BadDataException('Message id not specified.')

        if '*' in ids:
            data = Notifications.get_all_data()
        else:
            try:
                ids = map(int, ids)
            except ValueError:
                raise error.BadDataException(
                    "Numerical ids expected or the '*' symbol.")
            notifications = Notifications.get_by_ids(ids)

            data = [notification.get_fresh_data()
                    for notification in notifications]

        for notification in data:
            notification['status'] = 'read'

        resp = cls.connection.put_request(
            cls.class_api_path, data)

        return resp

    @classmethod
    def send(cls, message, topic=default_topic):
        if not topic:
            topic = cls.default_topic

        if not message:
            raise error.BadDataException('Message not specified.')

        resp = cls.connection.post_request(
            cls.class_api_path, {
                'message': message,
                'topic': topic,
            })

        return resp
