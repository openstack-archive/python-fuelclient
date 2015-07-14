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

import argparse
import sys

from fuelclient.cli import serializers
from fuelclient import client


class FuelVersionAction(argparse._VersionAction):
    """Custom argparse._VersionAction subclass to compute fuel server version

    :returns: prints fuel server version
    """
    def __call__(self, parser, namespace, values, option_string=None):
        serializer = serializers.Serializer.from_params(namespace)
        version = client.APIClient.get_fuel_version()
        print(serializer.serialize(version))
        sys.exit(0)
