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
        if2: eth1
        if3: eth3
        if4: eth4
        if5: eth2
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
    network_scheme:
      storage:
        transformations:
          - action: add-br
            name: br-storage
          - action: add-port
            bridge: br-storage
            name: if4.102
        endpoints:
          - br-storage
        roles:
          cinder/iscsi: br-storage
          swift/replication: br-storage
          ceph/replication: br-storage
          storage: br-storage
          mgmt/memcache: br-storage
          mgmt/database: br-storage
          ceph/public: br-storage
      private:
        transformations:
          - action: add-br
            name: br-prv
            provider: ovs
          - action: add-br
            name: br-aux
          - action: add-patch
            bridges:
            - br-prv
            - br-aux
            provider: ovs
            mtu: 65000
          - action: add-port
            bridge: br-aux
            name: if4.103
        endpoints:
          - br-prv
        roles:
          neutron/private: br-prv
      public:
        transformations:
          - action: add-br
            name: br-ex
          - action: add-br
            name: br-floating
            provider: ovs
          - action: add-patch
            bridges:
            - br-floating
            - br-ex
            provider: ovs
            mtu: 65000
          - action: add-port
            bridge: br-ex
            name: if2
        endpoints:
          - br-ex
        roles:
          public/vip: br-ex
          neutron/floating: br-floating
          ceph/radosgw: br-ex
          ex: br-ex
      common:
        transformations:
          - action: add-br
            name: br-fw-admin
          - action: add-port
            bridge: br-fw-admin
            name: if1
          - action: add-br
            name: br-mgmt
          - action: add-port
            bridge: br-mgmt
            name: if3.101
          - action: add-br
            name: br-fake
          - action: add-bond
            bridge: br-fake
            name: lnx-bond0
            interfaces:
            - if5.201
            - if5.202
            bond_properties:
              mode: active-backup
            interface_properties: {}
        endpoints:
          - br-fw-admin
          - br-mgmt
          - br-fake
        roles:
          admin/pxe: br-fw-admin
          fw-admin: br-fw-admin
          mongo/db: br-mgmt
          management: br-mgmt
          keystone/api: br-mgmt
          neutron/api: br-mgmt
          neutron/mesh: br-mgmt
          swift/api: br-mgmt
          sahara/api: br-mgmt
          ceilometer/api: br-mgmt
          cinder/api: br-mgmt
          glance/api: br-mgmt
          heat/api: br-mgmt
          nova/api: br-mgmt
          murano/api: br-mgmt
          horizon: br-mgmt
          mgmt/api: br-mgmt
          mgmt/messaging: br-mgmt
          mgmt/corosync: br-mgmt
          mgmt/vip: br-mgmt
          mgmt/api: br-mgmt
"""
JSON_TEMPLATE_DATA = {
    "adv_net_template": {
        "default": {
            "nic_mapping": {
                "default": {
                    "if1": "eth0",
                    "if2": "eth1",
                    "if3": "eth3",
                    "if4": "eth4",
                    "if5": "eth2"
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
            },
            "network_scheme": {
                "storage": {
                    "transformations": [
                        {
                            "action": "add-br",
                            "name": "br-storage"
                        },
                        {
                            "action": "add-port",
                            "bridge": "br-storage",
                            "name": "if4.102"
                        }
                    ],
                    "endpoints": [
                        "br-storage"
                    ],
                    "roles": {
                        "cinder/iscsi": "br-storage",
                        "swift/replication": "br-storage",
                        "ceph/replication": "br-storage",
                        "storage": "br-storage",
                        "mgmt/memcache": "br-storage",
                        "mgmt/database": "br-storage",
                        "ceph/public": "br-storage"
                    }
                },
                "private": {
                    "transformations": [
                        {
                            "action": "add-br",
                            "name": "br-prv",
                            "provider": "ovs"
                        },
                        {
                            "action": "add-br",
                            "name": "br-aux"
                        },
                        {
                            "action": "add-patch",
                            "bridges": [
                                "br-prv",
                                "br-aux"
                            ],
                            "provider": "ovs",
                            "mtu": 65000
                        },
                        {
                            "action": "add-port",
                            "bridge": "br-aux",
                            "name": "if4.103"
                        }
                    ],
                    "endpoints": [
                        "br-prv"
                    ],
                    "roles": {
                        "neutron/private": "br-prv"
                    }
                },
                "public": {
                    "transformations": [
                        {
                            "action": "add-br",
                            "name": "br-ex"
                        },
                        {
                            "action": "add-br",
                            "name": "br-floating",
                            "provider": "ovs"
                        },
                        {
                            "action": "add-patch",
                            "bridges": [
                                "br-floating",
                                "br-ex"
                            ],
                            "provider": "ovs",
                            "mtu": 65000
                        },
                        {
                            "action": "add-port",
                            "bridge": "br-ex",
                            "name": "if2"
                        }
                    ],
                    "endpoints": [
                        "br-ex"
                    ],
                    "roles": {
                        "public/vip": "br-ex",
                        "neutron/floating": "br-floating",
                        "ceph/radosgw": "br-ex",
                        "ex": "br-ex"
                    }
                },
                "common": {
                    "transformations": [
                        {
                            "action": "add-br",
                            "name": "br-fw-admin"
                        },
                        {
                            "action": "add-port",
                            "bridge": "br-fw-admin",
                            "name": "if1"
                        },
                        {
                            "action": "add-br",
                            "name": "br-mgmt"
                        },
                        {
                            "action": "add-port",
                            "bridge": "br-mgmt",
                            "name": "if3.101"
                        },
                        {
                            "action": "add-br",
                            "name": "br-fake"
                        },
                        {
                            "action": "add-bond",
                            "bridge": "br-fake",
                            "name": "lnx-bond0",
                            "interfaces": [
                                "if5.201",
                                "if5.202"
                            ],
                            "bond_properties": {
                                "mode": "active-backup"
                            },
                            "interface_properties": {}
                        }
                    ],
                    "endpoints": [
                        "br-fw-admin",
                        "br-mgmt",
                        "br-fake"
                    ],
                    "roles": {
                        "admin/pxe": "br-fw-admin",
                        "fw-admin": "br-fw-admin",
                        "mongo/db": "br-mgmt",
                        "management": "br-mgmt",
                        "keystone/api": "br-mgmt",
                        "neutron/api": "br-mgmt",
                        "neutron/mesh": "br-mgmt",
                        "swift/api": "br-mgmt",
                        "sahara/api": "br-mgmt",
                        "ceilometer/api": "br-mgmt",
                        "cinder/api": "br-mgmt",
                        "glance/api": "br-mgmt",
                        "heat/api": "br-mgmt",
                        "nova/api": "br-mgmt",
                        "murano/api": "br-mgmt",
                        "horizon": "br-mgmt",
                        "mgmt/api": "br-mgmt",
                        "mgmt/messaging": "br-mgmt",
                        "mgmt/corosync": "br-mgmt",
                        "mgmt/vip": "br-mgmt"
                    }
                }
            }
        }
    }
}


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


@patch('fuelclient.client.requests')
class TestSettings(BaseSettings):
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
