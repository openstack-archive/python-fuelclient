# -*- coding: utf-8 -*-
#
#    Copyright 2014 Mirantis, Inc.
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

import sys

import mock

from fuelclient.common.labels_filter import LabelsFilter
from fuelclient.tests.unit.v1 import base


class TestUtils(base.UnitTestCase):

    def test_operators(self):
        test_data = {
            "aaa": "exist",
            "bbb": "exist"
        }
        expressions_and_results = (
            ("aaa and bbb", True, ),
            ("aaa and zzz", False, ),
            ("aaa or bbb", True, ),
            ("aaa or zzz", True, ),
            ("xxx or zzz", False, ),
            ("not bbb", False, ),
            ("not zzz", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_errors(self):

        test_data = {
            "aaa": "exist",
            "bbb": "exist"
        }
        expressions_and_results = (
            ("aaa and", "Invalid AND operator position or operands", ),
            ("aaa or", "Invalid OR operator position or operands", ),
            ("not", "Invalid NOT operator position or operands", ),
            ("(aaa) and bbb)", "Left parenthesis is missing", ),
            ("(aaa and (bbb)", "Right parenthesis is missing", )
        )

        for expression, result in expressions_and_results:
            with self.assertRaisesRegexp(ValueError, result):
                ef = LabelsFilter(expression)
                ef.match(test_data)

    def test_priority(self):
        test_data = {
            "true": "exist"
        }
        expressions_and_results = (
            ("true or true and false", True, ),
            ("not false or false and false", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_uppercase(self):
        test_data = {
            "true": "exist"
        }
        expressions_and_results = (
            ("NOT false OR false AND false", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_fin(self):
        test_data = {
            "true": "exist"
        }
        expressions_and_results = (
            ("", True, ),
            ("true", True, ),
            ("false", False, ),
            ("true true true", True, ),
            ("true true false", True, ),
            ("true true not false", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_parentheses(self):
        test_data = {
            "true": "exist"
        }
        expressions_and_results = (
            ("(true or true) and false", False, ),
            ("true or (true and false)", True, ),
            ("true and (true and false) or false", False, ),
            ("true and (true and false) or false", False, ),
            ("true and (true and (true and (true and false))) or false",
             False, ),
            ("true and not (true and (true and (true and false))) or false",
             True, ),
            ("(true)", True, ),
            ("(false)", False, ),
            ("true ()", True),
            ("false ()", False),
            ("() true", True),
            ("() false", False),
            ("()", True),
            ("true (true)", True),
            ("(true and true) and not (false and false)", True),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_spaces(self):
        test_data = {
            "true": "exist"
        }
        expressions_and_results = (
            ("  (     true or      false    ) and true    ", True, ),
            ("  (true or      false    ) and true    ", True, ),
            ("  (   true or      false) and true    ", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_quotes(self):
        test_data = {
            "true true": "exist",
            "true \" true": "exist",
            "true \' true": "exist"
        }
        expressions_and_results = (
            ("'true true'", True, ),
            ('"true true"', True, ),
            ("'true \" true'", True, ),
            ('"true \' true"', True, ),
            ('"true true" and "true true"', True, ),
            ("'true true' and 'true true'", True, ),
            ("'true true' or 'or'", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_escaped_same_quotes(self):
        test_data = {
            "true\\'true": "exist",
            'true\\"true': "exist"
        }
        expressions_and_results = (
            ("'true\\'true'", True, ),
            ('"true\\"true"', True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_bad_symbols(self):
        test_data = {
            "!@#$%^&*\(\)_+\=-][}{><.,/?\|": "exist",
            "定是无聊": "exist",
        }
        expressions_and_results = (
            ("'!@#$%^&*\(\)_+\=-][}{><.,/?\|'", True, ),
            ("定是无聊", True, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_equal_operator(self):
        test_data = {
            "true": "exist",
            "reallytrue": "exist",
        }
        expressions_and_results = (
            ("true=exist", True, ),
            ("true=notexist", False, ),
            ("reallytrue=exist and true=exist", True, ),
            ("reallytrue= exist and true =exist", True, ),
            ("reallytrue=notexist and true=exist", False, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)

    def test_escaped_equal_operator(self):
        test_data = {
            "double true": "i'm exist",
        }
        expressions_and_results = (
            ("\"double true\"=\"i'm exist\"", True, ),
            ("\"double true\"=oops", False, ),
        )

        for expression, result in expressions_and_results:
            ef = LabelsFilter(expression)
            self.assertEqual(ef.match(test_data), result)
