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

from mock import patch

from fuelclient.tests.unit.v1 import base


@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestClusterAttributesActions(base.UnitTestCase):

    _input = {
        'editable': {
            'test': 'foo',
        }}

    _output = 'editable:\n  test: foo\n'

    def test_attributes_download(self, mos, mopen):
        get = self.m_request.get('/api/v1/clusters/1/attributes',
                                 json=self._input)

        self.execute(
            ['fuel', 'env', '--env', '1', '--attributes', '--download'])

        self.assertTrue(get.called)

        mopen().__enter__().write.assert_called_once_with(self._output)

    def test_attributes_upload(self, mos, mopen):
        mopen().__enter__().read.return_value = self._output
        put = self.m_request.put('/api/v1/clusters/1/attributes', json={})

        self.execute(
            ['fuel', 'env', '--env', '1', '--attributes', '--upload'])

        self.assertTrue(put.called)
        self.assertEqual(put.last_request.json(), self._input)
