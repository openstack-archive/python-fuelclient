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
from fuelclient.objects import base
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.v1 import base_v1


class FakeObject(base.BaseObject):
    class_api_path = 'fake/objects/'


class FakeClient(base_v1.BaseV1Client):

    _entity_wrapper = FakeObject


class TestClient(test_api.BaseLibTest):

    def setUp(self):
        super(TestClient, self).setUp()

        self.host = 'test.host.tld'
        self.port = 8888

        self.connection = fuelclient.connect(self.host, self.port)

        self.client = FakeClient(connection=self.connection)

        self.version = 'v1'
        self.res_uri = '/api/{version}/fake/objects/'.format(
            version=self.version)

    def test_custom_connection_used(self):
        m_get = self.m_request.get(self.res_uri, json={})
        self.client.get_all()

        self.assertTrue(m_get.called)
        self.assertEqual(
            m_get.last_request.netloc,
            '{host}:{port}'.format(host=self.host, port=self.port))
