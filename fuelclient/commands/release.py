# -*- coding: utf-8 -*-

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
from fuelclient.common import data_utils
from fuelclient import utils


class ReleaseMixIn(object):
    entity_name = 'release'


class ReleaseList(ReleaseMixIn, base.BaseListCommand):
    """Show list of all available releases."""

    columns = ("id",
               "name",
               "state",
               "operating_system",
               "version")


class ReleaseReposList(ReleaseMixIn, base.BaseListCommand):
    """Show repos for a given release."""

    columns = ()

    def _repo_columns(self, repos):
        if repos:
            return tuple(repos[0])
        return ()

    def get_parser(self, prog_name):
        parser = super(ReleaseReposList, self).get_parser(prog_name)
        parser.add_argument('id', type=int,
                            help='Id of the {0}.'.format(self.entity_name))
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_attributes_metadata_by_id(parsed_args.id)
        repos = data["editable"]["repo_setup"]["repos"]["value"]
        repos = data_utils.get_display_data_multi(self._repo_columns(repos), repos)
        return self._repo_columns(repos), repos


class ReleaseReposUpdate(ReleaseMixIn, base.BaseCommand):
    """Update repos for a given release."""

    def get_parser(self, prog_name):
        parser = super(ReleaseReposUpdate, self).get_parser(prog_name)
        parser.add_argument(
            '-f', '--file', action='store', required=True,
            help='Input yaml file with list of repositories')
        parser.add_argument(
            'id', type=int, help='Id of the {0}.'.format(self.entity_name))
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_attributes_metadata_by_id(parsed_args.id)
        new_repos = utils.parse_yaml_file(parsed_args.file)
        data["editable"]["repo_setup"]["repos"]["value"] = new_repos
        self.client.update_attributes_metadata_by_id(parsed_args.id, data)
        self.app.stdout.write(
            "Repositories for the release with "
            "id {rel_id} were set from {file}.\n".format(
                rel_id=parsed_args.id,
                file=parsed_args.file
            )
        )
