# -*- coding: utf-8 -*-
#
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


def get_fake_deployment_history():
    """Create a fake deployment history

    Returns the serialized and parametrized representation of a dumped Fuel
    Deployment History. Represents the average amount of data.

    """
    return [
        {
            "status": "ready",
            "time_start": "2016-03-25T17:22:10.687135",
            "time_end": "2016-03-25T17:22:30.830701",
            "node_id": "1",
            "deployment_graph_task_name": "controller_remaining_tasks"
        },
        {
            "status": "skipped",
            "time_start": "2016-03-25T17:23:37.313212",
            "time_end": "2016-03-25T17:23:37.313234",
            "node_id": "2",
            "deployment_graph_task_name": "ironic-compute"
        }
    ]
