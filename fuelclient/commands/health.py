# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

import six

from fuelclient.commands import base
from fuelclient.common import data_utils


class HealthMixIn(object):

    entity_name = 'health'


class HealthList(HealthMixIn, base.BaseListCommand):
    """List of all available health check test sets"""

    columns = ("id",
               "name")

    def get_parser(self, prog_name):
        parser = super(HealthList, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_all(parsed_args.env)

        data = data_utils.get_display_data_multi(self.columns, data)
        return self.columns, data


class HealthCheck(HealthMixIn, base.BaseCommand):
    """Run specified health check test for a given environment."""

    def get_parser(self, prog_name):
        parser = super(HealthCheck, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')
        parser.add_argument('-f',
                            '--force',
                            action='store_true',
                            help='Force run health check tests.')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-t',
                           '--tests',
                           nargs='+',
                           help='Name of the test sets to run.')
        group.add_argument('--tests-all',
                           action='store_true',
                           help='Run all health check tests.')
        parser.add_argument('--ostf-username',
                            default=None,
                            help='OSTF username.')
        parser.add_argument('--ostf-password',
                            default=None,
                            help='OSTF password.')
        parser.add_argument('--ostf-tenant-name',
                            default=None,
                            help='OSTF tenant name.')
        return parser

    def take_action(self, parsed_args):
        test_sets = None if parsed_args.tests_all else parsed_args.tests
        ostf_credentials = {}
        if parsed_args.ostf_tenant_name is not None:
            ostf_credentials['tenant'] = parsed_args.ostf_tenant_name
        if parsed_args.ostf_username is not None:
            ostf_credentials['username'] = parsed_args.ostf_username
        if parsed_args.ostf_password is not None:
            ostf_credentials['password'] = params.parsed_args.ostf_password

        if not ostf_credentials:
            self.app.stdout.write("WARNING: ostf credentials are going to be "
                                  "mandatory in the next release.\n")

        data = self.client.check(parsed_args.env,
                                 ostf_credentials=ostf_credentials,
                                 test_sets=test_sets,
                                 force=parsed_args.force)

        data = {ts["testset"]: ts["id"] for ts in data}
        msg = ("Health check tests with respective ids: {0} for "
               "the environment with id {1} has been "
               "started\n".format(', '.join("{} ({})".format(key, val) for
                                            (key, val) in six.iteritems(data)),
                                  parsed_args.env))
        self.app.stdout.write(msg)


class HealthGetStatus(HealthMixIn, base.BaseCommand):
    """Get current health check procedure status for a given environment."""

    def get_parser(self, prog_name):
        parser = super(HealthGetStatus, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')
        return parser

    def take_action(self, parsed_args):
        data = self.client.get_status(parsed_args.env)

        msg = "{}\n".format(data)
        self.app.stdout.write(msg)
