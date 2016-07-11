# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestReleaseFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestReleaseFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/releases/'.format(version=self.version)
        self.fake_releases = utils.get_fake_releases(10)
        self.fake_release_components = utils.get_fake_release_components(10)
        self.fake_attributes_metadata = utils.get_fake_attributes_metadata()
        self.client = fuelclient.get_client('release', self.version)

    def test_release_list(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_releases)
        self.client.get_all()
        self.assertTrue(matcher.called)

    def test_release_repos_list(self):
        release_id = 42
        expected_uri = self.get_object_uri(self.res_uri, release_id,
                                           '/attributes_metadata')
        matcher = self.m_request.get(expected_uri,
                                     json=self.fake_attributes_metadata)
        self.client.get_attributes_metadata_by_id(release_id)
        self.assertTrue(matcher.called)

    def test_release_repos_update(self):
        release_id = 42
        expected_uri = self.get_object_uri(self.res_uri, release_id,
                                           '/attributes_metadata')
        m_put = self.m_request.put(expected_uri,
                                   json=self.fake_attributes_metadata)

        m_open = mock.mock_open(read_data=self.fake_attributes_metadata)
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.update_attributes_metadata_by_id(
                release_id=release_id,
                data=self.fake_attributes_metadata
            )
        self.assertTrue(m_put.called)
        self.assertEqual(m_put.last_request.json(),
                         self.fake_attributes_metadata)

    def test_release_component_list(self):
        release_id = 42
        expected_uri = self.get_object_uri(self.res_uri, release_id,
                                           '/components')
        matcher = self.m_request.get(expected_uri,
                                     json=self.fake_release_components)
        self.client.get_components_by_id(release_id)
        self.assertTrue(matcher.called)
