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
import yaml

from oslo_serialization import jsonutils as json

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api


YAML_TEMPLATE = """adv_net_template:
  default:
    network_assignments:
      fuelweb_admin:
        ep: br-fw-admin
      management:
        ep: br-mgmt
      private:
        ep: br-prv
      public:
        ep: br-ex
      storage:
        ep: br-storage
    nic_mapping:
      default:
        if1: eth0
    templates_for_node_role:
      ceph-osd:
      - common
      - storage
      compute:
      - common
      - private
      - storage
      controller:
      - public
      - private
      - storage
      - common
"""


JSON_TEMPLATE = """{
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


class TestNetworkTemplateFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestNetworkTemplateFacade, self).setUp()

        self.version = 'v1'
        self.env_id = 42
        self.res_uri = (
            '/api/{version}/clusters/{env_id}'
            '/network_configuration/template'.format(
                version=self.version, env_id=self.env_id))

        self.client = fuelclient.get_client('environment', self.version)

    def test_network_template_upload(self):
        expected_body = json.loads(JSON_TEMPLATE)
        matcher = self.m_request.put(
            self.res_uri, json=expected_body)

        m_open = mock.mock_open(read_data=YAML_TEMPLATE)
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.upload_network_template(
                self.env_id,
                'fake_network_template_1.yaml'
            )

        m_open.assert_called_with('fake_network_template_1.yaml', 'r')
        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())

    def test_network_template_download(self):
        expected_body = json.loads(JSON_TEMPLATE)
        matcher = self.m_request.get(self.res_uri, json=expected_body)

        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.download_network_template(self.env_id)

        self.assertTrue(matcher.called)

        written_yaml = yaml.safe_load(m_open().write.mock_calls[0][1][0])
        expected_yaml = yaml.safe_load(YAML_TEMPLATE)
        self.assertEqual(written_yaml, expected_yaml)

    def test_network_template_delete(self):
        matcher = self.m_request.delete(self.res_uri, json={})

        self.client.delete_network_template(self.env_id)

        self.assertTrue(matcher.called)
