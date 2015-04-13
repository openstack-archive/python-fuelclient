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

        self.top_matcher = self.m_request.register_uri(rm.ANY,
                                                       rm.ANY,
                                                       json={})

        self.auth_required_patch = patch.object(client.Client,
                                                'auth_required',
                                                new_callable=mock.PropertyMock)
        self.m_auth_required = self.auth_required_patch.start()
        self.m_auth_required.return_value = False

        self.addCleanup(self.m_request.stop)
        self.addCleanup(self.auth_required_patch.stop)

    def tearDown(self):
        calls = ['{method} {path}'.format(method=req.method, path=req.path)
                 for req in self.top_matcher.request_history]
        calls = '\n'.join(calls)
        msg = 'Unexpected HTTP requests were detected:\n {0}'.format(calls)

        self.assertFalse(self.top_matcher.called, msg=msg)

    def get_object_uri(self, collection_path, object_id, attribute='/'):
        return urlparse.urljoin(collection_path, str(object_id) + attribute)
