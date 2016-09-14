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
            help='Output file in YAML format.'
        )

    @classmethod
    def write_info_to_file(cls, info_type, data, transaction_id,
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
        serializer = serializer or Serializer()
        if file_path:
            return serializer.write_to_full_path(
                file_path,
                data
            )
        else:
            return serializer.write_to_path(
                cls.get_default_info_path(info_type, transaction_id),
                data
            )

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
        data = self.client.download(transaction_id=transaction_id)
        return self.write_info_to_file(
            info_type=info_type,
            data=data,
            transaction_id=transaction_id,
            serializer=Serializer(),
            file_path=file_path)


class TaskInfoFileMixIn(TaskMixIn):

    def get_parser(self, prog_name):
        parser = super(TaskInfoFileMixIn, self).get_parser(
            prog_name)
        parser.add_argument('id', type=int, help='Id of the Task.')
        self.add_file_arg(parser)
        return parser

    def download_info(self, parsed_args):
        data_file_path = self.download_info_to_file(
            transaction_id=parsed_args.id,
            info_type=self.info_type,
            file_path=parsed_args.file)

        return data_file_path


class TaskList(TaskMixIn, base.BaseListCommand):
    """Show list of all available tasks."""
    columns = ('id',
               'status',
               'name',
               'graph_type',
               'cluster',
               'result',
               'dry_run',
               'progress')
    filters = {'cluster_id': 'env',
               'statuses': 'statuses',
               'transaction_types': 'names'}

    def get_parser(self, prog_name):
        parser = super(TaskList, self).get_parser(prog_name)

        parser.add_argument(
            '-e',
            '--env',
            type=int,
            help='Show list of tasks that belong to specified environment')

        parser.add_argument(
            '-t',
            '--statuses',
            type=str,
            choices=['pending', 'error', 'ready', 'running'],
            nargs='+',
            help='Show list of tasks with specified statuses')

        parser.add_argument(
            '-n',
            '--names',
            type=str,
            nargs='+',
            help='Show list of tasks with specified names')

        return parser


class TaskShow(TaskMixIn, base.BaseShowCommand):
    """Show info about task with given id."""
    columns = ('id',
               'uuid',
               'status',
               'name',
               'graph_type',
               'cluster',
               'result',
               'dry_run',
               'progress',
               'message')


class TaskDelete(TaskMixIn, base.BaseDeleteCommand):
    """Delete task with given id."""

    def get_parser(self, prog_name):
        parser = super(TaskDelete, self).get_parser(prog_name)

        parser.add_argument('-f',
                            '--force',
                            action='store_true',
                            default=False,
                            help='Force deletion of a task without '
                                 'considering its state.')

        return parser

    def take_action(self, parsed_args):
        self.client.delete_by_id(parsed_args.id, parsed_args.force)

        msg = 'Task with id {ent_id} was deleted\n'
        self.app.stdout.write(msg.format(ent_id=parsed_args.id))


class TaskHistoryShow(TaskMixIn, base.BaseListCommand):
    """Show deployment history about task with given ID."""

    entity_name = 'deployment_history'

    columns = ()

    def get_parser(self, prog_name):
        parser = super(TaskHistoryShow, self).get_parser(prog_name)

        parser.add_argument('id', type=int, help='Id of the Task')

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

        parser.add_argument(
            '-d',
            '--tasks-names',
            type=str,
            nargs='+',
            help='Show deployment history for specific deployment tasks names')

        parser.add_argument(
            '-p',
            '--show-parameters',
            action='store_true',
            default=False,
            help='Show deployment tasks parameters')
        parser.add_argument(
            '--include-summary',
            action='store_true',
            default=False,
            help='Show deployment tasks summary')
        return parser

    def take_action(self, parsed_args):
        # print parser
        show_parameters = parsed_args.show_parameters
        include_summary = parsed_args.include_summary
        data = self.client.get_all(
            transaction_id=parsed_args.id,
            nodes=parsed_args.nodes,
            statuses=parsed_args.statuses,
            tasks_names=parsed_args.tasks_names,
            include_summary=include_summary,
            show_parameters=show_parameters
        )
        if show_parameters:
            self.columns = self.client.tasks_records_keys
        else:
            self.columns = self.client.history_records_keys
        if include_summary:
            self.columns += ('summary',)
        data = data_utils.get_display_data_multi(self.columns, data)
        return self.columns, data


class TaskNetworkConfigurationDownload(TaskInfoFileMixIn, base.BaseCommand):
    """Save task network configuration to a file."""

    entity_name = 'network-configuration'
    info_type = 'network_configuration'

    def take_action(self, parsed_args):
        self.app.stdout.write(
            "Network configuration for task with id={0}"
            " downloaded to {1}\n".format(parsed_args.id,
                                          self.download_info(parsed_args))
        )


class TaskDeploymentInfoDownload(TaskInfoFileMixIn, base.BaseCommand):
    """Save task deployment info to a file."""

    entity_name = 'deployment-info'
    info_type = 'deployment_info'

    def take_action(self, parsed_args):
        self.app.stdout.write(
            "Deployment info for task with id={0}"
            " downloaded to {1}\n".format(parsed_args.id,
                                          self.download_info(parsed_args))
        )


class TaskClusterSettingsDownload(TaskInfoFileMixIn, base.BaseCommand):
    """Save task settings to a file."""

    entity_name = 'cluster-settings'
    info_type = 'cluster_settings'

    def take_action(self, parsed_args):
        self.app.stdout.write(
            "Cluster settings for task with id={0}"
            " downloaded to {1}\n".format(parsed_args.id,
                                          self.download_info(parsed_args))
        )
