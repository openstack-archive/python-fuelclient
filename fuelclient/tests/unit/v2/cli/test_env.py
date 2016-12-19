# -*- coding: utf-8 -*-
#
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


import json
import mock
import yaml

from six import moves

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_env
from fuelclient.tests.utils import fake_task
from fuelclient.v1 import environment


class TestEnvCommand(test_engine.BaseCLITest):
    """Tests for fuel2 env * commands."""

    def setUp(self):
        super(TestEnvCommand, self).setUp()

        self.m_client.get_all.return_value = [fake_env.get_fake_env()
                                              for i in range(10)]
        self.m_client.get_by_id.return_value = fake_env.get_fake_env()
        self.m_client.create.return_value = fake_env.get_fake_env()
        self.m_client.update.return_value = fake_env.get_fake_env()

    def test_env_list(self):
        args = 'env list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_env_list_sorted(self):
        args = 'env list -s name'
        self.exec_command(args)
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_env_show(self):
        args = 'env show 42'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(42)

    def test_env_create(self):
        args = 'env create -r 1 -nst gre env42'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)

        m_client = self.m_client
        m_client.create.assert_called_once_with(name='env42',
                                                release_id=1,
                                                net_segment_type='gre')

    def test_neutron_gre_deprecation_warning(self):
        args = 'env create -r 1 -nst gre env42'

        with mock.patch('sys.stderr', new=moves.cStringIO()) as m_stderr:
            self.exec_command(args)
            self.assertIn(
                "WARNING: GRE network segmentation type is deprecated "
                "since 7.0 release",
                m_stderr.getvalue()
            )

    def test_env_delete(self):
        args = 'env delete --force 42'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.delete_by_id.assert_called_once_with(42)

    def test_env_delete_wo_force(self):
        args = 'env delete 42'

        env = fake_env.get_fake_env(status='operational')
        self.m_client.get_by_id.return_value = env

        with mock.patch('sys.stdout', new=moves.cStringIO()) as m_stdout:
            self.exec_command(args)
            self.assertIn('--force', m_stdout.getvalue())

    def test_env_deploy(self):
        dry_run = False
        noop_run = False
        args = 'env deploy'

        args += ' 42'

        self.exec_command(args)

        calls = list()
        calls.append(mock.call.deploy_changes(42,
                                              noop_run=noop_run,
                                              dry_run=dry_run))

        self.m_get_client.assert_called_with('environment', mock.ANY)
        self.m_client.assert_has_calls(calls)

    def test_env_deploy_dry_run(self):
        dry_run = True
        noop_run = False

        args = 'env deploy -d'
        args += ' 42'

        self.exec_command(args)

        calls = list()
        calls.append(mock.call.deploy_changes(42,
                                              noop_run=noop_run,
                                              dry_run=dry_run))

        self.m_get_client.assert_called_with('environment', mock.ANY)
        self.m_client.assert_has_calls(calls)

    def test_env_deploy_noop_run(self):
        dry_run = False
        noop_run = True

        args = 'env deploy --noop'
        args += ' 42'

        self.exec_command(args)

        calls = list()
        calls.append(mock.call.deploy_changes(42,
                                              noop_run=noop_run,
                                              dry_run=dry_run))

        self.m_get_client.assert_called_with('environment', mock.ANY)
        self.m_client.assert_has_calls(calls)

    def test_env_redeploy(self):
        dry_run = False
        noop_run = False
        args = 'env redeploy'

        args += ' 42'

        self.exec_command(args)

        calls = list()
        calls.append(mock.call.redeploy_changes(42,
                                                noop_run=noop_run,
                                                dry_run=dry_run))

        self.m_get_client.assert_called_with('environment', mock.ANY)
        self.m_client.assert_has_calls(calls)

    def test_env_redeploy_dry_run(self):
        dry_run = True
        noop_run = False
        args = 'env redeploy -d'

        args += ' 42'

        self.exec_command(args)

        calls = list()
        calls.append(mock.call.redeploy_changes(42,
                                                noop_run=noop_run,
                                                dry_run=dry_run))

        self.m_get_client.assert_called_with('environment', mock.ANY)
        self.m_client.assert_has_calls(calls)

    def test_env_redeploy_noop_run(self):
        dry_run = False
        noop_run = True
        args = 'env redeploy --noop'

        args += ' 42'

        self.exec_command(args)

        calls = list()
        calls.append(mock.call.redeploy_changes(42,
                                                noop_run=noop_run,
                                                dry_run=dry_run))

        self.m_get_client.assert_called_with('environment', mock.ANY)
        self.m_client.assert_has_calls(calls)

    def test_env_reset(self):
        env_id = 45
        args = 'env reset {env_id}'.format(env_id=env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.reset.assert_called_once_with(env_id, force=False)

    def test_env_reset_force(self):
        env_id = 45
        args = 'env reset {env_id} --force'.format(env_id=env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.reset.assert_called_once_with(env_id, force=True)

    def test_env_add_nodes(self):
        args = 'env add nodes -e 42 -n 24 25 -r compute cinder'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.add_nodes.assert_called_once_with(environment_id=42,
                                                        nodes=[24, 25],
                                                        roles=['compute',
                                                               'cinder'])

    def test_env_remove_nodes_by_id(self):
        args = 'env remove nodes -e 42 -n 24 25'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.remove_nodes.assert_called_once_with(environment_id=42,
                                                           nodes=[24, 25])

    def test_env_remove_nodes_all(self):
        args = 'env remove nodes -e 42 --nodes-all'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.remove_nodes.assert_called_once_with(environment_id=42,
                                                           nodes=None)

    def test_env_update(self):
        self.m_client._updatable_attributes = \
            environment.EnvironmentClient._updatable_attributes

        args = 'env update -n test_name 42'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.update.assert_called_once_with(environment_id=42,
                                                     name='test_name')

    def test_env_spawn_vms(self):
        env_id = 10
        args = 'env spawn-vms {0}'.format(env_id)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.spawn_vms.assert_called_once_with(env_id)

    def test_env_nodes_deploy(self):
        env_id = 42
        node_ids = [43, 44]
        noop_run = False
        args = ('env nodes deploy '
                '--nodes {n[0]} {n[1]} --env {e}').format(e=env_id, n=node_ids)

        self.exec_command(args)

        self.m_client.deploy_nodes.return_value = fake_task.get_fake_task()
        self.m_client.deploy_nodes.assert_called_once_with(env_id, node_ids,
                                                           force=False,
                                                           noop_run=noop_run)

    def test_env_nodes_deploy_force(self):
        env_id = 42
        node_ids = [43, 44]
        force = True
        noop_run = False
        args = ('env nodes deploy --force '
                '--nodes {n[0]} {n[1]} --env {e}').format(e=env_id, n=node_ids)

        self.exec_command(args)

        self.m_client.deploy_nodes.return_value = fake_task.get_fake_task()
        self.m_client.deploy_nodes.assert_called_once_with(env_id, node_ids,
                                                           noop_run=noop_run,
                                                           force=force)

    def test_env_nodes_deploy_noop_run(self):
        env_id = 42
        node_ids = [43, 44]
        force = False
        noop_run = True
        args = ('env nodes deploy --noop '
                '--nodes {n[0]} {n[1]} --env {e}').format(e=env_id, n=node_ids)

        self.exec_command(args)

        self.m_client.deploy_nodes.return_value = fake_task.get_fake_task()
        self.m_client.deploy_nodes.assert_called_once_with(env_id, node_ids,
                                                           force=force,
                                                           noop_run=noop_run)

    def test_env_nodes_provision(self):
        env_id = 42
        node_ids = [43, 44]
        args = ('env nodes provision '
                '--nodes {n[0]} {n[1]} --env {e}').format(e=env_id, n=node_ids)

        self.m_client.provision_nodes.return_value = fake_task.get_fake_task()

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.provision_nodes.assert_called_once_with(env_id, node_ids)

    def test_env_stop(self):
        env_id = 45
        args = 'env stop-deployment {env_id}'.format(env_id=env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.stop.assert_called_once_with(env_id)

    def test_env_network_verify(self):
        env_id = 42
        args = 'env network verify {}'.format(env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.verify_network.assert_called_once_with(env_id)

    @mock.patch('json.dump')
    def test_env_network_download_json(self, m_dump):
        args = 'env network download --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/network.json'

        self.m_client.get_network_configuration.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_network_configuration.assert_called_once_with(42)

    def test_env_network_upload_json(self):
        args = 'env network upload --format json -d /tmp 42'
        config = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/network.json'

        m_open = mock.mock_open(read_data=json.dumps(config))
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.set_network_configuration.assert_called_once_with(42,
                                                                        config)

    @mock.patch('yaml.safe_dump')
    def test_env_network_download_yaml(self, m_safe_dump):
        args = 'env network download --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/network.yaml'

        self.m_client.get_network_configuration.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_network_configuration.assert_called_once_with(42)

    def test_env_network_upload_yaml(self):
        args = 'env network upload --format yaml -d /tmp 42'
        config = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/network.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(config))
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.set_network_configuration.assert_called_once_with(42,
                                                                        config)

    @mock.patch('json.dump')
    def test_env_settings_download_json(self, m_dump):
        args = 'env settings download --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/settings.json'

        self.m_client.get_settings.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_settings.assert_called_once_with(42)

    def test_env_settings_upload_json(self):
        args = 'env settings upload --format json -d /tmp 42'
        config = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/settings.json'

        m_open = mock.mock_open(read_data=json.dumps(config))
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.set_settings.assert_called_once_with(42,
                                                           config,
                                                           force=False)

    @mock.patch('yaml.safe_dump')
    def test_env_settings_download_yaml(self, m_safe_dump):
        args = 'env settings download --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/settings.yaml'

        self.m_client.get_settings.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.get_settings.assert_called_once_with(42)

    def test_env_settings_upload_yaml(self):
        args = 'env settings upload --format yaml -d /tmp 42'
        config = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/settings.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(config))
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.set_settings.assert_called_once_with(42,
                                                           config,
                                                           force=False)

    def test_env_settings_upload_force(self):
        args = 'env settings upload --format yaml -d /tmp --force 42'
        config = {'foo': 'bar'}
        expected_path = '/tmp/environment_42/settings.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(config))
        with mock.patch('fuelclient.commands.environment.open',
                        m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.set_settings.assert_called_once_with(42,
                                                           config,
                                                           force=True)

    def test_env_deployment_facts_delete(self):
        args = "env deployment-facts delete 42"
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.delete_facts.assert_called_once_with(42, 'deployment')

    def test_env_provisioning_facts_delete(self):
        args = "env provisioning-facts delete 42"
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.delete_facts.assert_called_once_with(42, 'provisioning')

    @mock.patch('json.dump')
    def _deployment_facts_download_json(self, m_dump, default=False):
        command = 'get-default' if default else 'download'
        args = (
            "env deployment-facts {}"
            " --env 42 --dir /tmp --nodes 2 --format json --no-split"
            .format(command)
        )
        data = [{'uid': 2, 'name': 'node'}]
        expected_path = '/tmp/deployment_42/2.json'

        self.m_client.download_facts.return_value = data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.common.data_utils.open',
                        m_open, create=True):
            self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.download_facts.assert_called_once_with(
            42, 'deployment', nodes=[2], default=default, split=False)
        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(data[0], mock.ANY, indent=4)

    def test_env_deployment_facts_download_json(self):
        self._deployment_facts_download_json(default=False)

    def test_env_deployment_facts_get_default_json(self):
        self._deployment_facts_download_json(default=True)

    @mock.patch('yaml.safe_dump')
    def _deployment_facts_download_yaml(self, m_safe_dump, default=False):
        command = 'get-default' if default else 'download'
        args = (
            "env deployment-facts {}"
            " --env 42 --dir /tmp --nodes 2 --format yaml"
            .format(command)
        )
        data = [{'uid': 2, 'name': 'node'}]
        expected_path = '/tmp/deployment_42/2.yaml'

        self.m_client.download_facts.return_value = data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.common.data_utils.open',
                        m_open, create=True):
            self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.download_facts.assert_called_once_with(
            42, 'deployment', nodes=[2], default=default, split=True)
        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(data[0], mock.ANY,
                                            default_flow_style=False)

    def test_env_deployment_facts_download_yaml(self):
        self._deployment_facts_download_yaml(default=False)

    def test_env_deployment_facts_get_default_yaml(self):
        self._deployment_facts_download_yaml(default=True)

    def test_env_deployment_facts_upload_json(self):
        args = 'env deployment-facts upload --env 42 --dir /tmp --format json'
        data = [{'uid': 2, 'name': 'node'}]
        expected_path = '/tmp/deployment_42/2.json'

        m_open = mock.mock_open(read_data=json.dumps(data[0]))
        with mock.patch('os.listdir', return_value=['2.json']):
            with mock.patch('fuelclient.common.data_utils.open',
                            m_open, create=True):
                self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        m_open.assert_called_once_with(expected_path, 'r')
        self.m_client.upload_facts.assert_called_once_with(
            42, 'deployment', data)

    def test_env_deployment_facts_upload_yaml(self):
        args = 'env deployment-facts upload --env 42 --dir /tmp --format yaml'
        data = [{'uid': 2, 'name': 'node'}]
        expected_path = '/tmp/deployment_42/2.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(data[0]))
        with mock.patch('os.listdir', return_value=['2.yaml']):
            with mock.patch('fuelclient.common.data_utils.open',
                            m_open, create=True):
                self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        m_open.assert_called_once_with(expected_path, 'r')
        self.m_client.upload_facts.assert_called_once_with(
            42, 'deployment', data)

    @mock.patch('json.dump')
    def _provisioning_facts_download_json(self, m_dump, default=False):
        command = 'get-default' if default else 'download'
        args = "env provisioning-facts {}" \
               " --env 42 --dir /tmp --nodes 2 --format json".format(command)
        data = {
            'engine': {'foo': 'bar'},
            'nodes': [{'uid': 2, 'name': 'node-2'}]
        }
        expected_path_engine = '/tmp/provisioning_42/engine.json'
        expected_path_node = '/tmp/provisioning_42/2.json'

        self.m_client.download_facts.return_value = data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.common.data_utils.open',
                        m_open, create=True):
            self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.download_facts.assert_called_once_with(
            42, 'provisioning', nodes=[2], default=default, split=True)
        m_open.assert_any_call(expected_path_engine, 'w')
        m_dump.assert_any_call(data['engine'], mock.ANY, indent=4)
        m_open.assert_any_call(expected_path_node, 'w')
        m_dump.assert_any_call(data['nodes'][0], mock.ANY, indent=4)

    def test_env_provisioning_facts_download_json(self):
        self._provisioning_facts_download_json(default=False)

    def test_env_provisioning_facts_get_default_json(self):
        self._provisioning_facts_download_json(default=True)

    @mock.patch('yaml.safe_dump')
    def _provisioning_facts_download_yaml(self, m_dump, default=False):
        command = 'get-default' if default else 'download'
        args = "env provisioning-facts {}" \
               " --env 42 --dir /tmp --nodes 2 --format yaml".format(command)
        data = {
            'engine': {'foo': 'bar'},
            'nodes': [{'uid': 2, 'name': 'node-2'}]
        }
        expected_path_engine = '/tmp/provisioning_42/engine.yaml'
        expected_path_node = '/tmp/provisioning_42/2.yaml'

        self.m_client.download_facts.return_value = data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.common.data_utils.open',
                        m_open, create=True):
            self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        self.m_client.download_facts.assert_called_once_with(
            42, 'provisioning', nodes=[2], default=default, split=True)
        m_open.assert_any_call(expected_path_engine, 'w')
        m_dump.assert_any_call(data['engine'], mock.ANY,
                               default_flow_style=False)
        m_open.assert_any_call(expected_path_node, 'w')
        m_dump.assert_any_call(data['nodes'][0], mock.ANY,
                               default_flow_style=False)

    def test_env_provisioning_facts_download_yaml(self):
        self._provisioning_facts_download_yaml(default=False)

    def test_env_provisioning_facts_get_default_yaml(self):
        self._provisioning_facts_download_yaml(default=True)

    def test_env_provisioning_facts_upload_json(self):
        args = 'env provisioning-facts upload' \
               ' --env 42 --dir /tmp --format json'
        expected_data = {
            'engine': {'foo': 'bar'},
            'nodes': [{'foo': 'bar'}]
        }
        expected_path_engine = '/tmp/provisioning_42/engine.json'
        expected_path_node = '/tmp/provisioning_42/2.json'

        m_open = mock.mock_open(read_data=json.dumps({'foo': 'bar'}))
        with mock.patch('os.listdir', return_value=['engine.json', '2.json']):
            with mock.patch('fuelclient.common.data_utils.open',
                            m_open, create=True):
                with mock.patch('os.path.lexists', return_value=True):
                    self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        m_open.assert_any_call(expected_path_engine, 'r')
        m_open.assert_any_call(expected_path_node, 'r')
        self.m_client.upload_facts.assert_called_once_with(
            42, 'provisioning', expected_data)

    def test_env_provisioning_facts_upload_yaml(self):
        args = 'env provisioning-facts upload' \
               ' --env 42 --dir /tmp --format yaml'
        expected_data = {
            'engine': {'foo': 'bar'},
            'nodes': [{'foo': 'bar'}]
        }
        expected_path_engine = '/tmp/provisioning_42/engine.yaml'
        expected_path_node = '/tmp/provisioning_42/2.yaml'

        m_open = mock.mock_open(read_data=json.dumps({'foo': 'bar'}))
        with mock.patch('os.listdir', return_value=['engine.yaml', '2.yaml']):
            with mock.patch('fuelclient.common.data_utils.open',
                            m_open, create=True):
                with mock.patch('os.path.lexists', return_value=True):
                    self.exec_command(args)

        self.m_get_client.assert_called_once_with('environment', mock.ANY)
        m_open.assert_any_call(expected_path_engine, 'r')
        m_open.assert_any_call(expected_path_node, 'r')
        self.m_client.upload_facts.assert_called_once_with(
            42, 'provisioning', expected_data)
