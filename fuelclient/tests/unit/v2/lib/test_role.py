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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestRoleFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestRoleFacade, self).setUp()

        self.version = 'v1'
        self.role_name = 'fake_role'
        self.fake_role = utils.get_fake_role(self.role_name)
        self.fake_roles = utils.get_fake_roles(10)

        self.client = fuelclient.get_client('role', self.version)

    def get_uri(self, owner):
        return '/api/{version}/{owner}/'.format(version=self.version,
                                                owner=owner)

    def test_release_role_list(self):
        owner, owner_id = 'releases', 42
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/')
        matcher = self.m_request.get(expected_uri, json=self.fake_roles)
        self.client.get_all(owner, owner_id)

        self.assertTrue(matcher.called)

    def test_cluster_role_list(self):
        owner, owner_id = 'clusters', 42
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/')
        matcher = self.m_request.get(expected_uri, json=self.fake_roles)
        self.client.get_all(owner_type=owner, owner_id=owner_id)

        self.assertTrue(matcher.called)

    def test_release_role_download(self):
        owner, owner_id = 'releases', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/{}/'.format(self.role_name))
        role_matcher = self.m_request.get(expected_uri, json=self.fake_role)

        role = self.client.get_one(owner, owner_id, self.role_name)

        self.assertTrue(expected_uri, role_matcher.called)
        self.assertEqual(role, self.fake_role)

    def test_cluster_role_download(self):
        owner, owner_id = 'clusters', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/{}/'.format(self.role_name))
        role_matcher = self.m_request.get(expected_uri, json=self.fake_role)

        role = self.client.get_one(owner, owner_id, self.role_name)

        self.assertTrue(expected_uri, role_matcher.called)
        self.assertEqual(role, self.fake_role)

    def test_release_role_update(self):
        owner, owner_id = 'releases', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id,
                  "role_name": self.role_name}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/{}/'.format(self.role_name))
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_role)

        self.client.update(self.fake_role, **params)

        self.assertTrue(upd_matcher.called)
        self.assertEqual(self.fake_role, upd_matcher.last_request.json())

    def test_cluster_role_update(self):
        owner, owner_id = 'clusters', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id,
                  "role_name": self.role_name}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/{}/'.format(self.role_name))
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_role)

        self.client.update(self.fake_role, **params)

        self.assertTrue(upd_matcher.called)
        self.assertEqual(self.fake_role, upd_matcher.last_request.json())

    def test_release_role_create(self):
        owner, owner_id = 'releases', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/')
        post_matcher = self.m_request.post(expected_uri, json=self.fake_role)

        self.client.create(self.fake_role, **params)

        self.assertTrue(post_matcher.called)
        self.assertEqual(self.fake_role, post_matcher.last_request.json())

    def test_cluster_role_create(self):
        owner, owner_id = 'clusters', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/')
        post_matcher = self.m_request.post(expected_uri, json=self.fake_role)

        self.client.create(self.fake_role, **params)

        self.assertTrue(post_matcher.called)
        self.assertEqual(self.fake_role, post_matcher.last_request.json())

    def test_release_role_delete(self):
        owner, owner_id = 'releases', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/{}/'.format(self.role_name))
        delete_matcher = self.m_request.delete(expected_uri, json={})

        self.client.delete(owner, owner_id, self.role_name)

        self.assertTrue(delete_matcher.called)

    def test_cluster_role_delete(self):
        owner, owner_id = 'clusters', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/roles/{}/'.format(self.role_name))
        delete_matcher = self.m_request.delete(expected_uri, json={})

        self.client.delete(owner, owner_id, self.role_name)

        self.assertTrue(delete_matcher.called)
