# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

from fuelclient.commands.release import ReleaseComponentList
from fuelclient.tests.unit.v1 import base


class TestReleaseComponent(base.UnitTestCase):

    def test_retrieve_predicates(self):
        predicates = ('any_of', 'all_of', 'one_of', 'none_of')
        items = {
            "items": ["fake:component:1",
                      "fake:component:2"]
        }

        for predicate in predicates:
            test_data = {predicate: items}
            real_data = ReleaseComponentList.retrieve_predicates(test_data)
            expected_data = "{} (fake:component:1, fake:component:2)".format(
                predicate)
            self.assertEqual(expected_data, real_data)

    def test_retrieve_predicates_w_wrong_predicate(self):
        test_data = {
            "bad_predicate": {
                "items": ["fake:component:1",
                          "fake:component:2"],
            }
        }

        self.assertRaisesRegexp(ValueError,
                                "Predicates not found.",
                                ReleaseComponentList.retrieve_predicates,
                                test_data)

    def test_retrieve_data(self):
        test_data = "fake:component:1"
        real_data = ReleaseComponentList.retrieve_data(test_data)
        self.assertEqual("fake:component:1", real_data)

        test_data = [{"name": "fake:component:1"}]
        real_data = ReleaseComponentList.retrieve_data(test_data)
        self.assertEqual("fake:component:1", real_data)

        test_data = [
            {
                "one_of": {
                    "items": ["fake:component:1"]
                }
            },
            {
                "any_of": {
                    "items": ["fake:component:1",
                              "fake:component:2"]
                }
            },
            {
                "all_of": {
                    "items": ["fake:component:1",
                              "fake:component:2"]
                }
            },
            {
                "none_of": {
                    "items": ["fake:component:1"]
                }
            }
        ]
        real_data = ReleaseComponentList.retrieve_data(test_data)
        expected_data = ("one_of (fake:component:1), "
                         "any_of (fake:component:1, fake:component:2), "
                         "all_of (fake:component:1, fake:component:2), "
                         "none_of (fake:component:1)")
        self.assertEqual(expected_data, real_data)
