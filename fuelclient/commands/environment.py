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

import argparse
import os
import shutil

from cliff import show

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils


class EnvMixIn(object):
    entity_name = 'environment'

    supported_file_formats = ('json', 'yaml')

    @staticmethod
    def srs_dir(directory=os.path.curdir):
        path = os.path.abspath(directory)
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(
                '"{0}" is not a directory.'.format(path))
        if not os.access(path, os.R_OK):
            raise argparse.ArgumentTypeError(
                'directory "{0}" is not readable'.format(path))
        return path

    @staticmethod
    def dst_dir(directory=os.path.curdir):
        path = os.path.abspath(directory)
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(
                '"{0}" is not a directory.'.format(path))
        if not os.access(path, os.W_OK):
            raise argparse.ArgumentTypeError(
                'directory "{0}" is not writable'.format(path))
        return path


class EnvList(EnvMixIn, base.BaseListCommand):
    """Show list of all available environments."""

    columns = ("id",
               "status",
               "name",
               "release_id")


class EnvShow(EnvMixIn, base.BaseShowCommand):
    """Show info about environment with given id."""
    columns = ("id",
               "status",
               "fuel_version",
               "name",
               "release_id",
               "is_customized",
               "changes")


class EnvCreate(EnvMixIn, base.BaseShowCommand):
    """Creates environment with given attributes."""

    columns = EnvShow.columns

    def get_parser(self, prog_name):
        # Avoid adding id argument by BaseShowCommand
        parser = show.ShowOne.get_parser(self, prog_name)

        parser.add_argument(
            'name',
            type=str,
            help='Name of the new environment'
        )

        parser.add_argument('-r',
                            '--release',
                            type=int,
                            required=True,
                            help='Id of the release for which will '
                                 'be deployed')

        parser.add_argument('-nst',
                            '--net-segmentation-type',
                            type=str,
                            choices=['vlan', 'gre', 'tun'],
                            dest='nst',
                            default='vlan',
                            help='Network segmentation type.\n'
                                 'WARNING: GRE network segmentation type '
                                 'is deprecated since 7.0 release.')

        return parser

    def take_action(self, parsed_args):
        if parsed_args.nst == 'gre':
            self.app.stderr.write('WARNING: GRE network segmentation type is '
                                  'deprecated since 7.0 release')

        new_env = self.client.create(name=parsed_args.name,
                                     release_id=parsed_args.release,
                                     net_segment_type=parsed_args.nst)

        new_env = data_utils.get_display_data_single(self.columns, new_env)

        return (self.columns, new_env)


class EnvDelete(EnvMixIn, base.BaseDeleteCommand):
    """Delete environment with given id."""

    def get_parser(self, prog_name):
        parser = super(EnvDelete, self).get_parser(prog_name)

        parser.add_argument('-f',
                            '--force',
                            action='store_true',
                            help='Force-delete the environment.')

        return parser

    def take_action(self, parsed_args):
        env = self.client.get_by_id(parsed_args.id)

        if env['status'] == 'operational' and not parsed_args.force:
            self.app.stdout.write("Deleting an operational environment is a "
                                  "dangerous operation.\n"
                                  "Please use --force to bypass this message.")
            return

        return super(EnvDelete, self).take_action(parsed_args)


class EnvUpdate(EnvMixIn, base.BaseShowCommand):
    """Change given attributes for an environment."""

    columns = EnvShow.columns

    def get_parser(self, prog_name):
        # Avoid adding id argument by BaseShowCommand
        parser = show.ShowOne.get_parser(self, prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the nailgun entity to be processed.')

        parser.add_argument('-n',
                            '--name',
                            type=str,
                            dest='name',
                            default=None,
                            help='New name for environment')

        return parser

    def take_action(self, parsed_args):
        updates = {}
        for attr in self.client._updatable_attributes:
            if getattr(parsed_args, attr, None):
                updates[attr] = getattr(parsed_args, attr)

        updated_env = self.client.update(environment_id=parsed_args.id,
                                         **updates)
        updated_env = data_utils.get_display_data_single(self.columns,
                                                         updated_env)

        return (self.columns, updated_env)


class EnvAddNodes(EnvMixIn, base.BaseCommand):
    """Adds nodes to an environment with the specified roles."""

    def get_parser(self, prog_name):

        parser = super(EnvAddNodes, self).get_parser(prog_name)

        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment to add nodes to')

        parser.add_argument('-n',
                            '--nodes',
                            type=int,
                            nargs='+',
                            required=True,
                            help='Ids of the nodes to add.')

        parser.add_argument('-r',
                            '--roles',
                            type=str,
                            nargs='+',
                            required=True,
                            help='Target roles of the nodes.')

        return parser

    def take_action(self, parsed_args):
        env_id = parsed_args.env

        self.client.add_nodes(environment_id=env_id,
                              nodes=parsed_args.nodes,
                              roles=parsed_args.roles)

        msg = 'Nodes {n} were added to the environment {e} with roles {r}\n'
        self.app.stdout.write(msg.format(n=parsed_args.nodes,
                                         e=parsed_args.env,
                                         r=parsed_args.roles))


class EnvRemoveNodes(EnvMixIn, base.BaseCommand):
    """Removes nodes from an environment."""

    def get_parser(self, prog_name):

        parser = super(EnvRemoveNodes, self).get_parser(prog_name)

        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment to remove nodes from')

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-n',
                           '--nodes',
                           type=int,
                           nargs='+',
                           help='Ids of the nodes to remove.')

        group.add_argument('--nodes-all',
                           action='store_true',
                           help='Remove all nodes from environment')

        return parser

    def take_action(self, parsed_args):
        nodes = None if parsed_args.nodes_all else parsed_args.nodes
        self.client.remove_nodes(environment_id=parsed_args.env,
                                 nodes=nodes)

        msg = 'Nodes were removed from the environment with id={e}\n'.format(
            e=parsed_args.env)

        self.app.stdout.write(msg)


class EnvDeploy(EnvMixIn, base.BaseCommand):
    """Deploys changes on the specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvDeploy, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the environment to be deployed.')

        dry_run_help_string = 'Specifies to dry-run a deployment by' \
                              'configuring task executor to dump the' \
                              'deployment graph to a dot file.' \
                              'Store cluster settings and serialized ' \
                              'data in the db and ask the task executor ' \
                              'to dump the resulting graph into a dot file'

        parser.add_argument(
            '-d', '--dry-run', dest="dry_run",
            action='store_true', help=dry_run_help_string)

        return parser

    def take_action(self, parsed_args):
        task_id = self.client.deploy_changes(parsed_args.id,
                                             dry_run=parsed_args.dry_run)

        msg = 'Deployment task with id {t} for the environment {e} '\
              'has been started.\n'.format(t=task_id, e=parsed_args.id)

        self.app.stdout.write(msg)


class EnvRedeploy(EnvDeploy):
    """Redeploys changes on the specified environment."""

    def take_action(self, parsed_args):
        task_id = self.client.redeploy_changes(parsed_args.id,
                                               dry_run=parsed_args.dry_run)

        msg = 'Deployment task with id {t} for the environment {e} '\
              'has been started.\n'.format(t=task_id, e=parsed_args.id)

        self.app.stdout.write(msg)


class EnvSpawnVms(EnvMixIn, base.BaseCommand):
    """Provision specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvSpawnVms, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the environment to be provision.')

        return parser

    def take_action(self, parsed_args):
        return self.client.spawn_vms(parsed_args.id)


class FactsMixIn(object):

    @staticmethod
    def _get_fact_dir(env_id, fact_type, directory):
        return os.path.join(directory, "{0}_{1}".format(fact_type, env_id))

    @staticmethod
    def _read_deployment_facts(directory, data_format):
        return map(
            lambda f: data_utils.read_from_file(f),
            [os.path.join(directory, file_name)
             for file_name in os.listdir(directory)
             if data_format == os.path.splitext(file_name)[1].lstrip('.')]
        )

    @staticmethod
    def _read_provisioning_facts(directory, data_format):
        node_facts = map(
            lambda f: data_utils.read_from_file(f),
            [os.path.join(directory, file_name)
             for file_name in os.listdir(directory)
             if data_format == os.path.splitext(file_name)[1].lstrip('.')
             and 'engine' != os.path.splitext(file_name)[0]]
        )
        engine_facts = data_utils.read_from_file(
            os.path.join(directory, "{}.{}".format('engine', data_format)))

        return {'engine': engine_facts, 'nodes': node_facts}

    @staticmethod
    def _write_deployment_facts(facts, directory, data_format):
        # from 9.0 the deployment info is serialized only per node
        for _fact in facts:
            file_name = "{role}_{uid}." if 'role' in _fact else "{uid}."
            file_name += data_format
            data_utils.write_to_file(
                os.path.join(directory, file_name.format(**_fact)),
                _fact)

    @staticmethod
    def _write_provisioning_facts(facts, directory, data_format):
        file_name = "{}.{}"
        data_utils.write_to_file(
            os.path.join(directory, file_name.format('engine', data_format)),
            facts['engine'])

        for _fact in facts['nodes']:
            data_utils.write_to_file(
                os.path.join(directory,
                             file_name.format(_fact['name'], data_format)),
                _fact)

    def download_facts(self, env_id, fact_type, dst_dir, data_format,
                       nodes=None, default=False):
        facts = self.client.get_facts(
            env_id, fact_type, nodes=nodes, default=default)
        if not facts:
            raise error.ServerDataException(
                "There are no {} facts for this environment!".format(
                    fact_type))

        facts_dir = self._get_fact_dir(env_id, fact_type, dst_dir)
        if os.path.exists(facts_dir):
            shutil.rmtree(facts_dir)
        os.makedirs(facts_dir)

        getattr(self, "_write_{0}_facts".format(fact_type))(
            facts, facts_dir, data_format)

        return facts_dir

    def upload_facts(self, env_id, fact_type, srs_dir, data_format):
        facts_dir = self._get_fact_dir(env_id, fact_type, srs_dir)
        facts = getattr(self, "_read_{0}_facts".format(fact_type))(
            facts_dir, data_format)

        if not facts:
            raise error.ServerDataException(
                "There are no {} facts for this environment!".format(
                    fact_type))

        return self.client.set_facts(env_id, fact_type, facts)


class EnvDeploymentFactsDelete(EnvMixIn, base.BaseCommand):
    """Delete current deployment facts."""

    def get_parser(self, prog_name):
        parser = super(EnvDeploymentFactsDelete, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='ID of the environment to delete the deployment facts')

        return parser

    def take_action(self, parsed_args):
        self.client.delete_facts(parsed_args.id, 'deployment')
        self.app.stdout.write(
            "Deployment facts for environment {} were deleted "
            "successfully.\n".format(parsed_args.id))


class EnvDeploymentFactsDownload(FactsMixIn, EnvMixIn, base.BaseCommand):
    """Download computed deployment facts for orchestrator."""

    def get_parser(self, prog_name):
        parser = super(EnvDeploymentFactsDownload, self).get_parser(prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='ID of the environment')

        parser.add_argument(
            '-d', '--dir',
            type=self.dst_dir,
            help='Path to directory to save deployment facts')

        parser.add_argument(
            '-n', '--nodes',
            type=int,
            nargs='+',
            help='Get deployment facts for nodes with given IDs')

        parser.add_argument(
            '--default',
            action='store_true',
            help='Get default deployment facts')

        parser.add_argument(
            '-f', '--format',
            choices=self.supported_file_formats,
            default='yaml',
            help='Format of serialized deployment facts (default: yaml)')

        return parser

    def take_action(self, parsed_args):
        facts_dir = self.download_facts(
            parsed_args.env,
            'deployment',
            parsed_args.dir,
            parsed_args.format,
            nodes=parsed_args.nodes,
            default=parsed_args.default
        )
        self.app.stdout.write(
            "{0}deployment facts were downloaded to {1}\n".format(
                'Default ' if parsed_args.default else '',
                facts_dir
            ).capitalize())


class EnvDeploymentFactsUpload(FactsMixIn, EnvMixIn, base.BaseCommand):
    """Upload deployment facts."""

    def get_parser(self, prog_name):
        parser = super(EnvDeploymentFactsUpload, self).get_parser(prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='ID of the environment')

        parser.add_argument(
            '-d', '--dir',
            type=self.srs_dir,
            help='Path to directory to read deployment facts')

        parser.add_argument(
            '-f', '--format',
            choices=self.supported_file_formats,
            default='yaml',
            help='Format of serialized deployment facts (default: yaml)')

        return parser

    def take_action(self, parsed_args):
        self.upload_facts(
            parsed_args.env,
            'deployment',
            parsed_args.dir,
            parsed_args.format
        )
        self.app.stdout.write(
            "Deployment facts were uploaded successfully "
            "into environment {}.\n".format(parsed_args.env))


class EnvProvisioningFactsDelete(EnvMixIn, base.BaseCommand):
    """Delete current provisioning facts."""

    def get_parser(self, prog_name):
        parser = super(EnvProvisioningFactsDelete, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='ID of the environment to delete the provisioning facts')

        return parser

    def take_action(self, parsed_args):
        self.client.delete_facts(parsed_args.id, 'provisioning')
        self.app.stdout.write(
            "Provisioning facts for environment {} were deleted "
            "successfully.\n".format(parsed_args.id))


class EnvProvisioningFactsDownload(FactsMixIn, EnvMixIn, base.BaseCommand):
    """Download computed provisioning facts for orchestrator."""

    def get_parser(self, prog_name):
        parser = super(EnvProvisioningFactsDownload, self).get_parser(
            prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='ID of the environment')

        parser.add_argument(
            '-d', '--dir',
            type=self.dst_dir,
            help='Path to directory to save provisioning facts')

        parser.add_argument(
            '-n', '--nodes',
            type=int,
            nargs='+',
            help='Get provisioning facts for nodes with given IDs')

        parser.add_argument(
            '--default',
            action='store_true',
            help='Get default provisioning facts')

        parser.add_argument(
            '-f', '--format',
            choices=self.supported_file_formats,
            default='yaml',
            help='Format of serialized provisioning facts (default: yaml)')

        return parser

    def take_action(self, parsed_args):
        facts_dir = self.download_facts(
            parsed_args.env,
            'provisioning',
            parsed_args.dir,
            parsed_args.format,
            nodes=parsed_args.nodes,
            default=parsed_args.default
        )
        self.app.stdout.write(
            "{0}provisioning facts were downloaded to {1}\n".format(
                'Default ' if parsed_args.default else '',
                facts_dir
            ).capitalize())


class EnvProvisioningFactsUpload(FactsMixIn, EnvMixIn, base.BaseCommand):
    """Upload provisioning facts."""

    def get_parser(self, prog_name):
        parser = super(EnvProvisioningFactsUpload, self).get_parser(prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='ID of the environment')

        parser.add_argument(
            '-d', '--dir',
            type=self.srs_dir,
            help='Path to directory to read provisioning facts')

        parser.add_argument(
            '-f', '--format',
            choices=self.supported_file_formats,
            default='yaml',
            help='Format of serialized provisioning facts (default: yaml)')

        return parser

    def take_action(self, parsed_args):
        self.upload_facts(
            parsed_args.env,
            'provisioning',
            parsed_args.dir,
            parsed_args.format
        )
        self.app.stdout.write(
            "Provisioning facts were uploaded successfully "
            "into environment {}.\n".format(parsed_args.env))
