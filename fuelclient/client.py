#    Copyright 2014 Mirantis, Inc.
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

import json
import logging
import requests

from keystoneclient.v2_0 import client as auth_client
from six.moves.urllib import parse as urlparse

from fuelclient import fuelclient_settings
from fuelclient.logs import NullHandler


# configure logging to silent all logs
# and prevent issues in keystoneclient logging
logger = logging.getLogger()
logger.addHandler(NullHandler())


class Client(object):
    """This class handles API requests
    """

    def __init__(self):
        conf = fuelclient_settings.get_settings()

        self.debug = False
        self.root = "http://{server}:{port}".format(server=conf.SERVER_ADDRESS,
                                                    port=conf.LISTEN_PORT)

        self.keystone_base = urlparse.urljoin(self.root, "/keystone/v2.0")
        self.api_root = urlparse.urljoin(self.root, "/api/v1/")
        self.ostf_root = urlparse.urljoin(self.root, "/ostf/")
        self.user = conf.KEYSTONE_USER
        self.password = conf.KEYSTONE_PASS
        self.tenant = 'admin'
        self._keystone_client = None
        self._auth_required = None

    @property
    def auth_token(self):
        if self.auth_required:
            if not self.keystone_client.auth_token:
                self.keystone_client.authenticate()
            return self.keystone_client.auth_token
        return ''

    @property
    def auth_required(self):
        if self._auth_required is None:
            url = self.api_root + 'version'
            resp = requests.get(url)
            resp.raise_for_status()

            self._auth_required = resp.json().get('auth_required', False)
        return self._auth_required

    @property
    def keystone_client(self):
        if not self._keystone_client:
            self.initialize_keystone_client()
        return self._keystone_client

    def update_own_password(self, new_pass):
        if self.auth_token:
            self.keystone_client.users.update_own_password(
                self.password, new_pass)

    def initialize_keystone_client(self):
        if self.auth_required:
            self._keystone_client = auth_client.Client(
                username=self.user,
                password=self.password,
                auth_url=self.keystone_base,
                tenant_name=self.tenant)
            self._keystone_client.session.auth = self._keystone_client
            self._keystone_client.authenticate()

    def debug_mode(self, debug=False):
        self.debug = debug
        return self

    def print_debug(self, message):
        if self.debug:
            print(message)

    def delete_request(self, api):
        """Make DELETE request to specific API with some data
        """
        url = self.api_root + api
        self.print_debug(
            "DELETE {0}".format(self.api_root + api)
        )

        headers = {'content-type': 'application/json',
                   'x-auth-token': self.auth_token}
        resp = requests.delete(url, headers=headers)
        resp.raise_for_status()

        if resp.status_code == 204:
            return {}

        return resp.json()

    def put_request(self, api, data):
        """Make PUT request to specific API with some data
        """
        url = self.api_root + api
        data_json = json.dumps(data)
        self.print_debug(
            "PUT {0} data={1}"
            .format(self.api_root + api, data_json)
        )

        headers = {'content-type': 'application/json',
                   'x-auth-token': self.auth_token}
        resp = requests.put(url, data=data_json, headers=headers)
        resp.raise_for_status()

        return resp.json()

    def get_request_raw(self, api, ostf=False, params=None):
        """Make a GET request to specific API and return raw response.

        :param api: API endpoint (path)
        :param ostf: is this a call to OSTF API
        :param params: params passed to GET request
        """
        url = (self.ostf_root if ostf else self.api_root) + api
        self.print_debug(
            "GET {0}"
            .format(url)
        )

        headers = {'x-auth-token': self.auth_token}
        params = params or {}
        return requests.get(url, params=params, headers=headers)

    def get_request(self, api, ostf=False, params=None):
        """Make GET request to specific API
        """
        resp = self.get_request_raw(api, ostf, params)
        resp.raise_for_status()

        return resp.json()

    def post_request_raw(self, api, data=None, ostf=False):
        """Make a POST request to specific API and return raw response.

        :param api: API endpoint (path)
        :param data: data send in request, will be serialzied to JSON
        :param ostf: is this a call to OSTF API
        """
        url = (self.ostf_root if ostf else self.api_root) + api
        headers = {'x-auth-token': self.auth_token}
        data_json = None

        if data:
            data_json = json.dumps(data)
            self.print_debug(
                'POST {0} data={1}'.format(url, data_json)
            )
            headers.update({'content-type': 'application/json'})
        else:
            self.print_debug('POST {0} with empty data'.format(url))

        return requests.post(url, data=data_json, headers=headers)

    def post_request(self, api, data=None, ostf=False):
        """Make POST request to specific API with some data
        """
        resp = self.post_request_raw(api, data, ostf=ostf)
        resp.raise_for_status()

        return resp.json()

    def get_fuel_version(self):
        return self.get_request("version")

# This line is single point of instantiation for 'Client' class,
# which intended to implement Singleton design pattern.
APIClient = Client()
