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

import mock
from mock import patch
import requests_mock as rm
from six.moves.urllib import parse as urlparse

from fuelclient import client
from fuelclient.tests import base


class BaseLibTest(base.UnitTestCase):
    def setUp(self):
        self.m_request = rm.Mocker()
        self.m_request.start()

        self.session_adapter = self.m_request._adapter.register_uri(rm.ANY,
                                                                    rm.ANY)

        self.token_patcher = mock.patch('fuelclient.common.os_utils.get_auth_token')
        self.service_url_patcher = mock.patch('fuelclient.common.os_utils.get_service_url')

        self.m_get_token = self.token_patcher.start()
        self.m_get_token.return_value = 'DEADBEEF'

        self.m_get_service_url = self.service_url_patcher.start()
        self.m_get_service_url.return_value = 'http://127.0.0.1:8000/api/v1/'

    def tearDown(self):
        self.m_request.stop()
        self.token_patcher.stop()
        self.service_url_patcher.stop()

    def get_object_uri(self, collection_path, object_id, attribute='/'):
        return urlparse.urljoin(collection_path, str(object_id) + attribute)
