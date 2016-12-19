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

import mock
import six
import yaml

from six import StringIO

from fuelclient.commands import node as cmd_node
from fuelclient import main as main_mod
from fuelclient.tests.unit.v2.cli import test_engine
from fuelclient.tests.utils import fake_node
from fuelclient.v1 import node


class TestNodeCommand(test_engine.BaseCLITest):
    """Tests for fuel2 node * commands."""

    def setUp(self):
        super(TestNodeCommand, self).setUp()

        self.m_client.get_all.return_value = [fake_node.get_fake_node()
                                              for i in range(10)]
        self.m_client.get_by_id.return_value = fake_node.get_fake_node()

    def test_node_list(self):
        args = 'node list'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_node_list_sorted(self):
        args = 'node list -s name'
        self.exec_command(args)
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with()

    def test_node_list_with_env(self):
        env_id = 42
        args = 'node list --env {env}'.format(env=env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(
            environment_id=env_id)

    def test_node_list_with_labels(self):
        labels = ['key_1=val_1', 'key_2=val_2', 'key3']
        args = 'node list --labels {labels}'.format(
            labels=' '.join(labels))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(labels=labels)

    def test_node_list_with_env_and_labels(self):
        env_id = 42
        labels = ['key_1=val_1', 'key_2=val_2', 'key3']
        args = 'node list --env {env} --labels {labels}'.format(
            env=env_id, labels=' '.join(labels))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(
            environment_id=env_id, labels=labels)
        self.assertIsInstance(
            self.m_client.get_all.call_args[1].get('labels')[0], six.text_type)

    def test_node_list_ansible_inventory(self):
        self.m_client.get_all.return_value = [
            fake_node.get_fake_node(hostname='node-1',
                                    ip='10.20.0.2',
                                    roles=['compute']),
            fake_node.get_fake_node(hostname='node-2',
                                    ip='10.20.0.3',
                                    roles=['compute', 'ceph-osd']),
            fake_node.get_fake_node(hostname='node-3',
                                    ip='10.20.0.4',
                                    roles=['controller']),
            fake_node.get_fake_node(hostname='node-4',
                                    ip='10.20.0.5',
                                    roles=['controller', 'mongo']),
            fake_node.get_fake_node(hostname='node-5',
                                    ip='10.20.0.6',
                                    roles=['controller', 'ceph-osd']),
        ]

        expected_output = '''\
[ceph-osd]
node-2 ansible_host=10.20.0.3
node-5 ansible_host=10.20.0.6

[compute]
node-1 ansible_host=10.20.0.2
node-2 ansible_host=10.20.0.3

[controller]
node-3 ansible_host=10.20.0.4
node-4 ansible_host=10.20.0.5
node-5 ansible_host=10.20.0.6

[mongo]
node-4 ansible_host=10.20.0.5

'''

        args = 'node ansible-inventory --env 1'
        with mock.patch('sys.stdout', new=StringIO()) as mstdout:
            rv = self.exec_command(args)
            actual_output = mstdout.getvalue()

        self.assertFalse(rv)
        self.assertEqual(expected_output, actual_output)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(
            environment_id=1, labels=None)

    def test_node_show(self):
        node_id = 42
        args = 'node show {node_id}'.format(node_id=node_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_by_id.assert_called_once_with(node_id)

    def test_node_vms_conf_list(self):
        node_id = 42
        args = 'node list-vms-conf {node_id}'.format(node_id=node_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_node_vms_conf.assert_called_once_with(node_id)

    def test_node_vms_conf_create(self):
        vms_conf = r'{\"id\":2} {\"id\":3}'
        config = [{'id': 2},
                  {'id': 3}]

        node_id = 42

        args = 'node create-vms-conf {0} --conf {1}'.format(
            node_id,
            vms_conf)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.node_vms_create.assert_called_once_with(node_id, config)

    def test_node_vms_conf_create_from_list(self):
        vms_conf = '[{"id": 2}, {"id": 3}]'
        config = [{'id': 2}, {'id': 3}]

        node_id = 42

        args = "node create-vms-conf {0} --conf '{1}'".format(
            node_id, vms_conf)
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.node_vms_create.assert_called_once_with(node_id, config)

    def test_node_vms_conf_create_fail(self):
        vms_conf = '[{"id": '
        node_id = 42

        args = "node create-vms-conf {0} --conf '{1}'".format(node_id,
                                                              vms_conf)
        self.assertRaises(SystemExit,
                          self.exec_command,
                          args)

    @mock.patch('cliff.formatters.table.TableFormatter.emit_one')
    def test_node_set_hostname(self, m_emit_one):
        self.m_client._updatable_attributes = \
            node.NodeClient._updatable_attributes
        node_id = 42
        hostname = 'test-name'
        expected_field_data = cmd_node.NodeShow.columns

        self.m_client.update.return_value = \
            fake_node.get_fake_node(node_id=node_id,
                                    hostname=hostname)

        args = 'node update {node_id} --hostname {hostname}'\
            .format(node_id=node_id, hostname=hostname)

        self.exec_command(args)
        m_emit_one.assert_called_once_with(expected_field_data,
                                           mock.ANY,
                                           mock.ANY,
                                           mock.ANY)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.update.assert_called_once_with(
            node_id, hostname=hostname)

    @mock.patch('cliff.formatters.table.TableFormatter.emit_one')
    def test_node_set_name(self, m_emit_one):
        self.m_client._updatable_attributes = \
            node.NodeClient._updatable_attributes
        node_id = 37
        expected_field_data = cmd_node.NodeShow.columns

        test_cases = ('new-name', 'New Name', 'śćż∑ Pó', '你一定是无聊')
        for name in test_cases:
            self.m_client.update.return_value = fake_node.get_fake_node(
                node_id=node_id, node_name=name)

            cmd = ['node', 'update', str(node_id), '--name', name]

            # NOTE(sbrzeczkowski): due to shlex inability to accept
            # unicode arguments prior to python 2.7.3
            main_mod.main(argv=cmd)

            if six.PY2:
                name = name.decode('utf-8')

            m_emit_one.assert_called_with(expected_field_data,
                                          mock.ANY,
                                          mock.ANY,
                                          mock.ANY)
            self.m_get_client.assert_called_once_with('node', mock.ANY)
            self.m_client.update.assert_called_once_with(
                node_id, name=name)
            self.m_get_client.reset_mock()
            self.m_client.reset_mock()

    def test_node_label_list_for_all_nodes(self):
        args = 'node label list'

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all_labels_for_nodes.assert_called_once_with(
            node_ids=None)

    def test_node_label_list_sorted(self):
        args = 'node label list -s label_name'
        self.exec_command(args)
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all_labels_for_nodes.assert_called_once_with(
            node_ids=None)

    def test_node_label_list_for_specific_nodes(self):
        node_ids = ['42', '43']
        args = 'node label list --nodes {node_ids}'.format(
            node_ids=' '.join(node_ids))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all_labels_for_nodes.assert_called_once_with(
            node_ids=node_ids)

    def test_node_label_set_for_all_nodes(self):
        labels = ['key_1=val_1', 'key_2=val_2']
        args = 'node label set -l {labels} --nodes-all'.format(
            labels=' '.join(labels))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_labels_for_nodes.assert_called_once_with(
            labels=labels, node_ids=None)

    @mock.patch('argparse.ArgumentParser.error')
    def test_node_label_set_for_all_nodes_wo_labels_arg(self, merror):
        cmd = 'node label set --nodes-all'
        self.exec_command(cmd)
        args, _ = merror.call_args
        self.assertIn('-l/--labels', args[0])

    def test_node_label_set_for_specific_nodes(self):
        labels = ['key_1=val_1', 'key_2=val_2']
        node_ids = ['42', '43']
        args = 'node label set -l {labels} --nodes {node_ids}'.format(
            labels=' '.join(labels), node_ids=' '.join(node_ids))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_labels_for_nodes.assert_called_once_with(
            labels=labels, node_ids=node_ids)

    def test_node_delete_specific_labels_for_all_nodes(self):
        labels = ['key_1', 'key_2']
        args = 'node label delete -l {labels} --nodes-all'.format(
            labels=' '.join(labels))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.delete_labels_for_nodes.assert_called_once_with(
            labels=labels, node_ids=None)

    @mock.patch('json.dump')
    def test_node_disks_download_json(self, m_dump):
        args = 'node disks download --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/disks.json'

        self.m_client.get_disks.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_disks.assert_called_once_with(42)

    def test_node_disks_upload_json(self):
        args = 'node disks upload --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/disks.json'

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_disks.assert_called_once_with(42, test_data)

    @mock.patch('json.dump')
    def test_node_disks_getdefault_json(self, m_dump):
        args = 'node disks get-default --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/disks.json'

        self.m_client.get_default_disks.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_default_disks.assert_called_once_with(42)

    @mock.patch('yaml.safe_dump')
    def test_node_disks_download_yaml(self, m_safe_dump):
        args = 'node disks download --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/disks.yaml'

        self.m_client.get_disks.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_disks.assert_called_once_with(42)

    def test_node_disks_upload_yaml(self):
        args = 'node disks upload --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/disks.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(test_data))
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_disks.assert_called_once_with(42, test_data)

    @mock.patch('yaml.safe_dump')
    def test_node_disks_getdefault_yaml(self, m_safe_dump):
        args = 'node disks get-default --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/disks.yaml'

        self.m_client.get_default_disks.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_default_disks.assert_called_once_with(42)

    def test_node_delete_specific_labels_for_specific_nodes(self):
        labels_keys = ['key_1', 'key_2']
        node_ids = ['42', '43']
        args = 'node label delete -l {labels} --nodes {node_ids}'.format(
            labels=' '.join(labels_keys), node_ids=' '.join(node_ids))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.delete_labels_for_nodes.assert_called_once_with(
            labels=labels_keys, node_ids=node_ids)

    def test_node_delete_all_labels_for_all_nodes(self):
        args = 'node label delete --labels-all --nodes-all'

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.delete_labels_for_nodes.assert_called_once_with(
            labels=None, node_ids=None)

    def test_node_delete_all_labels_for_specific_nodes(self):
        node_ids = ['42', '43']
        args = 'node label delete --labels-all --nodes {node_ids}'.format(
            node_ids=' '.join(node_ids))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.delete_labels_for_nodes.assert_called_once_with(
            labels=None, node_ids=node_ids)

    def test_node_label_delete_by_value(self):
        labels = ['key_1', 'key_2=value2']
        node_ids = ['42', '43']
        args = 'node label delete -l {labels} --nodes {node_ids}'.format(
            labels=' '.join(labels), node_ids=' '.join(node_ids))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.delete_labels_for_nodes.assert_called_once_with(
            labels=labels, node_ids=node_ids)

    def test_node_label_delete_by_value_with_whitespace(self):
        labels = ['key_1', "'key_2   =value2'"]
        labels_expected = [x.strip("'") for x in labels]
        node_ids = ['42', '43']
        args = 'node label delete -l {labels} --nodes {node_ids}'.format(
            labels=' '.join(labels), node_ids=' '.join(node_ids))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.delete_labels_for_nodes.assert_called_once_with(
            labels=labels_expected, node_ids=node_ids)

    def test_node_attributes_download(self):
        args = 'node attributes-download 42'

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.download_attributes.assert_called_once_with(42, None)

    def test_node_attributes_upload(self):
        args = 'node attributes-upload 42'

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.upload_attributes.assert_called_once_with(42, None)

    @mock.patch('json.dump')
    def test_node_interfaces_download_json(self, m_dump):
        args = 'node interfaces download --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/interfaces.json'

        self.m_client.get_interfaces.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_interfaces.assert_called_once_with(42)

    def test_node_interfaces_upload_json(self):
        args = 'node interfaces upload --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/interfaces.json'

        m_open = mock.mock_open(read_data=json.dumps(test_data))
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_interfaces.assert_called_once_with(42, test_data)

    @mock.patch('json.dump')
    def test_node_interfaces_getdefault_json(self, m_dump):
        args = 'node interfaces get-default --format json -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/interfaces.json'

        self.m_client.get_default_interfaces.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_dump.assert_called_once_with(test_data, mock.ANY, indent=4)
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_default_interfaces.assert_called_once_with(42)

    @mock.patch('yaml.safe_dump')
    def test_node_interfaces_download_yaml(self, m_safe_dump):
        args = 'node interfaces download --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/interfaces.yaml'

        self.m_client.get_interfaces.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_interfaces.assert_called_once_with(42)

    def test_node_interfaces_upload_yaml(self):
        args = 'node interfaces upload --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/interfaces.yaml'

        m_open = mock.mock_open(read_data=yaml.dump(test_data))
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'r')
        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.set_interfaces.assert_called_once_with(42, test_data)

    @mock.patch('yaml.safe_dump')
    def test_node_interfaces_getdefault_yaml(self, m_safe_dump):
        args = 'node interfaces get-default --format yaml -d /tmp 42'
        test_data = {'foo': 'bar'}
        expected_path = '/tmp/node_42/interfaces.yaml'

        self.m_client.get_default_interfaces.return_value = test_data

        m_open = mock.mock_open()
        with mock.patch('fuelclient.commands.node.open', m_open, create=True):
            self.exec_command(args)

        m_open.assert_called_once_with(expected_path, 'w')
        m_safe_dump.assert_called_once_with(test_data, mock.ANY,
                                            default_flow_style=False)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_default_interfaces.assert_called_once_with(42)

    def test_undiscover_nodes_by_id(self):
        args = 'node undiscover -n 24'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.undiscover_nodes.assert_called_once_with(
            env_id=None, node_id=24, force=False)

    def test_undiscover_nodes_by_id_force(self):
        args = 'node undiscover -n 24 --force'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.undiscover_nodes.assert_called_once_with(
            env_id=None, node_id=24, force=True)

    def test_undiscover_nodes_by_cluster_id(self):
        args = 'node undiscover -e 45'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.undiscover_nodes.assert_called_once_with(
            env_id=45, node_id=None, force=False)

    def test_undiscover_nodes_by_cluster_id_force(self):
        args = 'node undiscover -e 45 --force'
        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.undiscover_nodes.assert_called_once_with(
            env_id=45, node_id=None, force=True)

    @mock.patch('sys.stderr')
    def test_undiscover_nodes_w_wrong_params(self, mocked_stderr):
        args = 'node undiscover -e 45 -n 24'
        self.assertRaises(SystemExit, self.exec_command, args)
        self.assertIn('argument -n/--node: not allowed with argument -e/--env',
                      mocked_stderr.write.call_args_list[-1][0][0])
