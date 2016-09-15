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

import abc
import argparse
import functools
import os
import shutil

import six

from cliff import show
from oslo_utils import fileutils

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils


class EnvMixIn(object):
    entity_name = 'environment'

    supported_file_formats = ('json', 'yaml')
    allowed_attr_types = ('network', 'settings')

    @staticmethod
    def source_dir(directory):
        """Check that the source directory exists and is readable.

        :param directory: Path to source directory
        :type directory: str
        :return: Absolute path to source directory
        :rtype: str
        """
        path = os.path.abspath(directory)
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(
                '"{0}" is not a directory.'.format(path))
        if not os.access(path, os.R_OK):
            raise argparse.ArgumentTypeError(
                'directory "{0}" is not readable'.format(path))
        return path

    @staticmethod
    def destination_dir(directory):
        """Check that the destination directory exists and is writable.

        :param directory: Path to destination directory
        :type directory: str
        :return: Absolute path to destination directory
        :rtype: str
        """
        path = os.path.abspath(directory)
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(
                '"{0}" is not a directory.'.format(path))
        if not os.access(path, os.W_OK):
            raise argparse.ArgumentTypeError(
                'directory "{0}" is not writable'.format(path))
        return path


@six.add_metaclass(abc.ABCMeta)
class BaseUploadCommand(EnvMixIn, base.BaseCommand):

    @abc.abstractproperty
    def uploader(self):
        pass

    @abc.abstractproperty
    def attribute(self):
        pass

    def get_parser(self, prog_name):
        parser = super(BaseUploadCommand, self).get_parser(prog_name)
        parser.add_argument('id',
                            type=int,
                            help='Id of environment.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized '
                                 '{}.'.format(self.attribute))
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.curdir,
                            help='Source directory. Defaults to the '
                                 'current directory.')

        return parser

    def take_action(self, parsed_args):
        directory = parsed_args.directory
        file_path = self.get_attributes_path(self.attribute,
                                             parsed_args.format,
                                             parsed_args.id,
                                             directory)
        try:
            with open(file_path, 'r') as stream:
                attribute = data_utils.safe_load(parsed_args.format, stream)
        except (IOError, OSError):
            msg = 'Could not read configuration of {} at {}.'
            raise error.InvalidFileException(msg.format(self.attribute,
                                                        file_path))

        self.uploader(parsed_args.id, attribute)

        msg = ('Configuration of {t} for the environment with id '
               '{env} was loaded from {path}\n')

        self.app.stdout.write(msg.format(t=self.attribute,
                                         env=parsed_args.id,
                                         path=file_path))


@six.add_metaclass(abc.ABCMeta)
class BaseDownloadCommand(EnvMixIn, base.BaseCommand):

    @abc.abstractproperty
    def downloader(self):
        pass

    @abc.abstractproperty
    def attribute(self):
        pass

    def get_parser(self, prog_name):
        parser = super(BaseDownloadCommand, self).get_parser(prog_name)
        parser.add_argument('id',
                            type=int,
                            help='Id of an environment.')
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized '
                                 '{}.'.format(self.attribute))
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.curdir,
                            help='Destination directory. Defaults to the '
                                 'current directory.')

        return parser

    def take_action(self, parsed_args):
        directory = parsed_args.directory or os.curdir
        attributes = self.downloader(parsed_args.id)

        file_path = self.get_attributes_path(self.attribute,
                                             parsed_args.format,
                                             parsed_args.id,
                                             directory)

        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format, stream, attributes)
        except (IOError, OSError):
            msg = 'Could not store configuration of {} at {}.'
            raise error.InvalidFileException(msg.format(self.attribute,
                                                        file_path))

        msg = ('Configuration of {t} for the environment with id '
               '{env} was stored in {path}\n')
        self.app.stdout.write(msg.format(t=self.attribute,
                                         env=parsed_args.id,
                                         path=file_path))


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


class EnvReset(EnvMixIn, base.BaseCommand):
    """Reset deployed environment."""

    def get_parser(self, prog_name):
        parser = super(EnvReset, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the environment to reset.')
        parser.add_argument('-f',
                            '--force',
                            action='store_true',
                            help='Force reset environment.')

        return parser

    def take_action(self, parsed_args):
        result = self.client.reset(parsed_args.id, force=parsed_args.force)

        msg = ('Reset task with id {t} for the environment {e} '
               'has been started.\n'.format(t=result.data['id'],
                                            e=result.data['cluster']))

        self.app.stdout.write(msg)


class EnvStopDeploy(EnvMixIn, base.BaseCommand):
    """Stop deployment process for specific environment."""

    def get_parser(self, prog_name):
        parser = super(EnvStopDeploy, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the environment to stop deployment.')

        return parser

    def take_action(self, parsed_args):
        result = self.client.stop(parsed_args.id)

        msg = ('Stop deployment task with id {t} for the environment '
               '{e} has been started.\n'.format(t=result.data['id'],
                                                e=result.data['cluster']))
        self.app.stdout.write(msg)


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
        noop_run_help_string = 'Specifies noop-run deployment ' \
                               'configuring tasks executor to run ' \
                               'puppet and shell tasks in noop mode and ' \
                               'skip all other. Stores noop-run result ' \
                               'summary in nailgun database'
        parser.add_argument(
            '-d', '--dry-run', dest="dry_run",
            action='store_true', help=dry_run_help_string)
        parser.add_argument(
            '--noop', dest="noop_run",
            action='store_true', help=noop_run_help_string)

        return parser

    def take_action(self, parsed_args):
        task_id = self.client.deploy_changes(parsed_args.id,
                                             dry_run=parsed_args.dry_run,
                                             noop_run=parsed_args.noop_run)

        msg = 'Deployment task with id {t} for the environment {e} '\
              'has been started.\n'.format(t=task_id, e=parsed_args.id)

        self.app.stdout.write(msg)


class EnvRedeploy(EnvDeploy):
    """Redeploys changes on the specified environment."""

    def take_action(self, parsed_args):
        task_id = self.client.redeploy_changes(parsed_args.id,
                                               dry_run=parsed_args.dry_run,
                                               noop_run=parsed_args.noop_run)

        msg = 'Deployment task with id {t} for the environment {e} '\
              'has been started.\n'.format(t=task_id, e=parsed_args.id)

        self.app.stdout.write(msg)


class EnvProvisionNodes(EnvMixIn, base.BaseCommand):
    """Provision specified nodes for a specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvProvisionNodes, self).get_parser(prog_name)

        parser.add_argument('-e',
                            '--env',
                            required=True,
                            type=int,
                            help='Id of the environment.')
        parser.add_argument('-n',
                            '--nodes',
                            required=True,
                            type=int,
                            nargs='+',
                            help='Ids of nodes to provision.')

        return parser

    def take_action(self, parsed_args):
        node_ids = parsed_args.nodes
        task = self.client.provision_nodes(parsed_args.env, node_ids)

        msg = ('Provisioning task with id {t} for the nodes {n} '
               'within the environment {e} has been '
               'started.\n').format(t=task['id'],
                                    e=parsed_args.env,
                                    n=', '.join(str(i) for i in node_ids))

        self.app.stdout.write(msg)


class EnvDeployNodes(EnvMixIn, base.BaseCommand):
    """Deploy specified nodes for a specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvDeployNodes, self).get_parser(prog_name)

        parser.add_argument('-e',
                            '--env',
                            required=True,
                            type=int,
                            help='Id of the environment.')
        parser.add_argument('-n',
                            '--nodes',
                            required=True,
                            type=int,
                            nargs='+',
                            help='Ids of nodes to deploy.')
        parser.add_argument('-f',
                            '--force',
                            action='store_true',
                            help='Force deploy nodes.')

        noop_run_help_string = 'Specifies noop-run deployment ' \
                               'configuring tasks executor to run ' \
                               'puppet and shell tasks in noop mode and ' \
                               'skip all other. Stores noop-run result ' \
                               'summary in nailgun database'
        parser.add_argument('--noop', dest="noop_run", action='store_true',
                            help=noop_run_help_string)
        return parser

    def take_action(self, parsed_args):
        node_ids = parsed_args.nodes
        task = self.client.deploy_nodes(parsed_args.env, node_ids,
                                        force=parsed_args.force,
                                        noop_run=parsed_args.noop_run)

        msg = ('Deployment task with id {t} for the nodes {n} within '
               'the environment {e} has been '
               'started.\n').format(t=task['id'],
                                    e=parsed_args.env,
                                    n=', '.join(str(i) for i in node_ids))

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


class EnvNetworkVerify(EnvMixIn, base.BaseCommand):
    """Run network verification for specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvNetworkVerify, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the environment to verify network.')

        return parser

    def take_action(self, parsed_args):
        task = self.client.verify_network(parsed_args.id)
        msg = 'Network verification task with id {t} for the environment {e} '\
              'has been started.\n'.format(t=task['id'], e=parsed_args.id)

        self.app.stdout.write(msg)


class EnvNetworkUpload(BaseUploadCommand):
    """Upload network configuration and apply it to an environment."""

    attribute = 'network'

    @property
    def uploader(self):
        return self.client.set_network_configuration


class EnvNetworkDownload(BaseDownloadCommand):
    """Download and store network configuration of an environment."""

    attribute = 'network'

    @property
    def downloader(self):
        return self.client.get_network_configuration


class EnvSettingsUpload(BaseUploadCommand):
    """Upload and apply environment settings."""

    attribute = 'settings'

    @property
    def uploader(self):
        return functools.partial(self.client.set_settings,
                                 force=self.force_flag)

    def get_parser(self, prog_name):
        parser = super(EnvSettingsUpload, self).get_parser(prog_name)
        parser.add_argument('--force',
                            action='store_true',
                            help='Force applying the settings.')

        return parser

    def take_action(self, parsed_args):
        self.force_flag = parsed_args.force

        super(EnvSettingsUpload, self).take_action(parsed_args)


class EnvSettingsDownload(BaseDownloadCommand):
    """Download and store environment settings."""

    attribute = 'settings'

    @property
    def downloader(self):
        return self.client.get_settings


class FactsMixIn(object):

    @staticmethod
    def _get_fact_dir(env_id, fact_type, directory):
        return os.path.join(directory, "{0}_{1}".format(fact_type, env_id))

    @staticmethod
    def _read_deployment_facts_from_file(directory, file_format):
        return list(six.moves.map(
            lambda f: data_utils.read_from_file(f),
            [os.path.join(directory, file_name)
             for file_name in os.listdir(directory)
             if file_format == os.path.splitext(file_name)[1].lstrip('.')]
        ))

    @staticmethod
    def _read_provisioning_facts_from_file(directory, file_format):
        node_facts = list(six.moves.map(
            lambda f: data_utils.read_from_file(f),
            [os.path.join(directory, file_name)
             for file_name in os.listdir(directory)
             if file_format == os.path.splitext(file_name)[1].lstrip('.')
             and 'engine' != os.path.splitext(file_name)[0]]
        ))

        engine_facts = None
        engine_file = os.path.join(directory,
                                   "{}.{}".format('engine', file_format))
        if os.path.lexists(engine_file):
            engine_facts = data_utils.read_from_file(engine_file)

        return {'engine': engine_facts, 'nodes': node_facts}

    @staticmethod
    def _write_deployment_facts_to_file(facts, directory, file_format):
        # from 9.0 the deployment info is serialized only per node
        for _fact in facts:
            file_name = "{role}_{uid}." if 'role' in _fact else "{uid}."
            file_name += file_format
            data_utils.write_to_file(
                os.path.join(directory, file_name.format(**_fact)),
                _fact)

    @staticmethod
    def _write_provisioning_facts_to_file(facts, directory, file_format):
        file_name = "{uid}."
        file_name += file_format
        data_utils.write_to_file(
            os.path.join(directory, file_name.format(uid='engine')),
            facts['engine'])

        for _fact in facts['nodes']:
            data_utils.write_to_file(
                os.path.join(directory, file_name.format(**_fact)),
                _fact)

    def download(self, env_id, fact_type, destination_dir, file_format,
                 nodes=None, default=False, split=None):
        facts = self.client.download_facts(
            env_id, fact_type, nodes=nodes, default=default, split=split)

        facts_dir = self._get_fact_dir(env_id, fact_type, destination_dir)
        if os.path.exists(facts_dir):
            shutil.rmtree(facts_dir)
        os.makedirs(facts_dir)

        getattr(self, "_write_{0}_facts_to_file".format(fact_type))(
            facts, facts_dir, file_format)

        return facts_dir

    def upload(self, env_id, fact_type, source_dir, file_format):
        facts_dir = self._get_fact_dir(env_id, fact_type, source_dir)
        facts = getattr(self, "_read_{0}_facts_from_file".format(fact_type))(
            facts_dir, file_format)

        if not facts \
                or isinstance(facts, dict) and not six.moves.reduce(
                    lambda a, b: a or b, facts.values()):
            raise error.ServerDataException(
                "There are no {} facts for this environment!".format(
                    fact_type))

        return self.client.upload_facts(env_id, fact_type, facts)


class BaseEnvFactsDelete(EnvMixIn, base.BaseCommand):
    """Delete current various facts for orchestrator."""

    fact_type = ''

    def get_parser(self, prog_name):
        parser = super(BaseEnvFactsDelete, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            type=int,
            help='ID of the environment')

        return parser

    def take_action(self, parsed_args):
        self.client.delete_facts(parsed_args.id, self.fact_type)
        self.app.stdout.write(
            "{0} facts for the environment {1} were deleted "
            "successfully.\n".format(self.fact_type.capitalize(),
                                     parsed_args.id)
        )


class EnvDeploymentFactsDelete(BaseEnvFactsDelete):
    """Delete current deployment facts."""

    fact_type = 'deployment'


class EnvProvisioningFactsDelete(BaseEnvFactsDelete):
    """Delete current provisioning facts."""

    fact_type = 'provisioning'


class BaseEnvFactsDownload(FactsMixIn, EnvMixIn, base.BaseCommand):
    """Download various facts for orchestrator."""

    fact_type = ''
    fact_default = False

    def get_parser(self, prog_name):
        parser = super(BaseEnvFactsDownload, self).get_parser(prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='ID of the environment')

        parser.add_argument(
            '-d', '--directory',
            type=self.destination_dir,
            default=os.path.curdir,
            help='Path to directory to save {} facts. '
                 'Defaults to the current directory'.format(self.fact_type))

        parser.add_argument(
            '-n', '--nodes',
            type=int,
            nargs='+',
            help='Get {} facts for nodes with given IDs'.format(
                self.fact_type))

        parser.add_argument(
            '-f', '--format',
            choices=self.supported_file_formats,
            required=True,
            help='Format of serialized {} facts'.format(self.fact_type))

        parser.add_argument(
            '--no-split',
            action='store_false',
            dest='split',
            default=True,
            help='Do not split deployment info for node and cluster parts.'
        )

        return parser

    def take_action(self, parsed_args):
        facts_dir = self.download(
            parsed_args.env,
            self.fact_type,
            parsed_args.directory,
            parsed_args.format,
            nodes=parsed_args.nodes,
            default=self.fact_default,
            split=parsed_args.split
        )
        self.app.stdout.write(
            "{0} {1} facts for the environment {2} "
            "were downloaded to {3}\n".format(
                'Default' if self.fact_default else 'User-defined',
                self.fact_type,
                parsed_args.env,
                facts_dir)
        )


class EnvDeploymentFactsDownload(BaseEnvFactsDownload):
    """Download the user-defined deployment facts."""

    fact_type = 'deployment'
    fact_default = False


class EnvDeploymentFactsGetDefault(BaseEnvFactsDownload):
    """Download the default deployment facts."""

    fact_type = 'deployment'
    fact_default = True


class EnvProvisioningFactsDownload(BaseEnvFactsDownload):
    """Download the user-defined provisioning facts."""

    fact_type = 'provisioning'
    fact_default = False


class EnvProvisioningFactsGetDefault(BaseEnvFactsDownload):
    """Download the default provisioning facts."""

    fact_type = 'provisioning'
    fact_default = True


class BaseEnvFactsUpload(FactsMixIn, EnvMixIn, base.BaseCommand):
    """Upload various facts for orchestrator."""

    fact_type = ''

    def get_parser(self, prog_name):
        parser = super(BaseEnvFactsUpload, self).get_parser(prog_name)

        parser.add_argument(
            '-e', '--env',
            type=int,
            required=True,
            help='ID of the environment')

        parser.add_argument(
            '-d', '--directory',
            type=self.source_dir,
            default=os.path.curdir,
            help='Path to directory to read {} facts. '
                 'Defaults to the current directory'.format(self.fact_type))

        parser.add_argument(
            '-f', '--format',
            choices=self.supported_file_formats,
            required=True,
            help='Format of serialized {} facts'.format(self.fact_type))

        return parser

    def take_action(self, parsed_args):
        self.upload(
            parsed_args.env,
            self.fact_type,
            parsed_args.directory,
            parsed_args.format
        )
        self.app.stdout.write(
            "{0} facts for the environment {1} were uploaded "
            "successfully.\n".format(self.fact_type.capitalize(),
                                     parsed_args.env)
        )


class EnvDeploymentFactsUpload(BaseEnvFactsUpload):
    """Upload deployment facts."""

    fact_type = 'deployment'


class EnvProvisioningFactsUpload(BaseEnvFactsUpload):
    """Upload provisioning facts."""

    fact_type = 'provisioning'
