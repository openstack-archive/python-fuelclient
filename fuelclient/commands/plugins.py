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


class PluginsMixIn(object):
    entity_name = 'plugins'


class PluginsList(PluginsMixIn, base.BaseListCommand):
    """Show list of all available plugins."""

    columns = ('id',
               'name',
               'version',
               'package_version',
               'releases')


class PluginsSync(PluginsMixIn, base.BaseCommand):
    """Synchronise plugins on file system with plugins in API service."""

    def get_parser(self, prog_name):
        parser = super(PluginsSync, self).get_parser(prog_name)
        parser.add_argument(
            'ids',
            type=int,
            nargs='*',
            metavar='plugin-id',
            help='Synchronise only plugins with specified ids')

        return parser

    def take_action(self, parsed_args):
        ids = parsed_args.ids if len(parsed_args.ids) > 0 else None
        self.client.sync(ids=ids)
        self.app.stdout.write("Plugins were successfully synchronized.\n")
