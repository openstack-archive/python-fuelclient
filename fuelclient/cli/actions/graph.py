# -*- coding: utf-8 -*-

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

from fuelclient.cli.actions import base
import fuelclient.cli.arguments as Args
from fuelclient.cli import error
from fuelclient.cli import utils
from fuelclient.objects import environment


class GraphAction(base.Action):
    """Manipulate deployment graph's representation."""

    action_name = 'graph'

    def __init__(self):
        super(GraphAction, self).__init__()
        self.args = (
            Args.get_env_arg(),
            Args.get_render_arg(
                "Render graph from DOT to PNG"
            ),
            Args.get_download_arg(
                "Download graph of specific cluster"
            ),
            Args.get_dir_arg(
                "Select target directory."
            ),
            Args.group(
                Args.get_skip_tasks(),
                Args.get_tasks()
            ),
            Args.get_graph_endpoint(),
            Args.get_graph_startpoint(),
            Args.get_parents_arg(),
        )
        self.flag_func_map = (
            ('render', self.render),
            ('download', self.download),
            (None, self.download)
        )

    @base.check_all("env")
    def download(self, params):
        """Download deployment graph
        fuel graph --env 1 --download
        fuel graph --env 1 --download --tasks A B C
        fuel graph --env 1 --download --skip X Y --end pre_deployment
        fuel graph --env 1 --download --skip X Y --start post_deployment

        Get parents only for task A:

        fuel graph --env 1 --download --parents-for A
        """
        env = environment.Environment(params.env)

        target_dir = self.full_path_directory(
            self.default_directory(params.dir),
            'cluster_{0}'.format(env.id)
        )
        target_file = os.path.join(
            target_dir, 'deployment_graph.gv'
        )

        if params.tasks:
            tasks = params.tasks
        else:
            tasks = env.get_tasks(
                skip=params.skip, end=params.end, start=params.start)

        parents_for = getattr(params, 'parents-for')
        dotraph = env.get_deployment_tasks_graph(tasks,
                                                 parents_for=parents_for)
        with open(target_file, 'w') as f:
            f.write(dotraph)

        print('Graph for cluster {0} saved in {1}'.format(env.id, target_file))

    @base.check_all("render")
    def render(self, params):
        """Render graph in PNG format

        fuel graph --render graph.gv
        fuel graph --render graph.gv --dir ./output/dir/
        """
        if not os.path.exists(params.render):
            raise error.ArgumentException(
                "Input file does not exist"
            )
        target_dir = self.full_path_directory(
            self.default_directory(params.dir),
            ''
        )
        target_file = os.path.join(
            target_dir,
            '{0}.png'.format(os.path.basename(params.render)),
        )
        utils.render_graph(params.render, target_file)
        print('Rendered graph "{0}" saved in "{1}"'.format(
            params.render, target_file))
