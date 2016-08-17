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

import six

from fuelclient import objects
from fuelclient.v1 import base_v1


class TaskClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Task

    def get_all(self, env_id=None, statuses=None, types=None):
        """Get tasks by specific environment, statuses or types

        :param env_id: Id of specific environment (cluster)
        :type env_id: str
        :param statuses: List of string task statuses for filtering
        :type statuses: list
        :param types: List of string task types for filtering
        :type types: list
        :returns: list -- filtered list of tasks
        """
        filters = {
            'cluster_id': env_id,
            'statuses': statuses,
            'transaction_types': types
        }
        # remove unused filters
        filters = dict((k, v) for k, v in six.iteritems(filters)
                       if v is not None)
        # 'filter': ['param1', 'param2'] --> 'filter': 'param1,param2'
        for k in filters:
            filters[k] = ",".join(s for s in filters[k])
        result = self._entity_wrapper.get_filtered_data(**filters)

        return result

    def delete_by_id(self, task_id, force=False):
        """Delete a given task by its id

        :param task_id: Id of a task to delete.
        :type task_id: int
        :param force: Force deletion of a task without
                      considering its state

        """
        task_obj = self._entity_wrapper(obj_id=task_id)
        task_obj.delete(force=force)


def get_client(connection):
    return TaskClient(connection)
