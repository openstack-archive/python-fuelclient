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

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class FuelVersionClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.FuelVersion

    @classmethod
    def check_advanced_feature(cls):
        if 'advanced' not in cls._entity_wrapper.get_feature_groups():
            msg = "Advanced feature should be enabled in feature groups"
            raise error.ActionException(msg)


def get_client(connection):
    return FuelVersionClient(connection)
