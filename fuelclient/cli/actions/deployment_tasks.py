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

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli.formatting import format_table
from fuelclient.objects.deployment_history import DeploymentHistory


class DeploymentTasksAction(Action):
    """Show deployment tasks
    """
    action_name = "deployment-tasks"
    acceptable_keys = ("deployment_graph_task_name", "node_id", "status",
                       "time_start", "time_end")

    def __init__(self):
        super(DeploymentTasksAction, self).__init__()
        self.args = [
            group(
                Args.get_list_arg("List all deployment tasks"),
            ),
            Args.get_single_task_arg(required=True),
            Args.get_deployment_node_arg(
                "Node ids."
            ),
            Args.get_status_arg(
                "Statuses: pending, error, ready, running, skipped"
            )
        ]
        self.flag_func_map = (
            (None, self.list),
        )

    def list(self, params):
        """To display all deployment tasks for task:
                fuel deployment-tasks --task-id 5

            To display deployment tasks for some nodes:
                fuel deployment-tasks --task-id 5 --nodes 1,2

            To display deployment tasks for some statuses(pending, error,
            ready, running):
                fuel deployment-tasks --task-id 5 --status pending,running

            To display deployment tasks for some statuses(pending, error,
            ready, running) on some nodes:
                fuel deployment-tasks --task-id 5 --status error --nodes 1,2
        """

        tasks_data = DeploymentHistory.get_all(
            params.task,
            params.node,
            params.status
        )
        self.serializer.print_to_output(
            tasks_data,
            format_table(tasks_data, acceptable_keys=self.acceptable_keys)
        )
