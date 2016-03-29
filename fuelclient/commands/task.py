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

import os

from fuelclient.cli.serializers import Serializer
from fuelclient.commands import base
from fuelclient.common import data_utils


class TaskMixIn(object):
    entity_name = 'task'

    @staticmethod
    def add_file_arg(parser):
        parser.add_argument(
            '-f',
            '--file',
            required=False,
            type=str,
            help='YAML file that contains network configuration.'
        )

    @classmethod
    def write_info_to_file(self, info_type, data, transaction_id,
                           serializer=None, file_path=None):
        """Write additional info to the given path.

        :param info_type: deployment_info | cluster_settings |
                          network_configuration
        :type info_type: str
        :param data: data
        :type data: list of dict
        :param serializer: serializer
        :param transaction_id: Transaction ID
        :type transaction_id: str or int
        :param file_path: path
        :type file_path: str
        :return: path to resulting file
        :rtype: str
        """
        return (serializer or Serializer()).write_to_path(
            (file_path or self.get_default_info_path(info_type,
                                                     transaction_id)),
            data)

    @staticmethod
    def get_default_info_path(info_type, transaction_id):
        """Generate default path for task additional info e.g. deployment info

        :param info_type: deployment_info | cluster_settings |
                          network_configuration
        :type info_type: str
        :param transaction_id: Transaction ID
        :type transaction_id: str or int
        :return: path
        :rtype: str
        """
        return os.path.join(
            os.path.abspath(os.curdir),
            "{info_type}_{transaction_id}".format(
                info_type=info_type,
                transaction_id=transaction_id)
        )

    @classmethod
    def download_info_to_file(self, transaction_id, info_type, file_path):
        """Get and save to path for task additional info e.g. deployment info

        :param transaction_id: Transaction ID
        :type transaction_id: str or int
        :param info_type: deployment_info | cluster_settings |
                          network_configuration
        :type info_type: str
        :param file_path: path
        :type file_path: str
        :return: path
        :rtype: str
        """
        data = self.client.download(transaction_id)
        data_file_path = self.write_info_to_file(
            info_type,
            data,
            transaction_id,
            file_path)
        return data_file_path


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


class TaskNetworkConfigurationDownload(TaskMixIn, base.BaseCommand):

    entity_name = 'network-configuration'

    def get_parser(self, prog_name):
        parser = super(TaskNetworkConfigurationDownload, self).get_parser(
            prog_name)
        parser.add_argument('id', type=int, help='Id of the Task.')
        self.add_file_arg(parser)
        return parser

    def take_action(self, parsed_args):
        networks_data_file_path = self.download_info_to_file(
            transaction_id=parsed_args.id,
            info_type='network_configuration',
            file_path=parsed_args.file)

        self.app.stdout.write(
            "Network configuration for task with id={0}"
            " downloaded to {1}\n".format(parsed_args.id,
                                          networks_data_file_path)
        )


class TaskDeploymentInfoDownload(TaskMixIn, base.BaseCommand):

    entity_name = 'deployment-info'

    def get_parser(self, prog_name):
        parser = super(TaskDeploymentInfoDownload, self).get_parser(
            prog_name)
        parser.add_argument('id', type=int, help='Id of the Task.')
        self.add_file_arg(parser)
        return parser

    def take_action(self, parsed_args):
        deployment_data_file_path = self.download_info_to_file(
            transaction_id=parsed_args.id,
            info_type='deployment_info',
            file_path=parsed_args.file)

        self.app.stdout.write(
            "Deployment info for task with id={0}"
            " downloaded to {1}\n".format(parsed_args.id,
                                          deployment_data_file_path)
        )


class TaskClusterSettingsDownload(TaskMixIn, base.BaseCommand):

    entity_name = 'cluster-settings'

    def get_parser(self, prog_name):
        parser = super(TaskClusterSettingsDownload, self).get_parser(
            prog_name)
        parser.add_argument('id', type=int, help='Id of the Task.')
        self.add_file_arg(parser)
        return parser

    def take_action(self, parsed_args):
        cluster_data_file_path = self.download_info_to_file(
            transaction_id=parsed_args.id,
            info_type='cluster_settings',
            file_path=parsed_args.file)

        self.app.stdout.write(
            "Cluster settings for task with id={0}"
            " downloaded to {1}\n".format(parsed_args.id,
                                          cluster_data_file_path)
        )
