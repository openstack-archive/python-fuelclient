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

from cliff import command
from cliff import show

import fuelclient
from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils


class EnvMixIn(object):
    entity_name = 'environment'


class EnvList(EnvMixIn, base.BaseListCommand):
    """Show list of all avaliable envrionments."""

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
               "grouping",
               "mode",
               "release_id",
               "pending_release_id",
               "is_customized",
               "changes",
               "net_provider")


class EnvCreate(EnvMixIn, show.ShowOne):
    """Creates environment with given attributes."""

    columns = EnvShow.columns

    def get_parser(self, prog_name):
        parser = super(EnvCreate, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            type=str,
            help='Name of the new environment'
        )

        parser.add_argument('-r',
                            '--release',
                            type=int,
                            help='Id of the release for which will '
                                 'be deployed')

        parser.add_argument('-m',
                            '--mode',
                            type=str,
                            choices=['ha_compact', 'multinode'],
                            dest='mode',
                            default='ha_compact',
                            help='Deployment mode of new environment')

        parser.add_argument('-n',
                            '--net-provider',
                            type=str,
                            choices=['nova', 'neutron'],
                            dest='net_provider',
                            default='neutron',
                            help='Network provider for the new environment')

        parser.add_argument('-nst',
                            '--net-segmentation-type',
                            type=str,
                            choices=['vlan', 'gre'],
                            dest='nst',
                            default=None,
                            help='Network segmentation type. Is only '
                                 'used if network provider is  Neutron')

        return parser

    def take_action(self, parsed_args):
        if parsed_args.release is None:
            raise error.ArgumentException('Specifying release id is mandatory')

        client = fuelclient.get_client(self.entity_name, base.VERSION)

        new_env = client.create(name=parsed_args.name,
                                release_id=parsed_args.release,
                                network_provider=parsed_args.net_provider,
                                deployment_mode=parsed_args.mode,
                                net_segment_type=parsed_args.nst)

        new_env = data_utils.get_display_data_single(self.columns, new_env)

        return (self.columns, new_env)


class EnvDelete(EnvMixIn, base.BaseDeleteCommand):
    """Delete environment with given id."""


class EnvUpdate(EnvMixIn, show.ShowOne):
    """Change given attributes for an environment."""

    columns = EnvShow.columns

    updatabe_attributes = ('mode',
                           'name',
                           'pending_release_id')

    def get_parser(self, prog_name):
        parser = super(EnvUpdate, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the nailgun entity to be processed.')

        parser.add_argument('-n',
                            '--name',
                            type=str,
                            dest='name',
                            default=None,
                            help='New name for environment')

        parser.add_argument('-m',
                            '--mode',
                            type=str,
                            dest='mode',
                            choices=['ha_compact', 'multinode'],
                            default=None,
                            help='New mode for environment')

        return parser

    def take_action(self, parsed_args):
        client = fuelclient.get_client(self.entity_name, base.VERSION)

        updates = {}
        for attr in client._updatable_attributes:
            if getattr(parsed_args, attr, None):
                updates[attr] = getattr(parsed_args, attr)

        updated_env = client.update(environment_id=parsed_args.id, **updates)
        updated_env = data_utils.get_display_data_single(self.columns,
                                                         updated_env)

        return (self.columns, updated_env)


class EnvUpgrade(EnvMixIn, command.Command):
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
        client = fuelclient.get_client(self.entity_name, base.VERSION)
        task_id = client.upgrade(parsed_args.id,
                                 parsed_args.pending_release_id)

        msg = 'Upgrade task with id {} for the environment '\
              'has been started.\n'.format(task_id)

        self.app.stdout.write(msg)


class EnvAddNodes(EnvMixIn, command.Command):
    """Adds nodes to an environment with the specified roles."""

    def get_parser(self, prog_name):

        parser = super(EnvAddNodes, self).get_parser(prog_name)

        parser.add_argument('-e',
                            '--env',
                            type=int,
                            help='Id of the environment to add nodes to')

        parser.add_argument('-n',
                            '--nodes',
                            type=str,
                            help='Ids of the nodes to add.')

        parser.add_argument('-r',
                            '--roles',
                            type=str,
                            help='Target roles of the nodes.')

        return parser

    def take_action(self, parsed_args):
        if parsed_args.env is None or parsed_args.nodes is None or \
                parsed_args.roles is None:
            raise error.ArgumentException('--env, --nodes and --roles are '
                                          'mandatory parameters.')

        env_id = parsed_args.env
        nodes = data_utils.str_to_array(parsed_args.nodes, ',', int)
        roles = data_utils.str_to_array(parsed_args.roles, ',', str)

        client = fuelclient.get_client(self.entity_name, base.VERSION)
        client.add_nodes(environment_id=env_id, nodes=nodes, roles=roles)

        msg = 'Nodes {n} were added to the environment {e} with roles {r}\n'
        self.app.stdout.write(msg.format(n=parsed_args.nodes,
                                         e=parsed_args.env,
                                         r=parsed_args.roles))


class EnvDeploy(EnvMixIn, command.Command):
    """Deploys changes on the specified environment."""

    def get_parser(self, prog_name):
        parser = super(EnvDeploy, self).get_parser(prog_name)

        parser.add_argument('id',
                            type=int,
                            help='Id of the nailgun entity to be processed.')

        return parser

    def take_action(self, parsed_args):
        client = fuelclient.get_client(self.entity_name, base.VERSION)

        task_id = client.deploy_changes(parsed_args.id)

        msg = 'Deploy task with id {t} for the environment {e} '\
              'has been started.\n'.format(t=task_id, e=parsed_args.id)

        self.app.stdout.write(msg)
