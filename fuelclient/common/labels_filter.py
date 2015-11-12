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

import re
import six

# tokenizer regexps
RE_QUOTES = r"['\"]"
RE_QUOTES_COMP = re.compile(RE_QUOTES)
RE_OPERATOR = r"[\;\=\(\)]"
RE_WORD = r"[^ \;\=\(\)]+"

RE_QUOTED_STRING = r"(?P<quote>(?<![\\])['\"])" \
                   r"((?:.(?!(?<![\\])(?P=quote)))*.?)" \
                   r"(?P=quote)"
RE_TOKENS_COMP = re.compile(
    r"((" + RE_QUOTED_STRING + ")|(" + RE_OPERATOR + ")|(" + RE_WORD + "))"
)

L, R = "left", "right"


class Operator(object):
    """Operator is base class describing how expression operator is
    identified in expression (symbol), it's association with
    operands position and evaluation weight (precedence).

    """
    symbol = None
    association = L
    precedence = 0

    @staticmethod
    def _eval_operand(operand, ctx):
        """For string operand check it's presence in context
        or just boolify it in all other cases.

        :param bool|str operand:
        :param dict ctx: context
        :return boolean:
        """
        if isinstance(operand, six.string_types):
            return operand in ctx
        else:
            return bool(operand)

    @classmethod
    def from_infix_to_rpn(cls, stack, out):
        """This function describing logic that places
        operator to the reverse polish notation.
        :param list stack: shunting yard stack mutable
        :param list out: shunting yard output queue mutable
        :return:
        """
        while len(stack) and issubclass(stack[-1], Operator):
            if ((cls.association is L) and (
                    cls.precedence - stack[-1].precedence <= 0)) or (
                (cls.association is R) and (
                    cls.precedence - stack[-1].precedence < 0)):
                out.append(stack.pop())
                continue
            break
        stack.append(cls)

    @classmethod
    def evaluate(cls, operands_stack, ctx):
        """Applies operator to the operands queue. Implementation is
        not required.
        :param list operands_stack:
        :param dict ctx: is the context of operator evaluation, for labels
        filter it is dict of labels.
        :return:
        """
        pass


class LeftParenthesesOperator(Operator):
    symbol = "("
    precedence = -1

    @classmethod
    def from_infix_to_rpn(cls, stack, out):
        stack.append(cls)


class EqualOperator(Operator):
    symbol = "="
    precedence = 5

    @classmethod
    def evaluate(cls, operands_stack, ctx):
        if len(operands_stack) < 2:
            raise ValueError
        v = operands_stack.pop()
        k = operands_stack.pop()
        if k not in ctx:
            # no such label
            operands_stack.append(False)
        else:
            operands_stack.append(ctx[k] == str(v))


class NotOperator(Operator):
    symbol = "not"
    precedence = 4

    @classmethod
    def evaluate(cls, operands_stack, ctx):
        if not len(operands_stack):
            raise ValueError
        a = operands_stack.pop()
        operands_stack.append(not cls._eval_operand(a, ctx))


class AndOperator(Operator):
    symbol = "and"
    precedence = 3

    @classmethod
    def evaluate(cls, operands_stack, ctx):
        if len(operands_stack) < 2:
            raise ValueError
        a = operands_stack.pop()
        b = operands_stack.pop()
        operands_stack.append(
            cls._eval_operand(a, ctx) and cls._eval_operand(b, ctx)
        )


class OrOperator(Operator):
    symbol = "or"
    precedence = 2

    @classmethod
    def evaluate(cls, operands_stack, ctx):
        if len(operands_stack) < 2:
            raise ValueError
        a = operands_stack.pop()
        b = operands_stack.pop()
        operands_stack.append(
            cls._eval_operand(a, ctx) or cls._eval_operand(b, ctx)
        )


class RightParenthesesOperator(Operator):
    symbol = ")"
    precedence = -1

    @classmethod
    def from_infix_to_rpn(cls, stack, out):
        while len(stack) and stack[-1] is not LeftParenthesesOperator:
            out.append(stack.pop())
        stack.pop()


class FinOperator(Operator):
    """Fin is implicit operator that cleanup all execution results
    and producing final decision as boolean.
    Though it could be declared explicitly with ; symbol.
    Empty output is considered as filter that always returning True.
    OR will be applied to output not combined with other operators
    and "aaa bbb" will be considered as "aaa OR bbb".
    """
    symbol = ";"
    precedence = -10

    @classmethod
    def evaluate(cls, operands_stack, ctx):
        # and is applied if there are many operands left
        if len(operands_stack) > 1:
            while len(operands_stack) > 1:
                OrOperator.evaluate(operands_stack, ctx)
        # last operand is matched or left intact
        if len(operands_stack) == 1:
            a = operands_stack.pop()
            operands_stack.append(cls._eval_operand(a, ctx))
        # or return true if there is empty expression
        # that should match everything
        else:
            operands_stack.append(True)

OPERATORS_LIST = [
    LeftParenthesesOperator,
    EqualOperator,
    NotOperator,
    AndOperator,
    OrOperator,
    RightParenthesesOperator
]

OPERATORS_DICT = dict((op.symbol, op) for op in OPERATORS_LIST)


class LabelsFilter(object):
    """Provides ability to evaluate boolean expressions against
    dictionaries of entity attributes.

    Expression example:
    "(label1 and label2=10) or not label3"

    Operands priority order is: = > not > and > or

    Unclosed parentheses will be closed automatically at the
    end of the expression.

    If the expression have invalid syntax
    like "aa or bb cc" the ValueError will be raised during .match call.
    """
    _matcher = None

    def __init__(self, expression):
        """:param str expression: boolean expression e.g.
        (aaa and b=10) or z
        """
        self._make_matcher(expression)

    def match(self, attr_dict):
        """Matches dictionary of fields with value against
        expression and returning True or False.
        :param dict attr_dict: dictionary of attributes strings
        :return bool:
        :raises ValueError:
        """
        operands_stack = []
        for op in self._matcher:
            if hasattr(op, "evaluate"):
                op.evaluate(operands_stack, attr_dict)
            else:
                operands_stack.append(op)
        return operands_stack[0]

    @staticmethod
    def _remove_quotes(string):
        if string[0] == string[-1] and RE_QUOTES_COMP.match(string[0]):
            return string[1: -1]
        else:
            return string

    @staticmethod
    def _tokenize(expression):
        """Make list of operators and operands tokens
        from the expression string.
        :param str expression:
        :return list:
        """
        return [g[0] for g in RE_TOKENS_COMP.findall(expression)]

    def _make_matcher(self, expression):
        """Make RPN notated matcher.
        :param expression:
        :return:
        """
        out = []
        stack = []
        for token in self._tokenize(expression):
            if token.lower() in OPERATORS_DICT:
                OPERATORS_DICT[token.lower()].from_infix_to_rpn(stack, out)
            else:
                out.append(self._remove_quotes(token))
        while len(stack):
            out.append(stack.pop())
        # entailing fin operator is required
        if (not out) or (out[-1] is not FinOperator):
            out.append(FinOperator)
        self._matcher = out
