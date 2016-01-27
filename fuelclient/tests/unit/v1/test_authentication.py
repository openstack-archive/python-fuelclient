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

import fixtures
import mock

from fuelclient import fuelclient_settings
from fuelclient.tests.unit.v1 import base


@mock.patch('keystoneclient.v2_0.client.Client',
            return_value=mock.Mock(auth_token=''))
class TestAuthentication(base.UnitTestCase):

    def setUp(self):
        super(TestAuthentication, self).setUp()

        self.auth_required_mock.return_value = True
        self.m_request.get('/api/v1/nodes/', json={})

        self.useFixture(fixtures.MockPatchObject(fuelclient_settings,
                                                 '_SETTINGS',
                                                 None))

    def validate_credentials_response(self, m_client, username=None,
                                      password=None, tenant_name=None):
        """Checks whether keystone was called properly."""

        conf = fuelclient_settings.get_settings()

        expected_url = 'http://{}:{}{}'.format(conf.SERVER_ADDRESS,
                                               conf.SERVER_PORT,
                                               '/keystone/v2.0')
        m_client.__init__assert_called_once_with(auth_url=expected_url,
                                                 username=username,
                                                 password=password,
                                                 tenant_name=tenant_name)

    def test_credentials_settings(self, mkeystone_cli):
        self.useFixture(fixtures.EnvironmentVariable('OS_USERNAME'))
        self.useFixture(fixtures.EnvironmentVariable('OS_PASSWORD'))
        self.useFixture(fixtures.EnvironmentVariable('OS_TENANT_NAME'))

        conf = fuelclient_settings.get_settings()
        conf.config['OS_USERNAME'] = 'test_user'
        conf.config['OS_PASSWORD'] = 'test_password'
        conf.config['OS_TENANT_NAME'] = 'test_tenant_name'

        self.execute(['fuel', 'node'])
        self.validate_credentials_response(mkeystone_cli,
                                           username='test_user',
                                           password='test_password',
                                           tenant_name='test_tenant_name')

    def test_credentials_cli(self, mkeystone_cli):
        self.useFixture(fixtures.EnvironmentVariable('OS_USERNAME'))
        self.useFixture(fixtures.EnvironmentVariable('OS_PASSWORD'))
        self.useFixture(fixtures.EnvironmentVariable('OS_TENANT_NAME'))

        self.execute(['fuel', '--os-username=a', '--os-tenant-name=admin',
                      '--os-password=b', 'node'])
        self.validate_credentials_response(mkeystone_cli,
                                           username='a',
                                           password='b',
                                           tenant_name='admin')

    def test_authentication_env_variables(self, mkeystone_cli):
        self.useFixture(fixtures.EnvironmentVariable('OS_USERNAME', 'name'))
        self.useFixture(fixtures.EnvironmentVariable('OS_PASSWORD', 'pass'))
        self.useFixture(fixtures.EnvironmentVariable('OS_TENANT_NAME', 'ten'))

        self.execute(['fuel', 'node'])
        self.validate_credentials_response(mkeystone_cli,
                                           username='name',
                                           password='pass',
                                           tenant_name='ten')

    def test_credentials_override(self, mkeystone_cli):
        self.useFixture(fixtures.EnvironmentVariable('OS_USERNAME'))
        self.useFixture(fixtures.EnvironmentVariable('OS_PASSWORD', 'var_p'))
        self.useFixture(fixtures.EnvironmentVariable('OS_TENANT_NAME', 'va_t'))

        conf = fuelclient_settings.get_settings()
        conf.config['OS_USERNAME'] = 'conf_user'
        conf.config['OS_PASSWORD'] = 'conf_password'
        conf.config['OS_TENANT_NAME'] = 'conf_tenant_name'

        self.execute(['fuel', '--os-tenant-name=cli_tenant', 'node'])
        self.validate_credentials_response(mkeystone_cli,
                                           username='conf_user',
                                           password='var_p',
                                           tenant_name='cli_tenant')
