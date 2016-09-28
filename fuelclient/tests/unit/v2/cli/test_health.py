# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

import mock

from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_health


class TestHealthCommand(test_engine.BaseCLITest):
    """Tests for fuel2 health * commands."""

    def test_health_list_for_cluster(self):
        self.m_client.get_all.return_value = fake_health.get_fake_test_sets(10)
        cluster_id = 45
        args = 'health list -e {id}'.format(id=cluster_id)
        self.exec_command(args)
        self.m_client.get_all.assert_called_once_with(
            environment_id=cluster_id)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    @mock.patch('sys.stderr')
    def test_health_list_for_cluster_fail(self, mocked_stderr):
        args = 'health list'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_health_status_list(self):
        self.m_client.get_status_all.return_value = [
            fake_health.get_fake_test_set_item(testset_id=12, cluster_id=30),
            fake_health.get_fake_test_set_item(testset_id=13, cluster_id=32),
            fake_health.get_fake_test_set_item(testset_id=14, cluster_id=35)
        ]
        args = 'health status list'
        self.exec_command(args)
        self.m_client.get_status_all.assert_called_once_with(None)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    def test_health_status_list_for_cluster(self):
        cluster_id = 45
        self.m_client.get_status_all.return_value = [
            fake_health.get_fake_test_set_item(testset_id=12,
                                               cluster_id=cluster_id),
            fake_health.get_fake_test_set_item(testset_id=13,
                                               cluster_id=cluster_id),
            fake_health.get_fake_test_set_item(testset_id=14,
                                               cluster_id=cluster_id)
        ]
        args = 'health status list -e {id}'.format(id=cluster_id)
        self.exec_command(args)
        self.m_client.get_status_all.assert_called_once_with(cluster_id)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    def test_health_status_show(self):
        testset_id = 66
        self.m_client.get_status_single.return_value = \
            fake_health.get_fake_test_set_item(testset_id=testset_id)
        args = 'health status show {id}'.format(id=testset_id)
        self.exec_command(args)
        self.m_client.get_status_single.assert_called_once_with(testset_id)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    @mock.patch('sys.stderr')
    def test_health_status_show_fail(self, mocked_stderr):
        args = 'health status show'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('id', mocked_stderr.write.call_args_list[0][0][0])

    def test_health_start_force(self):
        cluster_id = 45
        testset = ['fake_test_set1', 'fake_test_set2']
        args = 'health start -e {id} -t {testset} --force'.format(
            id=cluster_id, testset=' '.join(testset))
        self.exec_command(args)
        self.m_client.start.assert_called_once_with(cluster_id,
                                                    ostf_credentials={},
                                                    test_sets=testset,
                                                    force=True)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    @mock.patch('sys.stderr')
    def test_health_start_w_wrong_parameters(self, mocked_stderr):
        args = 'health start'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('-e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])

    def test_health_start_wo_force(self):
        cluster_id = 45
        testset = ['fake_test_set1', 'fake_test_set2']
        args = 'health start -e {id} -t {testset}'.format(
            id=cluster_id, testset=' '.join(testset))
        self.exec_command(args)
        self.m_client.start.assert_called_once_with(cluster_id,
                                                    ostf_credentials={},
                                                    test_sets=testset,
                                                    force=False)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    def test_health_start_all_wo_force(self):
        cluster_id = 45
        args = 'health start -e {id}'.format(id=cluster_id)
        self.exec_command(args)
        self.m_client.start.assert_called_once_with(cluster_id,
                                                    ostf_credentials={},
                                                    test_sets=None,
                                                    force=False)
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    def test_health_start_force_w_ostf_credentials(self):
        cluster_id = 45
        testset = ['fake_test_set1', 'fake_test_set2']
        ostf_credentials = {'username': 'fake_user',
                            'password': 'fake_password',
                            'tenant': 'fake_tenant_name'}

        args = ('health start -e {id} -t {testset} --force --ostf-username '
                'fake_user --ostf-password fake_password --ostf-tenant-name '
                'fake_tenant_name'.format(id=cluster_id,
                                          testset=' '.join(testset)))

        self.exec_command(args)
        self.m_client.start.assert_called_once_with(
            cluster_id,
            ostf_credentials=ostf_credentials,
            test_sets=testset,
            force=True
        )
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    def test_health_stop(self):
        testset_id = 66
        args = 'health stop {id}'.format(id=testset_id)
        self.exec_command(args)
        self.m_client.action.assert_called_once_with(testset_id, 'stopped')
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    @mock.patch('sys.stderr')
    def test_health_stop_fail(self, mocked_stderr):
        args = 'health stop'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('id', mocked_stderr.write.call_args_list[0][0][0])

    def test_health_restart(self):
        testset_id = 66
        args = 'health restart {id}'.format(id=testset_id)
        self.exec_command(args)
        self.m_client.action.assert_called_once_with(testset_id, 'restarted')
        self.m_get_client.assert_called_once_with('health', mock.ANY)

    @mock.patch('sys.stderr')
    def test_health_restart_fail(self, mocked_stderr):
        args = 'health restart'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('id', mocked_stderr.write.call_args_list[0][0][0])
