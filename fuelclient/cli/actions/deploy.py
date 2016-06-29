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
import six

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.objects.environment import Environment


class ChangesAction(Action):

    action_name = None
    actions_func_map = {}

    def __init__(self):
        super(ChangesAction, self).__init__()
        self.args = (
            Args.get_env_arg(required=True),
            Args.get_dry_run_deployment_arg(),
        )
        self.flag_func_map = (
            (None, self.deploy_changes),
        )

    def print_deploy_info(self, deploy_task):
        six.print_("Deployment task with id {t} for the environment {e} "
                   "has been started.".format(t=deploy_task.id,
                                              e=deploy_task.env.id)
                   )

    def deploy_changes(self, params):
        """To apply all changes to some environment:
            fuel --env 1 {action_name}
        """
        env = Environment(params.env)

        deploy_task = getattr(
            env, self.actions_func_map[self.action_name])(
            dry_run=params.dry_run)
        self.serializer.print_to_output(
            deploy_task.data,
            deploy_task,
            print_method=self.print_deploy_info)


class DeployChangesAction(ChangesAction):
    """Deploy changes to environments
    """
    action_name = "deploy-changes"

    def __init__(self):
        super(DeployChangesAction, self).__init__()
        self.actions_func_map[self.action_name] = 'deploy_changes'


class RedeployChangesAction(ChangesAction):
    """Redeploy changes to environment which is in the operational state
    """
    action_name = "redeploy-changes"

    def __init__(self):
        super(RedeployChangesAction, self).__init__()
        self.actions_func_map[self.action_name] = 'redeploy_changes'
