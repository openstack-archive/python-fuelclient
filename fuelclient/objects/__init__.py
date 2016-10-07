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

"""fuelclient.objects sub-module contains classes that mirror
functionality from nailgun objects.
"""

from fuelclient.objects.base import BaseObject
from fuelclient.objects.environment import Environment
from fuelclient.objects.extension import Extension
from fuelclient.objects.health import Health
from fuelclient.objects.node import Node
from fuelclient.objects.node import NodeCollection
from fuelclient.objects.openstack_config import OpenstackConfig
from fuelclient.objects.release import Release
from fuelclient.objects.role import Role
from fuelclient.objects.task import DeployTask
from fuelclient.objects.task import SnapshotTask
from fuelclient.objects.task import Task
from fuelclient.objects.tag import Tag
from fuelclient.objects.fuelversion import FuelVersion
from fuelclient.objects.network_group import NetworkGroup
from fuelclient.objects.plugins import Plugins
from fuelclient.objects.sequence import Sequence
