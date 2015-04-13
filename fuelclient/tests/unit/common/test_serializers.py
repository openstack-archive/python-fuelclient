# -*- coding: utf-8 -*-

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

from fuelclient.cli.serializers import Serializer
from fuelclient.tests import base


class TestSerializers(base.UnitTestCase):

    DATA = {
        'a': 1,
        'b': {
            'c': [2, 3, 4],
            'd': 'string',
        }
    }

    def test_get_from_params(self):
        params_to_formats = (
            ('yaml', 'yaml'),
            ('json', 'json'),
            ('xyz', Serializer.default_format),
        )
        for param, format in params_to_formats:
            params = mock.Mock(serialization_format=format)
            serializer = Serializer.from_params(params)
            self.assertEqual(serializer.format, format)

    def test_serialize(self):
        deserializers = {'json': json.loads, 'yaml': yaml.load}
        for format, deserialize in six.iteritems(deserializers):
            serialized = Serializer(format).serialize(self.DATA)
            self.assertEqual(self.DATA, deserialize(serialized))

    def test_deserialize(self):
        serializers = {'json': json.dumps, 'yaml': yaml.safe_dump}
        for format, serialize in six.iteritems(serializers):
            serialized = serialize(self.DATA)
            deserialized = Serializer(format).deserialize(serialized)
            self.assertEqual(self.DATA, deserialized)
