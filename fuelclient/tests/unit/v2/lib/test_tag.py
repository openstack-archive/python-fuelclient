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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestTagFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestTagFacade, self).setUp()

        self.version = 'v1'
        self.tag_name = 'fake_tag'
        self.fake_tag = utils.get_fake_tag(self.tag_name)
        self.fake_tags = utils.get_fake_tags(10)

        self.client = fuelclient.get_client('tag', self.version)

    def get_uri(self, owner):
        return '/api/{version}/{owner}/'.format(version=self.version,
                                                owner=owner)

    def test_release_tag_list(self):
        owner, owner_id = 'releases', 42
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/')
        matcher = self.m_request.get(expected_uri, json=self.fake_tags)
        self.client.get_all(owner, owner_id)

        self.assertTrue(matcher.called)

    def test_cluster_tag_list(self):
        owner, owner_id = 'clusters', 42
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/')
        matcher = self.m_request.get(expected_uri, json=self.fake_tags)
        self.client.get_all(owner_type=owner, owner_id=owner_id)

        self.assertTrue(matcher.called)

    def test_release_tag_download(self):
        owner, owner_id = 'releases', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/{}/'.format(self.tag_name))
        tag_matcher = self.m_request.get(expected_uri, json=self.fake_tag)

        tag = self.client.get_tag(owner, owner_id, self.tag_name)

        self.assertTrue(expected_uri, tag_matcher.called)
        self.assertEqual(tag, self.fake_tag)

    def test_cluster_tag_download(self):
        owner, owner_id = 'clusters', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/{}/'.format(self.tag_name))
        tag_matcher = self.m_request.get(expected_uri, json=self.fake_tag)

        tag = self.client.get_tag(owner, owner_id, self.tag_name)

        self.assertTrue(expected_uri, tag_matcher.called)
        self.assertEqual(tag, self.fake_tag)

    def test_release_tag_update(self):
        owner, owner_id = 'releases', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id,
                  "tag_name": self.tag_name}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/{}/'.format(self.tag_name))
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_tag)

        self.client.update(self.fake_tag, **params)

        self.assertTrue(upd_matcher.called)
        self.assertEqual(self.fake_tag, upd_matcher.last_request.json())

    def test_cluster_tag_update(self):
        owner, owner_id = 'clusters', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id,
                  "tag_name": self.tag_name}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/{}/'.format(self.tag_name))
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_tag)

        self.client.update(self.fake_tag, **params)

        self.assertTrue(upd_matcher.called)
        self.assertEqual(self.fake_tag, upd_matcher.last_request.json())

    def test_release_tag_create(self):
        owner, owner_id = 'releases', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/')
        post_matcher = self.m_request.post(expected_uri, json=self.fake_tag)

        self.client.create(self.fake_tag, **params)

        self.assertTrue(post_matcher.called)
        self.assertEqual(self.fake_tag, post_matcher.last_request.json())

    def test_cluster_tag_create(self):
        owner, owner_id = 'clusters', 45
        params = {"owner_type": owner,
                  "owner_id": owner_id}
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/')
        post_matcher = self.m_request.post(expected_uri, json=self.fake_tag)

        self.client.create(self.fake_tag, **params)

        self.assertTrue(post_matcher.called)
        self.assertEqual(self.fake_tag, post_matcher.last_request.json())

    def test_release_tag_delete(self):
        owner, owner_id = 'releases', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/{}/'.format(self.tag_name))
        delete_matcher = self.m_request.delete(expected_uri, json={})

        self.client.delete(owner, owner_id, self.tag_name)

        self.assertTrue(delete_matcher.called)

    def test_cluster_tag_delete(self):
        owner, owner_id = 'clusters', 45
        expected_uri = self.get_object_uri(self.get_uri(owner),
                                           owner_id,
                                           '/tags/{}/'.format(self.tag_name))
        delete_matcher = self.m_request.delete(expected_uri, json={})

        self.client.delete(owner, owner_id, self.tag_name)

        self.assertTrue(delete_matcher.called)
