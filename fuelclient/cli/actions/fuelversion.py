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

import fuelclient.cli.arguments as Args

from fuelclient.cli.actions.base import Action
from fuelclient.objects.fuelversion import FuelVersion


class FuelVersionAction(Action):
    """Show Fuel server's version
    """

    action_name = "fuel-version"

    def __init__(self):
        super(FuelVersionAction, self).__init__()

        self.args = [
            Args.get_list_arg("Show fuel version"),
        ]
        self.flag_func_map = (
            (None, self.version),
        )

    def version(self, params):
        """To show fuel version data:
                fuel fuel-version
        """
        version = FuelVersion.get_all_data()
        print(self.serializer.serialize(version))
