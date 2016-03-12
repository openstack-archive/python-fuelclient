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
import six

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
        self.m_client.get_all.assert_called_once_with(
            environment_id=None, labels=None)

    def test_node_list_with_env(self):
        env_id = 42
        args = 'node list --env {env}'.format(env=env_id)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(
            environment_id=env_id, labels=None)

    def test_node_list_with_labels(self):
        labels = ['key_1=val_1', 'key_2=val_2', 'key3']
        args = 'node list --labels {labels}'.format(
            labels=' '.join(labels))

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.get_all.assert_called_once_with(
            environment_id=None, labels=labels)

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
        with mock.patch('sys.stdout', new=io.StringIO()) as mstdout:
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

    def test_node_set_hostname(self):
        self.m_client._updatable_attributes = \
            node.NodeClient._updatable_attributes
        node_id = 42
        hostname = 'test-name'

        self.m_client.update.return_value = \
            fake_node.get_fake_node(node_id=node_id,
                                    hostname=hostname)

        args = 'node update {node_id} --hostname {hostname}'\
            .format(node_id=node_id, hostname=hostname)

        self.exec_command(args)

        self.m_get_client.assert_called_once_with('node', mock.ANY)
        self.m_client.update.assert_called_once_with(
            node_id, hostname=hostname)

    def test_node_set_name(self):
        self.m_client._updatable_attributes = \
            node.NodeClient._updatable_attributes
        node_id = 37

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
