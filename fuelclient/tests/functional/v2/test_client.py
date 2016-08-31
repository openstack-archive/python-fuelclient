# -*- coding: utf-8 -*-
#
#    Copyright 2013-2014 Mirantis, Inc.
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

from fuelclient.tests.functional import base


class TestDeployChanges(base.CLIv2TestCase):

    cmd_create_env = "env create -r {0} cluster-test"
    cmd_add_node = "env add nodes -e 1 -n 1 -r controller"
    cmd_deploy_changes = "env deploy 1"
    cmd_redeploy_changes = "env redeploy 1"

    pattern_success = (r"^Deployment task with id (\d{1,}) "
                       r"for the environment 1 has been started.\n$")

    def setUp(self):
        super(TestDeployChanges, self).setUp()
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.cmd_create_env = self.cmd_create_env.format(release_id)
        self.run_cli_commands((
            self.cmd_create_env,
            self.cmd_add_node
        ))

    def test_deploy_changes(self):
        self.check_for_stdout_by_regexp(self.cmd_deploy_changes,
                                        self.pattern_success)

    def test_redeploy_changes(self):
        result = self.check_for_stdout_by_regexp(self.cmd_deploy_changes,
                                                 self.pattern_success)
        task_id = result.group(1)
        self.wait_task_ready(task_id)

        self.check_for_stdout_by_regexp(self.cmd_redeploy_changes,
                                        self.pattern_success)


class TestExtensionManagement(base.CLIv2TestCase):

    cmd_create_env = "env create -r {0} cluster-test-extensions-mgmt"
    cmd_disable_exts = "env extension disable 1 --extensions volume_manager"
    cmd_enable_exts = "env extension enable 1 --extensions volume_manager"

    pattern_enable_success = (r"^The following extensions: volume_manager "
                              r"have been enabled for the environment with "
                              r"id 1.\n$")
    pattern_disable_success = (r"^The following extensions: volume_manager "
                               r"have been disabled for the environment with "
                               r"id 1.\n$")

    def setUp(self):
        super(TestExtensionManagement, self).setUp()
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.cmd_create_env = self.cmd_create_env.format(release_id)
        self.run_cli_commands((
            self.cmd_create_env,
        ))

    def test_disable_extensions(self):
        self.check_for_stdout_by_regexp(self.cmd_disable_exts,
                                        self.pattern_disable_success)

    def test_enable_extensions(self):
        self.check_for_stdout_by_regexp(self.cmd_enable_exts,
                                        self.pattern_enable_success)
