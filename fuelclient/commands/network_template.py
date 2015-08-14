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


class NetworkTemplateMixin(object):

    entity_name = 'environment'

    @staticmethod
    def add_env_argument(parser):
        parser.add_argument(
            'env',
            type=int,
            help='Upload network template for specified environment'
        )

    @staticmethod
    def add_dir_argument(parser):
        parser.add_argument(
            '-d', '--dir',
            type=str,
            help='Directory with network data'
        )

    @staticmethod
    def add_file_argument(parser):
        parser.add_argument(
            '-f', '--file',
            type=str,
            help='Yaml file containing network template'
        )


class NetworkTemplateUpload(NetworkTemplateMixin, base.BaseCommand):
    """To upload network configuration for specified environment:

        fuel2 network-template upload --file path/to/file_name.yaml 1
    """

    def get_parser(self, prog_name):
        parser = super(NetworkTemplateUpload, self).get_parser(prog_name)

        self.add_env_argument(parser)
        self.add_file_argument(parser)

        return parser

    def take_action(self, parsed_args):

        file_path = self.client.upload_network_template(
            parsed_args.env, parsed_args.file)
        msg = "Network template {0} has been uploaded.\n".format(file_path)
        self.app.stdout.write(msg)


class NetworkTemplateDownload(NetworkTemplateMixin, base.BaseCommand):
    """To download network configuration for environment to the specified
    directory:
        fuel2 network-template download --dir path/to/directory 1
    """

    def get_parser(self, prog_name):
        parser = super(NetworkTemplateDownload, self).get_parser(prog_name)

        self.add_dir_argument(parser)
        self.add_env_argument(parser)

        return parser

    def take_action(self, parsed_args):
        file_path = self.client.download_network_template(
            parsed_args.env, parsed_args.dir)

        msg = ("Network template configuration for environment with id={0}"
               " downloaded to {1}\n").format(
                   parsed_args.env, file_path)
        self.app.stdout.write(msg)


class NetworkTemplateDelete(NetworkTemplateMixin, base.BaseCommand):

    def get_parser(self, prog_name):
        parser = super(NetworkTemplateDelete, self).get_parser(prog_name)

        self.add_env_argument(parser)

        return parser

    def take_action(self, parsed_args):
        self.client.delete_network_template(parsed_args.env)

        msg = ("Network template for environment id={0}"
               " has been deleted.\n".format(parsed_args.env))
        self.app.stdout.write(msg)
