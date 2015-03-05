#    Copyright 2014 Mirantis, Inc.
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

from cliff import help

from fuelclient.cli import parser as obsolete_parser


class HelpCommand(help.HelpCommand):
    """Shows help message for a command."""

    def take_action(self, parsed_args):
        try:
            super(HelpCommand, self).take_action(parsed_args)
        except ValueError:
            # try to find command in old versioned parser
            cmd_name = parsed_args.cmd[0]
            for pr in obsolete_parser.get_parser().subcommands_parsers:
                if cmd_name == pr.prog[5:]:
                    self.app.stdout.write(pr.format_help())
                    return
            raise
