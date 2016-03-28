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

from fuelclient.commands import base
from fuelclient.common import data_utils


class TaskMixIn(object):
    entity_name = 'task'


class TaskList(TaskMixIn, base.BaseListCommand):
    """Show list of all available tasks."""
    columns = ('id',
               'status',
               'name',
               'cluster',
               'result',
               'progress')


class TaskShow(TaskMixIn, base.BaseShowCommand):
    """Show info about task with given id."""
    columns = ('id',
               'uuid',
               'status',
               'name',
               'cluster',
               'result',
               'progress',
               'message')


class TaskHistoryShow(TaskMixIn, base.BaseListCommand):
    """Show deployment history about task with given id"""

    entity_name = 'deployment_history'

    columns = (
        'deployment_graph_task_name',
        'node_id',
        'status',
        'time_start',
        'time_end')

    def get_parser(self, prog_name):
        parser = super(TaskHistoryShow, self).get_parser(prog_name)

        parser.add_argument('id', type=int,
                            help='Id of the Task.')
        parser.add_argument(
            '-n',
            '--nodes',
            type=str,
            nargs='+',
            help='Show deployment history for specific nodes')

        parser.add_argument(
            '-t',
            '--statuses',
            type=str,
            choices=['pending', 'error', 'ready', 'running', 'skipped'],
            nargs='+',
            help='Show deployment history for specific statuses')

        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all(
            transaction_id=parsed_args.id,
            nodes=parsed_args.nodes,
            statuses=parsed_args.statuses)

        data = data_utils.get_display_data_multi(self.columns, data)

        return (self.columns, data)
