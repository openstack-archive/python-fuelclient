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

import json

from mock import Mock
from mock import mock_open
from mock import patch

from fuelclient.objects.environment import Environment
import requests_mock

from fuelclient.tests import base

YAML_TEMPLATE_DATA = """adv_net_template:
  default:
    nic_mapping:
      default:
        if1: eth0
    templates_for_node_role:
        controller:
          - public
          - private
          - storage
          - common
        compute:
          - common
          - private
          - storage
        ceph-osd:
          - common
          - storage
    network_assignments:
        storage:
          ep: br-storage
        private:
          ep: br-prv
        public:
          ep: br-ex
        management:
          ep: br-mgmt
        fuelweb_admin:
          ep: br-fw-admin
"""

JSON_TEMPLATE_DATA = """{
  "adv_net_template": {
    "default": {
      "nic_mapping": {
        "default": {
          "if1": "eth0"
        }
      },
      "templates_for_node_role": {
        "controller": [
          "public",
          "private",
          "storage",
          "common"
        ],
        "compute": [
          "common",
          "private",
          "storage"
        ],
        "ceph-osd": [
          "common",
          "storage"
        ]
      },
      "network_assignments": {
        "storage": {
          "ep": "br-storage"
        },
        "private": {
          "ep": "br-prv"
        },
        "public": {
          "ep": "br-ex"
        },
        "management": {
          "ep": "br-mgmt"
        },
        "fuelweb_admin": {
          "ep": "br-fw-admin"
        }
      }
    }
  }
}
"""


class TestNetworkTemplate(base.UnitTestCase):
    def setUp(self):
        super(TestNetworkTemplate, self).setUp()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()
        self.env_id = 42
        self.net_loc = 'http://127.0.0.1:8000'
        self.req_path = '/api/v1/' + Environment.network_template_path.format(
            self.env_id)

    def tearDown(self):
        self.mocker.stop()

    def test_upload_action(self):
        self.mocker.put(self.net_loc + self.req_path)
        test_command = [
            'fuel', 'network-template', '--env', str(self.env_id), '--upload']

        m_open = mock_open(read_data=YAML_TEMPLATE_DATA)
        with patch('__builtin__.open', m_open, create=True):
            self.execute(test_command)

        self.assertEqual(self.mocker.last_request.method, 'PUT')
        self.assertEqual(self.mocker.last_request.path, self.req_path)
        self.assertEqual(self.mocker.last_request.json(),
                         json.loads(JSON_TEMPLATE_DATA))
        m_open().read.assert_called_once_with()

    def test_download_action(self):
        self.mocker.get(self.net_loc + self.req_path, text=YAML_TEMPLATE_DATA)

        test_command = [
            'fuel', 'network-template', '--env', str(self.env_id),
            '--download']

        m_open = mock_open()
        with patch('__builtin__.open', m_open, create=True):
            self.execute(test_command)
            with open('foo', 'w') as h:
                h.write('some stuff')

        self.assertEqual(self.mocker.last_request.method, 'GET')
        self.assertEqual(self.mocker.last_request.path, self.req_path)
        m_open().write.assert_called_once_with(YAML_TEMPLATE_DATA)
