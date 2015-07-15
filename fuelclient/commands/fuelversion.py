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

from fuelclient.cli.serializers import Serializer
from fuelclient.commands import base


class FuelVersion(base.BaseCommand):
    """Show fuel version."""

    entity_name = 'fuel-version'

    def take_action(self, parsed_args):
        version = self.client.get_all()
        serializer = Serializer.from_params(parsed_args)
        msg = serializer.serialize(version)
        self.app.stdout.write(msg)
