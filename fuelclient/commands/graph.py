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
from fuelclient.common import data_utils

from fuelclient.commands import base


class GraphList(base.BaseListCommand):
    """Upload deployment graph configuration."""
    entity_name = 'graph'
    columns = ("id",
               "name",
               "tasks",
               "relations")

    def get_parser(self, prog_name):
        parser = super(GraphList, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Environment identifier')
        return parser

    def take_action(self, parsed_args):
        data = self.client.list(
            env_id=parsed_args.env
        )
        # format fields
        for d in data:
            d['relations'] = "\n".join(
                'as "{type}" to {model}(ID={model_id})'
                .format(**r) for r in d['relations']
            )
            d['tasks'] = ', '.join(sorted(t['id'] for t in d['tasks']))
        data = data_utils.get_display_data_multi(self.columns, data)
        scolumn_ids = [self.columns.index(col)
                       for col in parsed_args.sort_columns]
        data.sort(key=lambda x: [x[scolumn_id] for scolumn_id in scolumn_ids])
        return (self.columns, data)


class GraphUpload(base.BaseCommand):
    """Upload deployment graph configuration."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphUpload, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=False,
                            help='Environment identifier')
        parser.add_argument('-r',
                            '--release',
                            type=int,
                            required=False,
                            help='Release identifier')
        parser.add_argument('-p',
                            '--plugin',
                            type=int,
                            required=False,
                            help='Plugin identifier')

        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Graph type string')
        parser.add_argument('-f',
                            '--file',
                            type=str,
                            required=True,
                            default=None,
                            help='YAML file that contains tasks data.')
        return parser

    def take_action(self, args):

        self.client.upload(
            cluster_id=args.env,
            release_id=args.release,
            plugin_id=args.plugin,
            graph_type=args.type,
            file_path=args.file
        )

        self.app.stdout.write(
            "Graph was uploaded from {0}".format(args.file)
        )


class GraphDownload(base.BaseCommand):
    """Download deployment graph configuration."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphDownload, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Environment identifier')

        parser.add_argument('-a',
                            '--all',
                            action="store_true",
                            required=False,
                            default=False,
                            help='Download merged graph for the environment')
        parser.add_argument('-c',
                            '--cluster',
                            action="store_true",
                            required=False,
                            default=False,
                            help='Download cluster-specific tasks')
        parser.add_argument('-p',
                            '--plugins',
                            action="store_true",
                            required=False,
                            default=False,
                            help='Download plugins-specific tasks')
        parser.add_argument('-r',
                            '--release',
                            action="store_true",
                            required=False,
                            default=False,
                            help='Download release-specific tasks')

        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Graph type string')
        parser.add_argument('-f',
                            '--file',
                            type=str,
                            required=False,
                            default=None,
                            help='YAML file that contains tasks data.')
        return parser

    def take_action(self, args):
        file_path = self.client.download(
            env_id=args.env,
            all=args.all,
            cluster=args.cluster,
            release=args.release,
            plugins=args.plugins,
            graph_type=args.type,
            file_path=args.file
        )
        self.app.stdout.write(
            "Graph was downloaded to {0}".format(file_path)
        )


class GraphExecute(base.BaseCommand):
    """Start deployment with given graph type"""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphExecute, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Environment identifier')
        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Graph type string')
        parser.add_argument('-n',
                            '--nodes',
                            type=int,
                            nargs='+',
                            required=False,
                            help='Ids of the nodes to use for deployment.')
        return parser

    def take_action(self, args):
        self.client.execute(
            env_id=args.env,
            graph_type=args.type,
            nodes=args.nodes
        )
        self.app.stdout.write(
            "Deployment was executed"
        )
