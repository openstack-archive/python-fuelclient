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

from fuelclient.commands import base


class GraphUpload(base.BaseCommand):
    """Upload deployment graph configuration."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphUpload, self).get_parser(prog_name)
        graph_class = parser.add_mutually_exclusive_group()

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
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Type of the deployment graph')
        parser.add_argument('-f',
                            '--file',
                            type=str,
                            required=True,
                            default=None,
                            help='YAML file that contains '
                                 'deployment graph data.')
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
            "Deployment graph was uploaded from {0}".format(args.file)
        )


class GraphExecute(base.BaseCommand):
    """Start deployment with given graph type."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphExecute, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')
        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Type of the deployment graph')
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
