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

import mock
import os
import yaml

import fuelclient
from fuelclient.cli import error
from fuelclient.cli import serializers
from fuelclient.objects import base as base_object
from fuelclient.objects import fuelversion as fuelversion_object
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestNodeFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestNodeFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/nodes/'.format(version=self.version)

        self.fake_node = utils.get_fake_node()
        self.fake_nodes = [utils.get_fake_node() for _ in range(10)]

        self.client = fuelclient.get_client('node', self.version)

    def test_node_list(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_nodes)
        self.client.get_all()

        self.assertTrue(matcher.called)

    def test_node_list_with_labels(self):
        labels = ['key1']
        fake_nodes = [
            utils.get_fake_node(
                node_name='node_1', labels={'key1': 'val1'}),
            utils.get_fake_node(
                node_name='node_2', labels={'key2': 'val2'}),
            utils.get_fake_node(
                node_name='node_3', labels={'key1': 'val2', 'key3': 'val3'})
        ]

        matcher_get = self.m_request.get(self.res_uri, json=fake_nodes)

        data = self.client.get_all(labels=labels)

        self.assertTrue(matcher_get.called)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'node_1')
        self.assertEqual(data[1]['name'], 'node_3')

    def test_node_show(self):
        node_id = 42
        expected_uri = self.get_object_uri(self.res_uri, node_id)

        matcher = self.m_request.get(expected_uri, json=self.fake_node)

        self.client.get_by_id(node_id)

        self.assertTrue(matcher.called)

    @mock.patch.object(fuelversion_object.FuelVersion, 'get_feature_groups')
    def test_node_vms_list(self, m_feature_groups):
        node_id = 42
        expected_uri = "/api/v1/nodes/{0}/vms_conf/".format(node_id)
        m_feature_groups.return_value = \
            utils.get_fake_fuel_version()['feature_groups']

        fake_vms = [{'id': 1, 'opt2': 'val2'},
                    {'id': 2, 'opt4': 'val4'}]
        matcher = self.m_request.get(expected_uri, json=fake_vms)

        self.client.get_node_vms_conf(node_id)

        self.assertTrue(matcher.called)

    @mock.patch.object(fuelversion_object.FuelVersion, 'get_feature_groups')
    def test_node_vms_create(self, m_feature_groups):
        config = [{'id': 1, 'opt2': 'val2'},
                  {'id': 2, 'opt4': 'val4'}]
        node_id = 42
        m_feature_groups.return_value = \
            utils.get_fake_fuel_version()['feature_groups']

        expected_uri = "/api/v1/nodes/{0}/vms_conf/".format(node_id)
        expected_body = {'vms_conf': config}

        matcher = self.m_request.put(expected_uri, json=expected_body)

        self.client.node_vms_create(node_id, config)

        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.json())

    def test_node_set_hostname(self):
        node_id = 42
        hostname = 'test-name'
        data = {"hostname": hostname}
        expected_uri = self.get_object_uri(self.res_uri, node_id)

        matcher = self.m_request.put(expected_uri, json=data)

        self.client.update(node_id, **data)

        self.assertTrue(matcher.called)
        self.assertEqual(data, matcher.last_request.json())

    def test_get_all_labels_for_all_nodes(self):
        matcher = self.m_request.get(self.res_uri, json=self.fake_nodes)
        self.client.get_all_labels_for_nodes()

        self.assertTrue(matcher.called)

    def test_set_labels_for_all_nodes(self):
        labels = ['key_1=val_1', 'key_2=val_2', 'key_3   =   val_4']
        data = {'labels': {
            'key_1': 'val_1',
            'key_2': 'val_2',
            'key_3': 'val_4'
        }}

        expected_uri = self.get_object_uri(self.res_uri, 42)

        matcher_get = self.m_request.get(self.res_uri, json=self.fake_nodes)
        matcher_put = self.m_request.put(expected_uri, json=data)

        self.client.set_labels_for_nodes(labels=labels)

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertEqual(data, matcher_put.last_request.json())

    def test_set_labels_for_specific_nodes(self):
        labels = ['key_1=val_1', 'key_2=val_2', 'key_3   =   val_4']
        node_ids = ['42']
        data = {'labels': {
            'key_1': 'val_1',
            'key_2': 'val_2',
            'key_3': 'val_4'
        }}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        matcher_get = self.m_request.get(expected_uri, json=self.fake_node)
        matcher_put = self.m_request.put(expected_uri, json=data)

        self.client.set_labels_for_nodes(labels=labels, node_ids=node_ids)

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertEqual(data, matcher_put.last_request.json())

    def test_set_labels_with_empty_key(self):
        labels = ['key_1=val_1', ' =   val_2', 'key_3   = ']
        node_ids = ['42']

        msg = 'Wrong label "{0}" was provided. Label key couldn\'t ' \
              'be an empty string.'.format(labels[1])
        with self.assertRaisesRegexp(error.LabelEmptyKeyError, msg):
            self.client.set_labels_for_nodes(labels=labels, node_ids=node_ids)

    def test_delete_specific_labels_for_all_nodes(self):
        labels = ['key_1', '   key_3   ']
        data = {'labels': {'key_2': None}}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        matcher_get = self.m_request.get(self.res_uri, json=self.fake_nodes)
        matcher_put = self.m_request.put(expected_uri, json=data)

        self.client.delete_labels_for_nodes(labels=labels)

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertEqual(data, matcher_put.last_request.json())

    def test_delete_specific_labels_for_specific_nodes(self):
        labels = ['key_2']
        node_ids = ['42']
        data = {'labels': {'key_1': 'val_1', 'key_3': 'val_3'}}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        matcher_get = self.m_request.get(expected_uri, json=self.fake_node)
        matcher_put = self.m_request.put(expected_uri, json=data)

        self.client.delete_labels_for_nodes(labels=labels, node_ids=node_ids)

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertEqual(data, matcher_put.last_request.json())

    def test_delete_all_labels_for_all_nodes(self):
        data = {'labels': {}}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        matcher_get = self.m_request.get(self.res_uri, json=self.fake_nodes)
        matcher_put = self.m_request.put(expected_uri, json=data)

        self.client.delete_labels_for_nodes(labels=None)

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertEqual(data, matcher_put.last_request.json())

    def test_delete_all_labels_for_specific_nodes(self):
        node_ids = ['42']
        data = {'labels': {}}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        matcher_get = self.m_request.get(expected_uri, json=self.fake_node)
        matcher_put = self.m_request.put(expected_uri, json=data)

        self.client.delete_labels_for_nodes(labels=None, node_ids=node_ids)

        self.assertTrue(matcher_get.called)
        self.assertTrue(matcher_put.called)
        self.assertEqual(data, matcher_put.last_request.json())

    def test_delete_labels_by_value(self):
        labels = ['key_1=val_1', 'key_3=anothervalue', 'key_2']
        node_ids = ['42']
        result_labels = {'labels': {'key_3': 'val_3'}}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        self.m_request.get(expected_uri, json=self.fake_node)
        matcher_put = self.m_request.put(expected_uri, json=self.fake_node)

        self.client.delete_labels_for_nodes(
            labels=labels, node_ids=node_ids)

        self.assertTrue(matcher_put.called)
        self.assertEqual(result_labels, matcher_put.last_request.json())

    def test_delete_labels_by_value_with_whitespace(self):
        labels = ['key_1    =val_1', 'key_3=    anothervalue', 'key_2']
        node_ids = ['42']
        result_labels = {'labels': {'key_3': 'val_3'}}
        expected_uri = self.get_object_uri(self.res_uri, 42)

        self.m_request.get(expected_uri, json=self.fake_node)
        matcher_put = self.m_request.put(expected_uri, json=self.fake_node)

        self.client.delete_labels_for_nodes(
            labels=labels, node_ids=node_ids)

        self.assertTrue(matcher_put.called)
        self.assertEqual(result_labels, matcher_put.last_request.json())

    def test_get_name_and_value_from_labels(self):
        for label in (
            'key=value',
            '   key   =value',
            'key=    value    ',
            '  key  =  value   ',
        ):
            name, value, has_separator = self.client._split_label(label)
            self.assertEqual(name, 'key')
            self.assertEqual(value, 'value')
            self.assertTrue(has_separator)

    def test_get_name_and_empty_value_from_lables(self):
        for label in (
            'key=',
            '   key   =',
            'key=        ',
            '  key  =     ',
        ):
            name, value, has_separator = self.client._split_label(label)
            self.assertEqual(name, 'key')
            self.assertIsNone(value)
            self.assertTrue(has_separator)

    def test_get_name_without_separator(self):
        for label in (
            'key',
            '   key   ',
        ):
            name, value, has_separator = self.client._split_label(label)
            self.assertEqual(name, 'key')
            self.assertIsNone(value)
            self.assertFalse(has_separator)

    def test_label_with_many_separators(self):
        label = 'key1=  key2  = val2'
        name, value, has_separator = self.client._split_label(label)
        self.assertEqual(name, 'key1')
        self.assertEqual(value, 'key2  = val2')
        self.assertTrue(has_separator)

    def test_labels_after_delete(self):
        all_labels = {
            'label_A': 'A',
            'label_B': None,
            'label_C': 'C',
            'label_D': None,
        }
        expected_labels = {
            'label_A': 'A',
            'label_D': None,
        }

        for labels_to_delete in (
            ('label_B', 'label_C'),
            ('   label_B', 'label_C   '),
            ('label_B', 'label_C  ', 'unknown_label'),
            ('label_A =   trololo', 'label_B=', 'label_C =C', 'label_D=value')
        ):
            result = self.client._labels_after_delete(
                all_labels, labels_to_delete)
            self.assertEqual(result, expected_labels)

    @mock.patch.object(base_object.BaseObject, 'init_with_data')
    def test_node_update(self, m_init):
        node_id = 42
        expected_uri = self.get_object_uri(self.res_uri, node_id)

        get_matcher = self.m_request.get(expected_uri, json=self.fake_node)
        upd_matcher = self.m_request.put(expected_uri, json=self.fake_node)

        self.client.update(node_id, hostname="new-name")

        self.assertTrue(expected_uri, get_matcher.called)
        self.assertTrue(expected_uri, upd_matcher.called)

        req_data = upd_matcher.last_request.json()
        self.assertEqual('new-name', req_data['hostname'])

    def test_node_update_wrong_attribute(self):
        node_id = 42
        self.assertRaises(error.BadDataException,
                          self.client.update, node_id, status=42)

    @mock.patch('fuelclient.objects.node.os.mkdir', mock.Mock())
    def test_node_attributes_download(self):
        node_id = 42
        expected_uri = self.get_object_uri(
            self.res_uri, node_id, '/attributes/')
        fake_attributes = {
            'attribute_name': 'attribute_value'
        }

        m_get = self.m_request.get(expected_uri, json=fake_attributes)

        m_open = mock.mock_open()
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.download_attributes(node_id, directory='/fake/dir')

        self.assertTrue(m_get.called)
        m_open.assert_called_once_with(
            '/fake/dir/node_{0}/attributes.yaml'.format(node_id), mock.ANY)
        serializer = serializers.Serializer()
        m_open().write.assert_called_once_with(
            serializer.serialize(fake_attributes))

    def test_node_disks_upload(self):
        node_id = 42
        new_disks = {'test_key': u'test ☃ value'}

        node_uri = self.get_object_uri(self.res_uri, node_id)
        disks_uri = os.path.join(node_uri, 'disks/')

        get_matcher = self.m_request.get(node_uri, json=self.fake_node)
        upd_matcher = self.m_request.put(disks_uri, json={})

        self.client.set_disks(node_id, new_disks)

        self.assertTrue(node_uri, get_matcher.called)
        self.assertTrue(disks_uri, upd_matcher.called)

        req_data = upd_matcher.last_request.json()
        self.assertEqual(new_disks, req_data)

    def test_node_disks_download(self):
        node_id = 42
        fake_resp = {'test_key': u'test ☃ value'}

        node_uri = self.get_object_uri(self.res_uri, node_id)
        disks_uri = os.path.join(node_uri, 'disks/')

        node_matcher = self.m_request.get(node_uri, json=self.fake_node)
        disks_matcher = self.m_request.get(disks_uri, json=fake_resp)

        disks = self.client.get_disks(node_id)

        self.assertTrue(node_uri, node_matcher.called)
        self.assertTrue(disks_uri, disks_matcher.called)

        self.assertEqual(disks, fake_resp)

    def test_node_disks_defaults(self):
        node_id = 42
        fake_resp = {'test_key': u'test ☃ value'}

        node_uri = self.get_object_uri(self.res_uri, node_id)
        disks_uri = os.path.join(node_uri, 'disks/defaults')

        node_matcher = self.m_request.get(node_uri, json=self.fake_node)
        disks_matcher = self.m_request.get(disks_uri, json=fake_resp)

        disks = self.client.get_default_disks(node_id)

        self.assertTrue(node_uri, node_matcher.called)
        self.assertTrue(disks_uri, disks_matcher.called)

        self.assertEqual(disks, fake_resp)

    @mock.patch('fuelclient.objects.node.os.path.exists',
                mock.Mock(return_value=True))
    def test_node_attribute_upload(self):
        node_id = 42
        expected_uri = self.get_object_uri(
            self.res_uri, node_id, '/attributes/')
        fake_attributes = {
            'attribute_name': 'attribute_value'
        }

        m_put = self.m_request.put(expected_uri, json=fake_attributes)

        m_open = mock.mock_open(read_data=yaml.safe_dump(fake_attributes))
        with mock.patch('fuelclient.cli.serializers.open',
                        m_open, create=True):
            self.client.upload_attributes(node_id, directory='/fake/dir')

        self.assertTrue(m_put.called)
        m_open.assert_called_once_with(
            '/fake/dir/node_{0}/attributes.yaml'.format(node_id), mock.ANY)
        self.assertEqual(m_put.last_request.json(), fake_attributes)
        m_open().read.assert_called_once_with()

    def test_node_interfaces_upload(self):
        node_id = 42
        new_interfaces = {'test_key': u'test ☃ value'}

        node_uri = self.get_object_uri(self.res_uri, node_id)
        interfaces_uri = os.path.join(node_uri, 'interfaces/')

        get_matcher = self.m_request.get(node_uri, json=self.fake_node)
        upd_matcher = self.m_request.put(interfaces_uri, json={})

        self.client.set_interfaces(node_id, new_interfaces)

        self.assertTrue(node_uri, get_matcher.called)
        self.assertTrue(interfaces_uri, upd_matcher.called)

        req_data = upd_matcher.last_request.json()
        self.assertEqual(new_interfaces, req_data)

    def test_node_interfaces_download(self):
        node_id = 42
        fake_resp = {'test_key': u'test ☃ value'}

        node_uri = self.get_object_uri(self.res_uri, node_id)
        interfaces_uri = os.path.join(node_uri, 'interfaces/')

        node_matcher = self.m_request.get(node_uri, json=self.fake_node)
        interfaces_matcher = self.m_request.get(interfaces_uri, json=fake_resp)

        interfaces = self.client.get_interfaces(node_id)

        self.assertTrue(node_uri, node_matcher.called)
        self.assertTrue(interfaces_uri, interfaces_matcher.called)

        self.assertEqual(interfaces, fake_resp)

    def test_node_interfaces_default(self):
        node_id = 42
        fake_resp = {'test_key': u'test ☃ value'}

        node_uri = self.get_object_uri(self.res_uri, node_id)
        interfaces_uri = os.path.join(node_uri,
                                      'interfaces/default_assignment')

        node_matcher = self.m_request.get(node_uri, json=self.fake_node)
        interfaces_matcher = self.m_request.get(interfaces_uri, json=fake_resp)

        interfaces = self.client.get_default_interfaces(node_id)

        self.assertTrue(node_uri, node_matcher.called)
        self.assertTrue(interfaces_uri, interfaces_matcher.called)

        self.assertEqual(interfaces, fake_resp)

    def test_undiscover_nodes_by_id_force(self):
        node_id = 42
        expected_uri = '/api/v1/nodes/?ids={node_id}'.format(node_id=node_id)
        request_url = self.get_object_uri(self.res_uri, node_id)

        node_matcher = self.m_request.get(request_url, json=self.fake_node)
        matcher = self.m_request.delete(expected_uri, json={})

        self.client.undiscover_nodes(node_id=node_id, force=True)

        self.assertTrue(matcher.called)
        self.assertTrue(node_matcher.called)
        self.assertEqual([str(node_id)], matcher.last_request.qs.get('ids'))

    def test_undiscover_nodes_by_id(self):
        node_id = 42
        expected_uri = self.get_object_uri(self.res_uri, node_id)
        node_matcher = self.m_request.get(expected_uri, json=self.fake_node)

        self.assertRaises(error.ActionException,
                          self.client.undiscover_nodes,
                          node_id=node_id, force=False)
        self.assertTrue(node_matcher.called)

    def test_undiscover_nodes_by_env_force(self):
        env_id = 24
        node_ids = ['42', '43', '44']
        expected_uri = '/api/v1/nodes/?ids={node_ids}'.format(
            node_ids=','.join(node_ids))
        fake_nodes = [utils.get_fake_node(node_name='node_' + n_id,
                                          node_id=n_id,
                                          cluster=env_id) for n_id in node_ids]

        nodes_matcher = self.m_request.get(self.res_uri, json=fake_nodes)
        matcher = self.m_request.delete(expected_uri, json={})

        self.client.undiscover_nodes(env_id=env_id, node_id=None, force=True)

        self.assertTrue(matcher.called)
        self.assertTrue(nodes_matcher.called)
        self.assertEqual([','.join(node_ids)],
                         matcher.last_request.qs.get('ids'))

    def test_undiscover_nodes_by_env(self):
        env_id = 24
        node_ids = ['42', '43', '44']
        fake_nodes = [utils.get_fake_node(node_name='node_' + n_id,
                                          node_id=n_id,
                                          cluster=env_id) for n_id in node_ids]
        nodes_matcher = self.m_request.get(self.res_uri, json=fake_nodes)

        self.assertRaises(error.ActionException,
                          self.client.undiscover_nodes,
                          env_id=env_id, node_id=None, force=False)
        self.assertTrue(nodes_matcher.called)

    def test_undiscover_nodes_w_wrong_params(self):
        env_id = None
        node_id = None

        self.assertRaises(ValueError,
                          self.client.undiscover_nodes,
                          env_id=env_id, node_id=node_id, force=False)
