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


@patch('fuelclient.client.requests')
class BaseSettings(base.UnitTestCase):
    def check_upload_action(self, mrequests, test_command, test_url):
        m = mock_open(read_data=YAML_TEMPLATE_DATA)
        with patch('__builtin__.open', m, create=True):
            self.execute(test_command)

        request = mrequests.put.call_args_list[0]
        url = request[0][0]
        data = request[1]['data']

        m().read.assert_called_once_with()
        self.assertEqual(mrequests.put.call_count, 1)
        self.assertIn(test_url, url)
        self.assertDictEqual(json.loads(data), JSON_TEMPLATE_DATA)

    def check_download_action(self, mrequests, test_command, test_url):
        m = mock_open()
        mresponse = Mock(status_code=200)
        mresponse.json.return_value = JSON_TEMPLATE_DATA
        mrequests.get.return_value = mresponse

        with patch('__builtin__.open', m, create=True):
            self.execute(test_command)

        request = mrequests.get.call_args_list[0]
        url = request[0][0]

        m().write.assert_called_once_with(YAML_TEMPLATE_DATA)
        self.assertEqual(mrequests.get.call_count, 1)
        self.assertIn(test_url, url)

    def test_upload_action(self, mrequests):
        self.check_upload_action(
            mrequests=mrequests,
            test_command=[
                'fuel', 'network-template', '--env', '1', '--upload'],
            test_url='/api/v1/clusters/1/network_configuration/template')

    def test_download_action(self, mrequests):
        self.check_download_action(
            mrequests=mrequests,
            test_command=[
                'fuel', 'network-template', '--env', '1', '--download'],
            test_url='/api/v1/clusters/1/network_configuration/template')
