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
from oslotest import base as oslo_base
import requests_mock as rm
from six.moves.urllib import parse as urlparse

from fuelclient import client


class BaseLibTest(oslo_base.BaseTestCase):
    def setUp(self):
        super(BaseLibTest, self).setUp()

        self.m_request = rm.Mocker()
        self.m_request.start()

        self.auth_required_patch = patch.object(client.APIClient,
                                                'auth_required',
                                                new_callable=mock.PropertyMock)
        self.m_auth_required = self.auth_required_patch.start()
        self.m_auth_required.return_value = False

        self.addCleanup(self.m_request.stop)
        self.addCleanup(self.auth_required_patch.stop)

    def get_object_uri(self, collection_path, object_id, attribute='/'):
        return urlparse.urljoin(collection_path, str(object_id) + attribute)
