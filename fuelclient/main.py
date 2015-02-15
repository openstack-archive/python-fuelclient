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

import logging
import sys

from cliff import app
from cliff.commandmanager import CommandManager

from fuelclient.cli import parser as obsolete_parser

from fuelclient.actions import fuel_version
from fuelclient.actions import help as help_action
from fuelclient.commands import help as help_command


LOG = logging.getLogger(__name__)


class FuelClient(app.App):
    """Main cliff application class.

    Performs initialization of the command manager and
    configuration of basic engines.

    """
    def __init__(self, *args, **kwargs):
        """Initialize the application."""

        super(FuelClient, self).__init__(*args, **kwargs)

        # NOTE(romcheg): Cliff's hard-coded __init__ overloads any
        #                custom help command specified as an entry point.
        # TODO(romcheg): Add custom help command to the entry points list
        #                when the fix for Cliff is landed and released.
        self.command_manager.add_command('help', help_command.HelpCommand)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        """Overrides default options for backwards compatibility."""

        argparse_kwargs = argparse_kwargs or {}
        # override `help` argument
        argparse_kwargs.update({'conflict_handler': 'resolve'})

        parser = super(FuelClient, self).build_option_parser(
            description=description,
            version=version,
            argparse_kwargs=argparse_kwargs
        )

        parser.add_argument(
            '-h', '--help',
            action=help_action.HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit",
        )

        parser.add_argument(
            '--fuel-version',
            action=fuel_version.FuelVersionAction,
            help="show Fuel server's version number and exit"
        )

        return parser

    def run_subcommand(self, argv):
        """Runs a subcommand using either new or old command manager."""

        try:
            self.command_manager.find_command(argv[1:])
        except ValueError:
            LOG.info('Command is not implemented in the new version of '
                     'python-fuelclient yet. Falling back to the previous '
                     ' version.')

            return obsolete_parser.get_parser(argv).parse()

        super(FuelClient, self).run_subcommand(argv[1:])

    def configure_logging(self):
        super(FuelClient, self).configure_logging()

        # there is issue with management url processing by keystone client
        # code in our workflow, so we have to mute appropriate keystone
        # loggers in order to get rid from unprocessable errors
        logging.getLogger('keystoneclient.httpclient').setLevel(logging.ERROR)

        # increase level of loggin for urllib3 to avoid of displaying
        # of useless messages. List of logger names is needed for
        # consistency on different execution environments that could have
        # installed requests packages (which is used urllib3) of different
        # versions in turn
        for logger_name in ('requests.packages.urllib3.connectionpool',
                            'urllib3.connectionpool'):
            logging.getLogger(logger_name).setLevel(logging.WARNING)


def main(argv=sys.argv):
    fuelclient_app = FuelClient(
        description='Command line interface and Python API wrapper for Fuel.',
        version='6.0.0',
        command_manager=CommandManager('fuelclient', convert_underscores=True)
    )
    return fuelclient_app.run(argv)
