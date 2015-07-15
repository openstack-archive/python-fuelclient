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

from fuelclient.actions import fuel_version
from fuelclient.cli.error import exceptions_decorator


LOG = logging.getLogger(__name__)


class FuelClient(app.App):
    """Main cliff application class.

    Performs initialization of the command manager and
    configuration of basic engines.

    """

    def build_option_parser(self, description, version, argparse_kwargs=None):
        """Overrides default options for backwards compatibility."""
        p_inst = super(FuelClient, self)
        parser = p_inst.build_option_parser(description=description,
                                            version=version,
                                            argparse_kwargs=argparse_kwargs)

        parser.add_argument(
            '--fuel-version',
            action=fuel_version.FuelVersionAction,
            help=("show Fuel server's version number and exit. "
                  "WARNING: deprecated since 7.0 release. "
                  "Please use fuel-version command instead"))

        return parser

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


@exceptions_decorator
def main(argv=sys.argv[1:]):
    fuelclient_app = FuelClient(
        description='Command line interface and Python API wrapper for Fuel.',
        version='7.0.0',
        command_manager=CommandManager('fuelclient', convert_underscores=True)
    )
    return fuelclient_app.run(argv)
