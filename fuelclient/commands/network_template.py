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
from fuelclient.objects.environment import Environment

class NetworkTemplateMixin(object):

    entity_name = 'network'

    @staticmethod
    def add_env_argument(parser):
        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='Upload network template for specified environment'
        )

    @staticmethod
    def add_dir_argument(parser):
        parser.add_argument(
            '-d', '--dir',
            type=str,
            required=True,
            help='Directory with network data'
        )

    def get_parser(self, prog_name):
        parser = super(NetworkTemplateMixin, self).get_parser(prog_name)

        self.add_dir_argument(parser)
        self.add_env_argument(parser)

        return parser


class NetworkTemplateUpload(NetworkTemplateMixin, base.BaseCommand):
    """To upload network configuration for specified environment:

        fuel2 network-template upload --env 1 --dir path/to/directory
    """

    def take_action(self, parsed_args):
        env = Environment(parsed_args.env)
        network_data = env.read_network_data(
            directory=parsed_args.dir)
        env.set_network_data(network_data)

        msg = "Network configuration uploaded\n"
        self.app.stdout.write(msg)


class NetworkTemplateDownload(NetworkTemplateMixin, base.BaseCommand):
    """To download network configuration for environment to the specified
    directory:
        fuel2 network-template download --env 1 --dir path/to/directory
    """

    def take_action(self, parsed_args):
        env = Environment(parsed_args.env)
        network_data = env.get_network_data()
        network_file_path = env.write_network_data(
            network_data, directory=parsed_args.dir)

        msg = ("Network configuration for environment with id={0}"
               " downloaded to {1}\n".format(env.id, network_file_path))
        self.app.stdout.write(msg)


class NetworkTemplateVerify(NetworkTemplateMixin, base.BaseCommand):
    """To verify network configuration for specified environment:
            fuel2 network-template verify --env 1 --dir path/to/directory
    """

    def take_action(self, parsed_args):
        env = Environment(parsed_args.env)
        response = env.verify_network()

        msg = "Verification status is '{status}'. Message: {message}\n"
        self.app.stdout.write(msg.format(**response))
