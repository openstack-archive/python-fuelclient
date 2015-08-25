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

from cliff import show

from fuelclient.commands import base
from fuelclient.common import data_utils


class EnvMixIn(object):
    entity_name = 'environment'


class EnvList(EnvMixIn, base.BaseListCommand):
    """Show list of all available environments."""

    columns = ("id",
               "status",
               "name",
               "mode",
               "release_id",
               "net_provider")


class EnvShow(EnvMixIn, base.BaseShowCommand):
    """Show info about environment with given id."""
    columns = ("id",
               "status",
               "fuel_version",
               "name",
               "mode",
               "release_id",
               "pending_release_id",
               "is_customized",
               "changes",
               "net_provider")


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

        parser.add_argument('-n',
                            '--net-provider',
                            type=str,
                            choices=['nova', 'neutron'],
                            dest='net_provider',
                            default='neutron',
                            help=('Network provider for the new environment. '
                                  'WARNING: nova-network is deprecated since '
                                  '6.1 release'))

        parser.add_argument('-nst',
                            '--net-segmentation-type',
                            type=str,
                            choices=['vlan', 'gre', 'tun'],
                            dest='nst',
                            default='vlan',
                            help='Network segmentation type. Is only '
                                 'used if network provider is Neutron.'
                                 'WARNING: GRE network segmentation type '
                                 'is deprecated since 7.0 release.')

        return parser

    def take_action(self, parsed_args):
        if parsed_args.net_provider == 'nova':
            self.app.stdout.write('WARNING: nova-network is deprecated '
                                  'since 6.1 release')

        if parsed_args.net_provider == 'neutron' and parsed_args.nst == 'gre':
            self.app.stdout.write('WARNING: GRE network segmentation type is '
                                  'deprecated since 7.0 release')

        new_env = self.client.create(name=parsed_args.name,
                                     release_id=parsed_args.release,
                                     network_provider=parsed_args.net_provider,
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


class EnvUpgrade(EnvMixIn, base.BaseCommand):
    """Upgrades environment to given relese."""

    def get_parser(self, prog_name):
        parser = super(EnvUpgrade, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the environmen to be upgraded.')

        parser.add_argument('pending_release_id',
                            type=int,
                            help='Relese id for upgrading the environment to')

        return parser

    def take_action(self, parsed_args):
        task_id = self.client.upgrade(parsed_args.id,
                                      parsed_args.pending_release_id)

        msg = 'Upgrade task with id {0} for the environment '\
              'has been started.\n'.format(task_id)

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


class EnvDeploy(EnvMixIn, base.BaseCommand):
    """Deploys changes on the specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvDeploy, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the nailgun entity to be processed.')

        return parser

    def take_action(self, parsed_args):
        task_id = self.client.deploy_changes(parsed_args.id)

        msg = 'Deploy task with id {t} for the environment {e} '\
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
