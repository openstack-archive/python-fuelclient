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

import os

from fuelclient.cli import error
from fuelclient.cli.serializers import Serializer
from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient.utils import iterfiles


class FileMethodsMixin(object):
    @classmethod
    def check_file_path(cls, file_path):
        if not os.path.exists(file_path):
            raise error.InvalidFileException(
                "File '{0}' doesn't exist.".format(file_path))

    @classmethod
    def check_dir(cls, directory):
        if not os.path.exists(directory):
            raise error.InvalidDirectoryException(
                "Directory '{0}' doesn't exist.".format(directory))
        if not os.path.isdir(directory):
            raise error.InvalidDirectoryException(
                "Error: '{0}' is not a directory.".format(directory))


class GraphUpload(base.BaseCommand, FileMethodsMixin):
    """Upload deployment graph configuration."""
    entity_name = 'graph'

    @classmethod
    def read_data_from_file(cls, file_path=None, serializer=None):
        """Read graph data from given path.

        :param file_path: path
        :type file_path: str
        :param serializer: serializer object
        :type serializer: object
        :return: data
        :rtype: list|object
        """
        cls.check_file_path(file_path)
        return (serializer or Serializer()).read_from_full_path(file_path)

    @classmethod
    def read_data_from_dir(cls, dir_path=None, serializer=None):
        """Read graph data from directory.

        :param dir_path: path
        :type dir_path: str
        :param serializer: serializer object
        :type serializer: object
        :return: data
        :rtype: list|object
        """
        cls.check_dir(dir_path)
        serializer = serializer or Serializer()

        metadata_filepath = os.path.join(dir_path, 'metadata.yaml')
        if os.path.exists(metadata_filepath):
            data = serializer.read_from_full_path(metadata_filepath)
        else:
            data = {}

        tasks = []
        for file_name in iterfiles(dir_path, 'tasks.yaml'):
            task_data = serializer.read_from_full_path(file_name)
            if task_data:
                tasks.extend(task_data)

        if tasks:
            data['tasks'] = tasks

        if not data:
            msg = ("Nothing to upload. Check if at least one 'tasks.yaml' "
                   "file is not empty and exists in '{path}' directory "
                   "path".format(path=dir_path))
            raise error.ActionException(msg)
        return data

    def get_parser(self, prog_name):
        parser = super(GraphUpload, self).get_parser(prog_name)
        graph_class = parser.add_mutually_exclusive_group(required=True)

        graph_class.add_argument('-e',
                                 '--env',
                                 type=int,
                                 required=False,
                                 help='Id of the environment')
        graph_class.add_argument('-r',
                                 '--release',
                                 type=int,
                                 required=False,
                                 help='Id of the release')
        graph_class.add_argument('-p',
                                 '--plugin',
                                 type=int,
                                 required=False,
                                 help='Id of the plugin')

        parser.add_argument('-t',
                            '--graph-type',
                            required=True,
                            help='Type of the deployment graph')

        graph_source = parser.add_mutually_exclusive_group(required=True)
        graph_source.add_argument(
            '-f',
            '--file',
            default=None,
            help='YAML file that contains deployment graph data.'
        )
        graph_source.add_argument(
            '-d',
            '--dir',
            default=None,
            help='The directory that includes tasks.yaml and metadata.yaml.'
        )
        return parser

    def take_action(self, args):
        parameters_to_graph_class = (
            ('env', 'clusters'),
            ('release', 'releases'),
            ('plugin', 'plugins'),
        )

        if args.file:
            data = self.read_data_from_file(args.file)
        else:
            data = self.read_data_from_dir(args.dir)

        for parameter, graph_class in parameters_to_graph_class:
            model_id = getattr(args, parameter)
            if model_id:
                self.client.upload(
                    data=data,
                    related_model=graph_class,
                    related_id=model_id,
                    graph_type=args.graph_type
                )
                break

        self.app.stdout.write("Deployment graph was successfully uploaded.\n")


class GraphExecute(base.BaseTasksExecuteCommand):
    """Start deployment with given graph type."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphExecute, self).get_parser(prog_name)
        parser.add_argument(
            '-t',
            '--graph-types',
            nargs='+',
            required=True,
            help='Types of the deployment graph in order of execution'
        )
        parser.add_argument(
            '-n',
            '--nodes',
            type=int,
            nargs='+',
            help='Ids of the nodes to use for deployment.'
        )
        parser.add_argument(
            '-T',
            '--task-names',
            nargs='+',
            help='List of deployment tasks to run.'
        )
        parser.add_argument('-S',
                            '--subgraphs',
                            type=str,
                            nargs='+',
                            required=False,
                            help='List of subgraphs to execute'
                                 'Format is: '
                                 '[<start_task>[/<node_ids>]]\
                                 [:<end_task>/[<node_ids>]]')
        return parser

    def get_options(self, parsed_args):
        return {
            'graph_types': parsed_args.graph_types,
            'nodes': parsed_args.nodes,
            'task_names': parsed_args.task_names,
            'subgraphs': parsed_args.subgraphs
        }


class GraphDownload(base.BaseCommand):
    """Download deployment graph configuration."""
    entity_name = 'graph'
    supported_file_formats = ('json', 'yaml')

    def get_parser(self, prog_name):
        parser = super(GraphDownload, self).get_parser(prog_name)
        tasks_level = parser.add_mutually_exclusive_group(required=True)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')

        tasks_level.add_argument('-a',
                                 '--all',
                                 action="store_true",
                                 required=False,
                                 default=False,
                                 help='Download merged graph for the '
                                      'environment')
        tasks_level.add_argument('-c',
                                 '--cluster',
                                 action="store_true",
                                 required=False,
                                 default=False,
                                 help='Download cluster-specific tasks')
        tasks_level.add_argument('-p',
                                 '--plugins',
                                 action="store_true",
                                 required=False,
                                 default=False,
                                 help='Download plugins-specific tasks')
        tasks_level.add_argument('-r',
                                 '--release',
                                 action="store_true",
                                 required=False,
                                 default=False,
                                 help='Download release-specific tasks')

        parser.add_argument('-t',
                            '--graph-type',
                            type=str,
                            default=None,
                            required=False,
                            help='Graph type string')
        parser.add_argument('-f',
                            '--file',
                            type=str,
                            required=False,
                            default=None,
                            help='File in {} format that contains tasks '
                                 'data.'.format(self.supported_file_formats))
        parser.add_argument('--format',
                            required=False,
                            choices=self.supported_file_formats,
                            default='yaml',
                            help='Format of serialized tasks data. '
                                 'Defaults to YAML.')
        return parser

    @classmethod
    def get_default_tasks_data_path(cls, env_id, task_level_name, file_format):
        return os.path.join(
            os.path.abspath(os.curdir),
            '{}_graph_{}.{}'.format(task_level_name, env_id, file_format)
        )

    @classmethod
    def write_tasks_to_file(cls, tasks_data, serializer, file_path):
        return serializer.write_to_full_path(file_path, tasks_data)

    def take_action(self, args):
        tasks_data = []
        tasks_level_name = ''
        for tasks_level_name in ('all', 'cluster', 'release', 'plugins'):
            if getattr(args, tasks_level_name):
                tasks_data = self.client.download(
                    env_id=args.env,
                    level=tasks_level_name,
                    graph_type=args.graph_type
                )
                break

        # write to file
        file_path = args.file or self.get_default_tasks_data_path(
            args.env, tasks_level_name, args.format)
        graph_data_file_path = self.write_tasks_to_file(
            tasks_data=tasks_data,
            serializer=Serializer(format=args.format),
            file_path=file_path)

        self.app.stdout.write(
            "Tasks were downloaded to {0}\n".format(graph_data_file_path)
        )


class GraphList(base.BaseListCommand):
    """List deployment graphs."""
    entity_name = 'graph'
    columns = ("id",
               "name",
               "tasks",
               "relations")

    def get_parser(self, prog_name):
        parser = super(GraphList, self).get_parser(prog_name)
        parser.add_argument(
            '-e',
            '--env',
            type=int,
            help='Id of the environment'
        )
        parser.add_argument(
            '--cluster',
            dest='filters',
            action='append_const',
            const='cluster',
            help='Include cluster-specific graphs'
        )
        parser.add_argument(
            '--plugins',
            dest='filters',
            action='append_const',
            const='plugin',
            help='Include plugins-specific graphs'
        )
        parser.add_argument(
            '--release',
            dest='filters',
            action='append_const',
            const='release',
            help='Include release-specific graphs'
        )
        return parser

    def take_action(self, args):
        data = self.client.list(env_id=args.env, filters=args.filters)

        # make table context applying special formatting to data copy
        display_data = []
        for d in data:
            d = d.copy()
            d.update({
                'relations': "\n".join(
                    'as "{type}" to {model}(ID={model_id})'.format(**r)
                    for r in d['relations']
                ),
                'tasks': ', '.join(sorted(t['id'] for t in d['tasks']))
            })
            display_data.append(d)

        data = data_utils.get_display_data_multi(self.columns, display_data)
        scolumn_ids = [self.columns.index(col) for col in args.sort_columns]
        data.sort(key=lambda x: [x[scolumn_id] for scolumn_id in scolumn_ids])
        return self.columns, data


class GraphDelete(base.BaseCommand):
    """Delete deployment graph."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphDelete, self).get_parser(prog_name)
        graph_class = parser.add_mutually_exclusive_group(required=True)
        graph_class.add_argument('-e',
                                 '--environment',
                                 type=int,
                                 help='Id of the environment')
        graph_class.add_argument('-r',
                                 '--release',
                                 type=int,
                                 help='Id of the release')
        graph_class.add_argument('-p',
                                 '--plugin',
                                 type=int,
                                 help='Id of the plugin')
        parser.add_argument('-t',
                            '--graph-type',
                            required=True,
                            help='Type of the deployment graph')
        return parser

    def take_action(self, parsed_args):
        parameters_to_graph_class = (
            ('environment', 'clusters'),
            ('release', 'releases'),
            ('plugin', 'plugins'),
        )

        msg = ''
        for parameter, graph_class in parameters_to_graph_class:
            model_id = getattr(parsed_args, parameter)
            if model_id:
                self.client.delete(
                    related_model=graph_class,
                    related_id=model_id,
                    graph_type=parsed_args.graph_type
                )
                msg = ("Deployment graph '{0}' for {1} with id {2} was "
                       "deleted.\n".format(parsed_args.graph_type,
                                           parameter,
                                           model_id))
                break

        self.app.stdout.write(msg)
