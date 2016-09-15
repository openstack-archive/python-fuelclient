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


class TestTagFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestTagFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/'.format(
            version=self.version)
        self.fake_tag = utils.get_fake_tag('fake_tag')
        self.fake_tags = utils.get_fake_tags(10)
        self.instance_uri = (self.res_uri +
                             'tags/{}/'.format(self.fake_tag['id']))

        self.client = fuelclient.get_client('tag', self.version)

    def test_tag_list(self):
        expected_uri = self.res_uri + 'tags/'
        matcher = self.m_request.get(expected_uri, json=self.fake_tags)
        [t for t in self.client.get_all()]
        self.assertTrue(matcher.called)

    def test_tag_download(self):
        expected_uri = self.instance_uri
        tag_matcher = self.m_request.get(expected_uri, json=self.fake_tag)

        tag = self.client.get_one(self.fake_tag['id'])

        self.assertTrue(expected_uri, tag_matcher.called)
        self.assertEqual(tag, self.fake_tag)

    def test_tag_upload(self):
        expected_uri = self.instance_uri
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_tag)

        self.client.upload(self.fake_tag, self.fake_tag['id'])

        self.assertTrue(upd_matcher.called)
        self.assertEqual(self.fake_tag, upd_matcher.last_request.json())

    def test_tag_create(self):
        expected_uri = self.res_uri + 'tags/'
        post_matcher = self.m_request.post(expected_uri, json=self.fake_tag)

        self.client.create(self.fake_tag, **self.fake_tag)

        self.assertTrue(post_matcher.called)
        self.assertEqual(self.fake_tag, post_matcher.last_request.json())

    def test_tag_delete(self):
        expected_uri = self.instance_uri
        delete_matcher = self.m_request.delete(expected_uri, json={})
        self.client.delete(self.fake_tag['id'])

        self.assertTrue(delete_matcher.called)

    def test_tag_assign(self):
        expected_uri = (self.res_uri +
                        'nodes/{node_id}/tags/assign/'.format(node_id=1))
        tag_ids = [self.fake_tag['id']]
        node_id = 1
        post_matcher = self.m_request.post(expected_uri, json=tag_ids)
        self.client.assign(tag_ids, node_id)

        self.assertTrue(post_matcher.called)
        self.assertEqual(tag_ids, post_matcher.last_request.json())

    def test_tag_unassign(self):
        expected_uri = (self.res_uri +
                        'nodes/{node_id}/tags/unassign/'.format(node_id=1))
        tag_ids = [self.fake_tag['id']]
        node_id = 1
        post_matcher = self.m_request.post(expected_uri, json=tag_ids)
        self.client.unassign(tag_ids, node_id)

        self.assertTrue(post_matcher.called)
        self.assertEqual(tag_ids, post_matcher.last_request.json())
