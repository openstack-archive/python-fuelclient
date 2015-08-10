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
import sys

import six

from fuelclient.cli.actions import base
import fuelclient.cli.arguments as Args
from fuelclient.cli import error
from fuelclient.objects import environment


class GraphAction(base.Action):
    """Manipulate deployment graph's representation."""

    action_name = 'graph'

    task_types = ('skipped', 'group', 'stage')

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
                "Select target dir to render graph."
            ),
            Args.group(
                Args.get_skip_tasks(),
                Args.get_tasks()
            ),
            Args.get_graph_endpoint(),
            Args.get_graph_startpoint(),
            Args.get_remove_type_arg(self.task_types),
            Args.get_parents_arg(),
        )
        self.flag_func_map = (
            ('render', self.render),
            ('download', self.download),
        )

    @base.check_all("env")
    def download(self, params):
        """Download deployment graph to stdout

        fuel graph --env 1 --download
        fuel graph --env 1 --download --tasks A B C
        fuel graph --env 1 --download --skip X Y --end pre_deployment
        fuel graph --env 1 --download --skip X Y --start post_deployment

        Sepcify output:
        fuel graph --env 1 --download > outpup/dir/file.gv

        Get parents only for task A:

        fuel graph --env 1 --download --parents-for A
        """
        env = environment.Environment(params.env)

        parents_for = getattr(params, 'parents-for')

        used_params = "# params:\n"
        for param in ('start', 'end', 'skip', 'tasks', 'parents-for',
                      'remove'):
            used_params += "# - {0}: {1}\n".format(param,
                                                   getattr(params, param))

        tasks = params.tasks

        if not tasks or (params.skip or params.end or params.start):
            tasks = env.get_tasks(
                skip=params.skip, end=params.end,
                start=params.start, include=params.tasks)

        dotraph = env.get_deployment_tasks_graph(tasks,
                                                 parents_for=parents_for,
                                                 remove=params.remove)
        sys.stdout.write(six.text_type(used_params))
        sys.stdout.write(six.text_type(dotraph))

    @base.check_all("render")
    def render(self, params):
        """Render graph in PNG format

        fuel graph --render graph.gv
        fuel graph --render graph.gv --dir ./output/dir/

        Read graph from stdin
        some_process | fuel graph --render -
        """
        if params.render == '-':
            dot_data = sys.stdin.read()
            out_filename = 'graph.gv'
        elif not os.path.exists(params.render):
            raise error.ArgumentException(
                "Input file does not exist"
            )
        else:
            out_filename = os.path.basename(params.render)
            with open(params.render, 'r') as f:
                dot_data = f.read()

        target_dir = self.full_path_directory(
            self.default_directory(params.dir),
            ''
        )
        target_file = os.path.join(
            target_dir,
            '{0}.png'.format(out_filename),
        )

        if not os.access(os.path.dirname(target_file), os.W_OK):
            raise error.ActionException(
                'Path {0} is not writable'.format(target_file))

        render_graph(dot_data, target_file)
        print('Graph saved in "{0}"'.format(target_file))


def render_graph(input_data, output_path):
    """Renders DOT graph using pydot or pygraphviz depending on their presence.

    If none of the libraries is available and are fully functional it is not
    possible to render graphs.

    :param input_data: DOT graph representation
    :param output_path: path to the rendered graph
    """
    try:
        _render_with_pydot(input_data, output_path)
    except ImportError:
        try:
            _render_with_pygraphiz(input_data, output_path)
        except ImportError:
            raise error.WrongEnvironmentError(
                "This action require Graphviz installed toghether with "
                "'pydot_ng' or 'pygraphviz' Python library")


def _render_with_pydot(input_data, output_path):
    """Renders graph using pydot_ng library."""
    import pydot_ng as pydot

    graph = pydot.graph_from_dot_data(input_data)
    if not graph:
        raise error.BadDataException(
            "Passed data does not contain graph in DOT format")
    try:
        graph.write_png(output_path)
    except pydot.InvocationException as e:
        raise error.WrongEnvironmentError(
            "There was an error with rendering graph:\n{0}".format(e))


def _render_with_pygraphiz(input_data, output_path):
    """Renders graph using pygraphviz library."""
    import pygraphviz as pgv

    graph = pgv.AGraph(string=input_data)
    graph.draw(output_path, prog='dot', format='png')
