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

from fuelclient.v1.deployment_history import DeploymentHistoryClient


class DeploymentTasksAction(Action):
    """Show deployment tasks
    """
    action_name = "deployment-tasks"

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
            ),
            Args.get_show_parameters_arg(
                "Show deployment tasks parameters"
            ),
            Args.get_include_summary_arg(
                "Show deployment tasks summary"
            ),
        ]
        self.flag_func_map = (
            (None, self.list),
        )

    def list(self, params):
        """To display all deployment tasks for task:
                fuel deployment-tasks --task-id 5

            To display deployment tasks for some nodes:
                fuel deployment-tasks --task-id 5 --node 1,2

            To display deployment tasks for some statuses(pending, error,
            ready, running):
                fuel deployment-tasks --task-id 5 --status pending,running

            To display deployment tasks for some statuses(pending, error,
            ready, running) on some nodes:
                fuel deployment-tasks --task-id 5 --status error --node 1,2

            To display certain deployment tasks results only:
                fuel deployment-tasks --task-id 5
                    --task-name task-name1,task-name2

            To display tasks parameters use:
                fuel deployment-tasks --task-id 5 --show-parameters

        """
        client = DeploymentHistoryClient()
        tasks_names = getattr(params, 'task-name', None)
        show_parameters = getattr(params, 'show-parameters')
        statuses = params.status.split(',') if params.status else []
        nodes = params.node.split(',') if params.node else []
        tasks_names = tasks_names.split(',') if tasks_names else []
        include_summary = getattr(params, 'include-summary')

        data = client.get_all(
            transaction_id=params.task,
            nodes=nodes,
            statuses=statuses,
            tasks_names=tasks_names,
            show_parameters=show_parameters,
            include_summary=include_summary
        )

        if show_parameters:
            table_keys = client.tasks_records_keys
        else:
            table_keys = client.history_records_keys
        if include_summary:
            table_keys += ('summary',)
        self.serializer.print_to_output(
            data,
            format_table(
                data,
                acceptable_keys=table_keys
            )
        )
