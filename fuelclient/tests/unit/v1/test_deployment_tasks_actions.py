# -*- coding: utf-8 -*-
#
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

import os

from mock import patch
import requests_mock as rm

from fuelclient.tests.unit.v1 import base


API_INPUT = [{'id': 'primary-controller'}]
API_OUTPUT = '- id: primary-controller\n'
RELEASE_OUTPUT = [{'id': 1, 'version': '2014.2-6.0', 'name': 'Something'}]
MULTIPLE_RELEASES = [{'id': 1, 'version': '2014.2-6.0', 'name': 'Something'},
                     {'id': 2, 'version': '2014.3-6.1', 'name': 'Something'}]


@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestReleaseDeploymentTasksActions(base.UnitTestCase):

    def test_release_tasks_download(self, mos, mopen):
        self.m_request.get(rm.ANY, json=API_INPUT)
        self.execute(
            ['fuel', 'rel', '--rel', '1', '--deployment-tasks', '--download'])
        mopen().__enter__().write.assert_called_once_with(API_OUTPUT)

    def test_release_tasks_upload(self, mos, mopen):
        mopen().__enter__().read.return_value = API_OUTPUT
        put = self.m_request.put('/api/v1/releases/1/deployment_tasks',
                                 json=API_OUTPUT)

        self.execute(
            ['fuel', 'rel', '--rel', '1', '--deployment-tasks', '--upload'])

        self.assertTrue(put.called)
        self.assertEqual(put.last_request.json(), API_INPUT)


@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestClusterDeploymentTasksActions(base.UnitTestCase):

    def test_cluster_tasks_download(self, mos, mopen):
        self.m_request.get(rm.ANY, json=API_INPUT)
        self.execute(
            ['fuel', 'env', '--env', '1', '--deployment-tasks', '--download'])
        mopen().__enter__().write.assert_called_once_with(API_OUTPUT)

    def test_cluster_tasks_upload(self, mos, mopen):
        mopen().__enter__().read.return_value = API_OUTPUT
        put = self.m_request.put('/api/v1/clusters/1/deployment_tasks',
                                 json=API_OUTPUT)

        self.execute(
            ['fuel', 'env', '--env', '1', '--deployment-tasks', '--upload'])

        self.assertTrue(put.called)
        self.assertEqual(put.last_request.json(), API_INPUT)


@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.utils.iterfiles')
class TestSyncDeploymentTasks(base.UnitTestCase):

    def test_sync_deployment_scripts(self, mfiles, mopen):
        self.m_request.get(rm.ANY, json=RELEASE_OUTPUT)
        put = self.m_request.put('/api/v1/releases/1/deployment_tasks',
                                 json={})

        mfiles.return_value = ['/etc/puppet/2014.2-6.0/tasks.yaml']
        mopen().__enter__().read.return_value = API_OUTPUT
        file_pattern = '*tests*'
        self.execute(
            ['fuel', 'rel', '--sync-deployment-tasks', '--fp', file_pattern])

        mfiles.assert_called_once_with(
            os.path.realpath(os.curdir), file_pattern)

        self.assertTrue(put.called)
        self.assertEqual(put.last_request.json(), API_INPUT)

    @patch('fuelclient.cli.actions.release.os')
    def test_sync_with_directory_path(self, mos, mfiles, mopen):
        self.m_request.get(rm.ANY, json=RELEASE_OUTPUT)
        put = self.m_request.put('/api/v1/releases/1/deployment_tasks',
                                 json={})

        mos.path.realpath.return_value = real_path = '/etc/puppet'
        mfiles.return_value = [real_path + '/2014.2-6.0/tasks.yaml']
        mopen().__enter__().read.return_value = API_OUTPUT
        self.execute(
            ['fuel', 'rel', '--sync-deployment-tasks', '--dir', real_path])
        mfiles.assert_called_once_with(real_path, '*tasks.yaml')
        self.assertTrue(put.called)

    def test_multiple_tasks_but_one_release(self, mfiles, mopen):
        self.m_request.get(rm.ANY, json=RELEASE_OUTPUT)
        put = self.m_request.put(rm.ANY, json={})

        mfiles.return_value = ['/etc/puppet/2014.2-6.0/tasks.yaml',
                               '/etc/puppet/2014.3-6.1/tasks.yaml']
        mopen().__enter__().read.return_value = API_OUTPUT

        self.execute(
            ['fuel', 'rel', '--sync-deployment-tasks'])

        self.assertEqual(put.call_count, 1)

    def test_multiple_releases(self, mfiles, mopen):
        self.m_request.get(rm.ANY, json=MULTIPLE_RELEASES)
        put = self.m_request.put(rm.ANY, json={})
        mfiles.return_value = ['/etc/puppet/2014.2-6.0/tasks.yaml',
                               '/etc/puppet/2014.3-6.1/tasks.yaml']
        mopen().__enter__().read.return_value = API_OUTPUT

        self.execute(
            ['fuel', 'rel', '--sync-deployment-tasks'])

        self.assertEqual(put.call_count, 2)
