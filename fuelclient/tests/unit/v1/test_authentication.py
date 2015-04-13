# -*- coding: utf-8 -*-
#
#    Copyright 2013-2014 Mirantis, Inc.
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

from mock import Mock
from mock import patch
import urllib2

from fuelclient import fuelclient_settings
from fuelclient.tests import base


class TestAuthentication(base.UnitTestCase):

    def setUp(self):
        super(TestAuthentication, self).setUp()
        self.auth_required_mock.return_value = True

    def validate_credentials_response(self,
                                      args,
                                      username=None,
                                      password=None,
                                      tenant_name=None):
        conf = fuelclient_settings.get_settings()

        self.assertEqual(args['username'], username)
        self.assertEqual(args['password'], password)
        self.assertEqual(args['tenant_name'], tenant_name)
        pr = urllib2.urlparse.urlparse(args['auth_url'])
        self.assertEqual(conf.SERVER_ADDRESS, pr.hostname)
        self.assertEqual(int(conf.LISTEN_PORT), int(pr.port))
        self.assertEqual('/keystone/v2.0', pr.path)

    @patch('fuelclient.client.requests')
    @patch('fuelclient.client.auth_client')
    def test_credentials(self, mkeystone_cli, mrequests):
        mkeystone_cli.return_value = Mock(auth_token='')
        mrequests.get_request.return_value = Mock(status_code=200)
        self.execute(
            ['fuel', '--user=a', '--password=b', 'node'])
        self.validate_credentials_response(
            mkeystone_cli.Client.call_args[1],
            username='a',
            password='b',
            tenant_name='admin'
        )
        self.execute(
            ['fuel', '--user=a', '--password', 'b', 'node'])
        self.validate_credentials_response(
            mkeystone_cli.Client.call_args[1],
            username='a',
            password='b',
            tenant_name='admin'
        )
        self.execute(
            ['fuel', '--user=a', '--password=b', '--tenant=t', 'node'])
        self.validate_credentials_response(
            mkeystone_cli.Client.call_args[1],
            username='a',
            password='b',
            tenant_name='t'
        )
        self.execute(
            ['fuel', '--user', 'a', '--password', 'b', '--tenant', 't',
             'node'])
        self.validate_credentials_response(
            mkeystone_cli.Client.call_args[1],
            username='a',
            password='b',
            tenant_name='t'
        )
        self.execute(
            ['fuel', 'node', '--user=a', '--password=b', '--tenant=t'])
        self.validate_credentials_response(
            mkeystone_cli.Client.call_args[1],
            username='a',
            password='b',
            tenant_name='t'
        )
        self.execute(
            ['fuel', 'node', '--user', 'a', '--password', 'b',
             '--tenant', 't'])
        self.validate_credentials_response(
            mkeystone_cli.Client.call_args[1],
            username='a',
            password='b',
            tenant_name='t'
        )
