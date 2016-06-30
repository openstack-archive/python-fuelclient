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

import os
import tempfile

from fuelclient.tests.functional import base


class TestHandlers(base.CLIv1TestCase):

    def test_env_action(self):
        # check env help
        help_msgs = ["usage: fuel environment [-h]",
                     "[--list | --set | --delete | --create]",
                     "optional arguments:", "--help", "--list", "--set",
                     "--delete", "--rel", "--env-create",
                     "--create", "--name", "--env-name", "--nst",
                     "--net-segment-type"]
        self.check_all_in_msg("env --help", help_msgs)
        # no clusters
        self.check_for_rows_in_table("env")

        for action in ("set", "create", "delete"):
            self.check_if_required("env {0}".format(action))

        release_id = self.get_first_deployable_release_id()

        # list of tuples (<fuel CLI command>, <expected output of a command>)
        expected_stdout = \
            [(
                "env --create --name=TestEnv --release={0}".format(release_id),
                "Environment 'TestEnv' with id=1 was created!\n"
            ), (
                "--env-id=1 env set --name=NewEnv",
                ("Following attributes are changed for "
                 "the environment: name=NewEnv\n")
            )]

        for cmd, msg in expected_stdout:
            self.check_for_stdout(cmd, msg)

    def test_node_action(self):
        help_msg = ["fuel node [-h] [--env ENV]",
                    "[--list | --set | --delete | --attributes |"
                    " --network | --disk | --deploy |"
                    " --hostname HOSTNAME | --name NAME |"
                    " --delete-from-db | --provision]", "-h", "--help", " -s",
                    "--default", " -d", "--download", " -u",
                    "--upload", "--dir", "--node", "--node-id", " -r",
                    "--role", "--net", "--hostname", "--name"]
        self.check_all_in_msg("node --help", help_msg)

        self.check_for_rows_in_table("node")

        for action in ("set", "remove", "--network", "--disk"):
            self.check_if_required("node {0}".format(action))

        self.load_data_to_nailgun_server()
        self.check_number_of_rows_in_table("node --node 9f:b6,9d:24,ab:aa", 3)

    def test_selected_node_provision(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 1 --role=controller"
        ))
        cmd = "--env-id=1 node --provision --node=1"
        msg = "Started provisioning nodes [1].\n"

        self.check_for_stdout(cmd, msg)

    def test_help_works_without_connection(self):
        fake_config = 'SERVER_ADDRESS: "333.333.333.333"'

        c_handle, c_path = tempfile.mkstemp(suffix='.json', text=True)
        with open(c_path, 'w') as f:
            f.write(fake_config)

        env = os.environ.copy()
        env['FUELCLIENT_CUSTOM_SETTINGS'] = c_path

        try:
            result = self.run_cli_command("--help", env=env)
            self.assertEqual(result.return_code, 0)
        finally:
            os.remove(c_path)

    def test_error_when_destroying_online_node(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 1 --role=controller"
        ), check_errors=False)
        msg = ("Nodes with ids [1] cannot be deleted from cluster because "
               "they are online. You might want to use the --force option.\n")
        self.check_for_stderr(
            "node --node 1 --delete-from-db",
            msg,
            check_errors=False
        )

    def test_force_destroy_online_node(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 1 --role=controller"
        ))
        msg = ("Nodes with ids [1] have been deleted from Fuel db.\n")
        self.check_for_stdout(
            "node --node 1 --delete-from-db --force",
            msg
        )

    def test_destroy_offline_node(self):

        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        node_id = 4
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node {0} --role=controller".format(node_id)
        ))
        msg = ("Nodes with ids [{0}] have been deleted from Fuel db.\n".format(
            node_id))
        self.check_for_stdout(
            "node --node {0} --delete-from-db".format(node_id),
            msg
        )

    def test_node_change_hostname(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 2 --role=controller"
        ))
        msg = "Hostname for node with id 2 has been changed to test-name.\n"
        self.check_for_stdout(
            "node --node 2 --hostname test-name",
            msg
        )

    def test_env_create_neutron_tun(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.check_for_stdout(
            "env create --name=NewEnv --release={0} --nst=tun"
            .format(release_id),
            "Environment 'NewEnv' with id=1 was created!\n")

    def test_destroy_multiple_nodes(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 1 2 --role=controller"
        ))
        msg = ("Nodes with ids [1, 2] have been deleted from Fuel db.\n")
        self.check_for_stdout(
            "node --node 1 2 --delete-from-db --force",
            msg
        )

    def test_for_examples_in_action_help(self):
        actions = (
            "node", "stop", "deployment", "reset", "network",
            "settings", "provisioning", "environment", "deploy-changes",
            "role", "release", "snapshot", "health", "vip"
        )
        for action in actions:
            self.check_all_in_msg("{0} -h".format(action), ("Examples",))

    def test_get_release_list_without_errors(self):
        cmd = 'release --list'
        self.run_cli_command(cmd)

    def test_reassign_node_group(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0} --nst=gre"
            .format(release_id),
            "--env-id=1 node set --node 1 2 --role=controller",
            "nodegroup --create --env 1 --name 'new group'"
        ))
        msg = ['PUT http://127.0.0.1',
               '/api/v1/nodes/ data=',
               '"id": 1',
               '"group_id": 2']
        self.check_all_in_msg(
            "nodegroup --assign --group 2 --node 1 --debug",
            msg
        )

    def test_node_group_creation_prints_warning_w_seg_type_vlan(self):
        warn_msg = ("WARNING: In VLAN segmentation type, there will be no "
                    "connectivity over private network between instances "
                    "running on hypervisors in different segments and that "
                    "it's a user's responsibility to handle this "
                    "situation.")

        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0} --nst=vlan"
            .format(release_id),

        ))
        self.check_for_stderr(
            "nodegroup create --name tor1 --env 1",
            warn_msg,
            check_errors=False
        )

    def test_create_network_group_fails_w_duplicate_name(self):
        err_msg = ("(Network with name storage already exists "
                   "in node group default)\n")
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0} --nst=gre"
            .format(release_id),
        ))
        self.check_for_stderr(
            ("network-group --create --name storage --node-group 1 "
             "--vlan 10 --cidr 10.0.0.0/24"),
            err_msg,
            check_errors=False
        )

    def test_create_network_group_fails_w_invalid_group(self):
        err_msg = "(Node group with ID 997755 does not exist)\n"

        self.check_for_stderr(
            ("network-group --create --name test --node-group 997755 "
             "--vlan 10 --cidr 10.0.0.0/24"),
            err_msg,
            check_errors=False
        )


class TestCharset(base.CLIv1TestCase):

    def test_charset_problem(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=привет --release={0}".format(release_id),
            "--env-id=1 node set --node 1 --role=controller",
            "env"
        ))


class TestFiles(base.CLIv1TestCase):

    def test_file_creation(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 1 --role=controller",
            "--env-id=1 node set --node 2,3 --role=compute"
        ))
        for action in ("network", "settings"):
            for format_ in ("yaml", "json"):
                self.check_if_files_created(
                    "--env 1 {0} --download --{1}".format(action, format_),
                    ("{0}_1.{1}".format(action, format_),)
                )
        command_to_files_map = (
            (
                "--env 1 deployment --default",
                (
                    "deployment_1",
                    "deployment_1/1.yaml",
                    "deployment_1/2.yaml",
                    "deployment_1/3.yaml"
                )
            ),
            (
                "--env 1 provisioning --default",
                (
                    "provisioning_1",
                    "provisioning_1/engine.yaml",
                    "provisioning_1/node-1.yaml",
                    "provisioning_1/node-2.yaml",
                    "provisioning_1/node-3.yaml"
                )
            ),
            (
                "--env 1 deployment --default --json",
                (
                    "deployment_1/1.json",
                    "deployment_1/2.json",
                    "deployment_1/3.json"
                )
            ),
            (
                "--env 1 provisioning --default --json",
                (
                    "provisioning_1/engine.json",
                    "provisioning_1/node-1.json",
                    "provisioning_1/node-2.json",
                    "provisioning_1/node-3.json"
                )
            ),
            (
                "node --node 1 --disk --default",
                (
                    "node_1",
                    "node_1/disks.yaml"
                )
            ),
            (
                "node --node 1 --network --default",
                (
                    "node_1",
                    "node_1/interfaces.yaml"
                )
            ),
            (
                "node --node 1 --disk --default --json",
                (
                    "node_1/disks.json",
                )
            ),
            (
                "node --node 1 --network --default --json",
                (
                    "node_1/interfaces.json",
                )
            )
        )
        for command, files in command_to_files_map:
            self.check_if_files_created(command, files)

    def check_if_files_created(self, command, paths):
        command_in_dir = "{0} --dir={1}".format(command, self.temp_directory)
        self.run_cli_command(command_in_dir)
        for path in paths:
            self.assertTrue(os.path.exists(
                os.path.join(self.temp_directory, path)
            ))


class TestDownloadUploadNodeAttributes(base.CLIv1TestCase):

    def test_upload_download_interfaces(self):
        self.load_data_to_nailgun_server()

        release_id = self.get_first_deployable_release_id()
        env_create = "env create --name=test --release={0}".format(release_id)
        add_node = "--env-id=1 node set --node 1 --role=controller"

        cmd = "node --node-id 1 --network"
        self.run_cli_commands((env_create,
                              add_node,
                              self.download_command(cmd),
                              self.upload_command(cmd)))

    def test_upload_download_disks(self):
        self.load_data_to_nailgun_server()
        cmd = "node --node-id 1 --disk"
        self.run_cli_commands((self.download_command(cmd),
                              self.upload_command(cmd)))


class TestDeployChanges(base.CLIv1TestCase):

    cmd_create_env = "env create --name=test --release={0}"
    cmd_add_node = "--env-id=1 node set --node 1 --role=controller"
    cmd_deploy_changes = "deploy-changes --env 1"
    cmd_redeploy_changes = "redeploy-changes --env 1"

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


class TestDirectoryDoesntExistErrorMessages(base.CLIv1TestCase):

    def test_settings_upload(self):
        self.check_for_stderr(
            "settings --upload --dir /foo/bar/baz --env 1",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_deployment_upload(self):
        self.check_for_stderr(
            "deployment --upload --dir /foo/bar/baz --env 1",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_net_upload(self):
        self.check_for_stderr(
            "network --upload --dir /foo/bar/baz --env 1",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_env_download(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 2 --role=controller"
        ))
        self.check_for_stderr(
            "network --download --dir /foo/bar/baz --env 1",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_download_network_configuration(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 2 --role=controller"
        ))
        self.check_for_stderr(
            "--env 1 network --download --dir /foo/bar/baz",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_download_default_settings(self):
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.run_cli_commands((
            "env create --name=NewEnv --release={0}".format(release_id),
            "--env-id=1 node set --node 2 --role=controller"
        ))
        self.check_for_stderr(
            "--env 1 settings --default --dir /foo/bar/baz",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_upload_network_configuration(self):
        self.check_for_stderr(
            "--env 1 network --upload --dir /foo/bar/baz",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )

    def test_upload_network_template(self):
        self.check_for_stderr(
            "--env 1 network-template --upload --dir /foo/bar/baz",
            "Directory '/foo/bar/baz' doesn't exist.\n",
            check_errors=False
        )


class TestUploadSettings(base.CLIv1TestCase):

    create_env = "env create --name=test --release={0}"
    add_node = "--env-id=1 node set --node 1 --role=controller"
    deploy_changes = "deploy-changes --env 1"
    cmd = "settings --env 1"
    cmd_force = "settings --env 1 --force"

    def setUp(self):
        super(TestUploadSettings, self).setUp()
        self.load_data_to_nailgun_server()
        release_id = self.get_first_deployable_release_id()
        self.create_env = self.create_env.format(release_id)
        self.run_cli_commands((
            self.create_env,
            self.add_node,
            self.download_command(self.cmd)
        ))

    def test_upload_settings(self):
        msg_success = "Settings configuration uploaded.\n"
        self.check_for_stdout(self.upload_command(self.cmd),
                              msg_success)
