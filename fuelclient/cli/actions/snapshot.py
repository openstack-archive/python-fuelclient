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

import sys

import six
import yaml

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.objects.task import SnapshotTask


class SnapshotAction(Action):
    """Generate and download snapshot.
    """
    action_name = "snapshot"

    def __init__(self):
        super(SnapshotAction, self).__init__()
        self.args = (
            Args.get_boolean_arg("conf",
                                 help_="Provide this flag to generate conf"),
        )
        self.flag_func_map = (
            ('conf', self.get_snapshot_config),
            (None, self.create_snapshot),
        )

    def create_snapshot(self, params):
        """To create diagnostic snapshot:
                fuel snapshot

            To specify config for snapshotting:
                fuel snapshot < conf.yaml

        """
        if sys.stdin.isatty():
            conf = {}
        else:
            conf = yaml.load(sys.stdin.read())

        snapshot_task = SnapshotTask.start_snapshot_task(conf)
        self.serializer.print_to_output(
            snapshot_task.data,
            "Generating diagnostic snapshot..."
        )
        snapshot_task.wait()

        if snapshot_task.status == 'ready':
            self.serializer.print_to_output(
                snapshot_task.data,
                "...Completed...\n"
                "Diagnostic snapshot can be downloaded from " +
                snapshot_task.connection.root +
                snapshot_task.data["message"]
            )
        elif snapshot_task.status == 'error':
            six.print_(
                "Snapshot generating task ended with error. Task message: {0}"
                .format(snapshot_task.data["message"]),
                file=sys.stderr
            )

    def get_snapshot_config(self, params):
        """Download default config for snapshot:
                fuel snapshot --conf > dump_conf.yaml

            To use json formatter:
                fuel snapshot --conf --json
        """
        conf = SnapshotTask.get_default_config()
        self.serializer.write_to_file(sys.stdout, conf)
