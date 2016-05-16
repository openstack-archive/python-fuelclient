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
from collections import defaultdict

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli.formatting import format_table
from fuelclient.objects.deployment_history import DeploymentHistory


class DeploymentTasksAction(Action):
    """Show deployment tasks
    """
    action_name = "deployment-tasks"
    history_records_keys = ("task_name", "node_id", "status",
                            "time_start", "time_end")
    tasks_groups_keys = ("task_name", "task_parameters", "status_by_node")

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
            ),
            Args.get_tasks_names_arg(
                "Show deployment history for specific deployment tasks names "
                "and group output by task"
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

            To display certain deployment tasks results only you could use:
                fuel deployment-tasks --task-name task-name1,task-name2

        """

        tasks_names = getattr(params, 'task-name')
        tasks_data = DeploymentHistory.get_all(
            transaction_id=params.task,
            nodes=params.node,
            statuses=params.status,
            tasks_names=tasks_names
        )

        # rename legacy field for Fuel 9.0
        for record in tasks_data:
            if 'deployment_graph_task_name' in record:
                record['task_name'] = record['deployment_graph_task_name']
                record.pop('deployment_graph_task_name', None)

        tasks_data = {}                     # metadata for each task
        records_by_task = defaultdict(list) # history records by task ID
        history_records = []                # history records in initial order

        for record in tasks_data:
            history_record = {}
            task_name = record['task_name']
            for key in record:
                # split keys to history- and task-specific
                if key in self.history_records_keys:
                    history_record[key] = record[key]
                else:
                    tasks_data[task_name][key] = record[key]
            history_records.append(history_record)
            records_by_task[task_name].append(history_record)

        if tasks_names:
            pass
        else:
            self.serializer.print_to_output(
                history_records,
                format_table(
                    history_records,
                    acceptable_keys=self.history_records_keys
                )
            )