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

import io

import mock

from fuelclient.tests import base


@mock.patch('fuelclient.client.requests')
class TestPluginsActions(base.UnitTestCase):

    @mock.patch('fuelclient.cli.actions.token.APIClient')
    def test_token_action(self, mAPIClient, mrequests):
        with mock.patch('sys.stdout', new=io.StringIO()) as mstdout:
            token = u'token123'
            mauth_token = mock.PropertyMock(return_value=token)
            type(mAPIClient).auth_token = mauth_token

            self.execute(['fuel', 'token'])

            self.assertEqual(mauth_token.call_count, 1)
            self.assertEqual(mstdout.getvalue(), token)
