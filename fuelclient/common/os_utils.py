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

from keystoneclient import exceptions as ks_exc
from keystoneclient.v2_0 import client

from fuelclient import fuelclient_settings
from fuelclient.cli import error


_KSCLIENT = None


def _get_ksclient(token=None):
    """Returns an authenticated Keystone client."""

    if _KSCLIENT is not None:
        return _KSCLIENT

    conf = fuelclient_settings.get_settings()

    try:
        if token:
            return client.Client(token=token, auth_url=conf.OS_AUTH_URL)
        else:
            return client.Client(username=conf.OS_USERNAME,
                                 password=conf.OS_PASSWORD,
                                 tenant_name=conf.OS_TENANT_NAME,
                                 region_name=conf.OS_REGION_NAME,
                                 auth_url=conf.OS_AUTH_URL)
    except ks_exc.Unauthorized:
        raise error.Unauthorized()
    except ks_exc.AuthorizationFailure as err:
        raise error.AuthenticationError('Keystone authentication failed: '
                                        '%s' % err)


def get_auth_token():
    """Get user's auth_token from the Keystone."""
    ksclient = _get_ksclient()
    return ksclient.auth_token


def get_service_url(service_type='fuel', endpoint_type='public'):
    """Wrapper for get service url from keystone service catalog.

    Given a service_type and an endpoint_type, this method queries keystone
    service catalog and provides the url for the desired endpoint.

    :param service_type: the keystone service for which url is required.
    :param endpoint_type: the type of endpoint for the service.
    :returns: an http/https url for the desired endpoint.

    """
    conf = fuelclient_settings.get_settings()
    ksclient = _get_ksclient()

    if not ksclient.has_service_catalog():
        raise error.KeystoneFailure('No Keystone service catalog loaded.')

    try:
        endpoint = ksclient.service_catalog.url_for(service_type=service_type,
                                                    endpoint_type=endpoint_type,
                                                    region_name=conf.OS_REGION_NAME)

    except ks_exc.EndpointNotFound:
        msg = ('Fuel API endpoint not found: '
               'service type: {st}, endpoint type: {et}.')

        raise error.KeystoneFailure(msg.format(st=service_type,
                                               et=endpoint_type))

    return endpoint
