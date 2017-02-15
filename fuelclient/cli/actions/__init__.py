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
"""fuelclient.cli.actions sub-module contains files with action classes
which implement command line interface logic

All action classes must be added to action_tuple to be used by parser
"""
from fuelclient.cli.actions.deploy import DeployChangesAction
from fuelclient.cli.actions.deploy import RedeployChangesAction
from fuelclient.cli.actions.deployment_tasks import DeploymentTasksAction
from fuelclient.cli.actions.environment import EnvironmentAction
from fuelclient.cli.actions.fact import DeploymentAction
from fuelclient.cli.actions.fact import ProvisioningAction
from fuelclient.cli.actions.graph import GraphAction
from fuelclient.cli.actions.token import TokenAction
from fuelclient.cli.actions.health import HealthCheckAction
from fuelclient.cli.actions.interrupt import ResetAction
from fuelclient.cli.actions.interrupt import StopAction
from fuelclient.cli.actions.network import NetworkAction
from fuelclient.cli.actions.network import NetworkTemplateAction
from fuelclient.cli.actions.network_group import NetworkGroupAction
from fuelclient.cli.actions.node import NodeAction
from fuelclient.cli.actions.nodegroup import NodeGroupAction
from fuelclient.cli.actions.notifications import NotificationsAction
from fuelclient.cli.actions.notifications import NotifyAction
from fuelclient.cli.actions.openstack_config import OpenstackConfigAction
from fuelclient.cli.actions.release import ReleaseAction
from fuelclient.cli.actions.role import RoleAction
from fuelclient.cli.actions.settings import SettingsAction
from fuelclient.cli.actions.snapshot import SnapshotAction
from fuelclient.cli.actions.user import UserAction
from fuelclient.cli.actions.plugins import PluginAction
from fuelclient.cli.actions.fuelversion import FuelVersionAction
from fuelclient.cli.actions.vip import VIPAction

actions_tuple = (
    DeployChangesAction,
    DeploymentAction,
    DeploymentTasksAction,
    EnvironmentAction,
    FuelVersionAction,
    GraphAction,
    HealthCheckAction,
    NetworkAction,
    NetworkGroupAction,
    NetworkTemplateAction,
    NodeAction,
    NodeGroupAction,
    NotificationsAction,
    NotifyAction,
    OpenstackConfigAction,
    PluginAction,
    ProvisioningAction,
    RedeployChangesAction,
    ReleaseAction,
    ResetAction,
    RoleAction,
    SettingsAction,
    SnapshotAction,
    StopAction,
    TokenAction,
    UserAction,
    VIPAction,
)

actions = dict(
    (action.action_name, action())
    for action in actions_tuple
)
