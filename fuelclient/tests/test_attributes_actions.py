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

from mock import patch

from fuelclient.tests import base


@patch('fuelclient.client.requests')
@patch('fuelclient.cli.serializers.open', create=True)
@patch('fuelclient.cli.actions.base.os')
class TestClusterAttributesActions(base.UnitTestCase):

    _input = {
        'editable': {
            'test': 'foo',
        }}

    _output = 'editable:\n  test: foo\n'

    def test_attributes_download(self, mos, mopen, mrequests):
        mrequests.get().json.return_value = self._input
        self.execute(
            ['fuel', 'env', '--env', '1', '--attributes', '--download'])

        url = mrequests.get.call_args[0][0]
        self.assertIn('clusters/1/attributes', url)

        mopen().__enter__().write.assert_called_once_with(self._output)

    def test_attributes_upload(self, mos, mopen, mrequests):
        mopen().__enter__().read.return_value = self._output
        self.execute(
            ['fuel', 'env', '--env', '1', '--attributes', '--upload'])
        self.assertEqual(mrequests.put.call_count, 1)

        call_args = mrequests.put.call_args_list[0]
        url = call_args[0][0]
        kwargs = call_args[1]

        self.assertIn('clusters/1/attributes', url)
        self.assertEqual(json.loads(kwargs['data']), self._input)
