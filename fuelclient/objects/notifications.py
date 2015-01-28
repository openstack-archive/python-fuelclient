#    Copyright 2014 Mirantis, Inc.
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

from fuelclient.objects import base


class Notifications(base.BaseObject):

    class_api_path = "notifications/"
    class_instance_path = "notifications/{id}"

    @classmethod
    def send(cls, message, topic=None):
        if topic is None:
            topic = "done"

        resp = cls.connection.post_request_raw(
            cls.class_api_path, {
                'message': message,
                'topic': topic,
            })

        resp.raise_for_status()

        return resp
