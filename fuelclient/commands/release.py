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

    columns = (
        'name',
        'priority',
        'uri',
        'section',
        'suite',
        'type')

    @property
    def default_sorting_by(self):
        return ['priority']

    def get_parser(self, prog_name):
        parser = super(ReleaseReposList, self).get_parser(prog_name)
        parser.add_argument('id', type=int,
                            help='Id of the {0}.'.format(self.entity_name))
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_attributes_metadata_by_id(parsed_args.id)
        repos = data["editable"]["repo_setup"]["repos"]["value"]
        repos = data_utils.get_display_data_multi(self.columns, repos)
        repos = self._sort_data(parsed_args, repos)
        return self.columns, repos


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


class ReleaseComponentList(ReleaseMixIn, base.BaseListCommand):
    """Show list of components for a given release."""

    columns = ("name",
               "requires",
               "compatible",
               "incompatible",
               "default")

    @property
    def default_sorting_by(self):
        return ['name']

    @staticmethod
    def retrieve_predicates(statement):
        """Retrieve predicates with respective 'items' components

        :param statement: the dictionary to extract predicate values from
        :return: retrieval result as a string
        """
        predicates = ('any_of', 'all_of', 'one_of', 'none_of')
        for predicate in predicates:
            if predicate in statement:
                result = ', '.join(statement[predicate].get('items'))
                return "{0} ({1})".format(predicate, result)
        raise ValueError('Predicates not found.')

    @classmethod
    def retrieve_data(cls, value):
        """Retrieve names of components or predicates from nested data

        :param value: data to extract name or to retrieve predicates from
        :return: names of components or predicates as a string
        """
        if isinstance(value, list):
            # get only "name" of components otherwise retrieve predicates
            return ', '.join([v['name'] if 'name' in v
                              else cls.retrieve_predicates(v)
                              for v in value])
        return value

    def get_parser(self, prog_name):
        parser = super(ReleaseComponentList, self).get_parser(prog_name)
        parser.add_argument('id', type=int,
                            help='Id of the {0}.'.format(self.entity_name))
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_components_by_id(parsed_args.id)
        # some keys (columns) can be missed in origin data
        # then create them with respective '-' value
        data = [{k: self.retrieve_data(d.get(k, '-')) for k in self.columns}
                for d in data]
        data = data_utils.get_display_data_multi(self.columns, data)
        data = self._sort_data(parsed_args, data)
        return self.columns, data
