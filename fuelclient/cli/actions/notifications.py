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

from fuelclient.cli import error

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.cli.formatting import format_table
from fuelclient.objects.notifications import Notifications


class NotificationsAction(Action):
    """List and create notifications
    """
    action_name = "notifications"

    acceptable_keys = (
        "message",
        "status",
        "topic",
    )

    def __init__(self):
        super(NotificationsAction, self).__init__()
        self.args = [
            Args.get_list_arg("List all available notifications."),
            Args.get_notify_send_arg("Send notification"),
            Args.get_notify_topic_arg("Notification topic (severity)"),
        ]
        self.flag_func_map = (
            ("send", self.send),
            (None, self.list),
        )

    def list(self, params):
        """Print all available notifications:
                fuel notifications
                fuel notifications --list
        """
        notifications = Notifications.get_all_data()
        self.serializer.print_to_output(
            notifications,
            format_table(
                notifications,
                acceptable_keys=self.acceptable_keys
            )
        )

    def send(self, params):
        """Send notification:
            fuel notifications --send "message" --topic done
        """
        result = Notifications.send(params.send, topic=params.topic)
        self.serializer.print_to_output(
            result,
            "Notification sent")
