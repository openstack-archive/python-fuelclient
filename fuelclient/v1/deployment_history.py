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

import six
import yaml

from fuelclient import objects
from fuelclient.v1 import base_v1


class DeploymentHistoryClient(base_v1.BaseV1Client):

    class_api_path = "transactions/{transaction_id}/deployment_history/"

    history_records_keys = ("task_name", "node_id", "status",
                            "time_start", "time_end")
    tasks_records_keys = ("task_name", "task_parameters", "status_by_node")

    _entity_wrapper = objects.Environment

    def get_all(self, transaction_id, nodes=None, statuses=None,
                tasks_names=None, show_parameters=False,
                include_summary=False):
        parameters = {
            'statuses': statuses,
            'nodes': nodes,
            'tasks_names': tasks_names,
            'include_summary': (str(int(include_summary)),),
        }
        # remove unused parameters or parameters with empty list as value
        parameters = {k: v for k, v in six.iteritems(parameters)
                      if v is not None and v}
        # 'parameters': ['param1', 'param2'] --> 'parameters': 'param1,param2'
        for k in parameters:
            parameters[k] = ",".join(s for s in parameters[k])

        history_with_tasks = self.connection.get_request(
            self.class_api_path.format(
                transaction_id=transaction_id,
            ), params=parameters
        )
        # rename legacy field for Fuel 9.0
        for record in history_with_tasks:
            if 'deployment_graph_task_name' in record:
                record['task_name'] = record['deployment_graph_task_name']
                record.pop('deployment_graph_task_name', None)

        # metadata for each task
        tasks_parameters = defaultdict(dict)
        # history records by task ID
        history_records_by_task = defaultdict(list)
        # history records in initial order
        history_records = []
        # split keys to history- and task-specific

        for record in history_with_tasks:
            task_name = record['task_name']
            if tasks_names and task_name not in tasks_names:
                # API gave us a task, that we actually want to filter out
                continue
            history_record = {}
            for key in record:
                if key in self.history_records_keys or key == 'summary':
                    history_record[key] = record[key]
                else:
                    tasks_parameters[task_name][key] = record[key]
            if include_summary:
                history_record['summary'] = history_record.get('summary', None)
            history_records.append(history_record)
            history_records_by_task[task_name].append(history_record)

        if show_parameters:
            result = []
            for task_name, value in sorted(six.iteritems(tasks_parameters)):
                statuses_by_node = []
                for record in history_records_by_task[task_name]:
                    time_start = record.get('time_start')
                    time_start = time_start.partition(u'.')[0] if time_start\
                        else u'not started'
                    record['time_start'] = time_start
                    time_end = record.get('time_end')
                    time_end = time_end.partition(u'.')[0] if time_end \
                        else u'not ended'
                    record['time_end'] = time_end

                    statuses_by_node.append(
                        '{node_id} - {status} - {time_start} - {time_end}'
                        ''.format(**record)
                    )

                result.append(
                    {
                        "task_name": task_name,
                        "task_parameters": yaml.safe_dump(
                            tasks_parameters[task_name]),
                        "status_by_node": '\n'.join(statuses_by_node)
                    }
                )
            return result
        else:
            return history_records


def get_client(connection):
    return DeploymentHistoryClient(connection)
