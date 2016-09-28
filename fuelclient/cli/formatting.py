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

from itertools import chain
from operator import itemgetter
from time import sleep

import six


def format_table(data, acceptable_keys=None, column_to_join=None):
    """Format list of dicts to table in a string form

    :acceptable_keys list(str): list of keys for which to create table
                                also specifies their order
    """

    # prepare columns
    if column_to_join is not None:
        for data_dict in data:
            for column_name in column_to_join:
                data_dict[column_name] = u", ".join(
                    sorted(data_dict[column_name])
                )
    if acceptable_keys is not None:
        rows = [tuple(value.get(key, "") for key in acceptable_keys)
                for value in data]
        header = tuple(acceptable_keys)
    else:
        rows = [tuple(x.values()) for x in data]
        header = tuple(data[0].keys())
    number_of_columns = len(header)

    # split multi-lines cells if there is no automatic columns merge
    if column_to_join:
        def format_cell(cell):
            return [cell or ""]
    else:
        def format_cell(cell):
            return six.text_type(cell).split('\n')
    rows = [
        [format_cell(cell) if cell is not None else [''] for cell in row]
        for row in rows
    ]

    # calculate columns widths
    column_widths = dict(
        zip(
            range(number_of_columns),
            (len(str(x)) for x in header)
        )
    )
    for row in rows:
        column_widths.update(
            (
                index,
                max(
                    column_widths[index],
                    max(len(six.text_type(line)) for line in cell)
                )
            )
            for index, cell in enumerate(row)
        )

    # make output
    hor_delimeter = u'-+-'.join(column_widths[column_index] * u'-'
                                for column_index in range(number_of_columns))

    row_template = u' | '.join(
        u"{{{0}:{1}}}".format(idx, width)
        for idx, width in column_widths.items()
    )

    output_lines = [
        row_template.format(*header),
        hor_delimeter
    ]

    for row in rows:
        max_cell_lines = max(len(cell) for cell in row)
        for cell_line_no in range(max_cell_lines):
            output_lines.append(
                row_template.format(
                    *(
                        cell[cell_line_no] if len(cell) > cell_line_no else u""
                        for cell in row
                    )
                )
            )
    return u'\n'.join(output_lines)


def quote_and_join(words):
    """quote_and_join - performs listing of objects and returns string.
    """
    words = list(words)
    if len(words) > 1:
        return '{0} and "{1}"'.format(
            ", ".join(
                ['"{0}"'.format(x) for x in words][:-1]
            ),
            words[-1]
        )
    else:
        return '"{0}"'.format(words[0])


# TODO(vkulanov): remove when deprecate old cli
def print_health_check(env):
    tests_states = [{"status": "not finished"}]
    finished_tests = set()
    test_counter, total_tests_count = 1, None
    while not all(map(
            lambda t: t["status"] == "finished",
            tests_states
    )):
        tests_states = env.get_state_of_tests()
        all_tests = list(chain(*map(
            itemgetter("tests"),
            filter(
                env.is_in_running_test_sets,
                tests_states
            ))))
        if total_tests_count is None:
            total_tests_count = len(all_tests)
        all_finished_tests = filter(
            lambda t: "running" not in t["status"],
            all_tests
        )
        new_finished_tests = filter(
            lambda t: t["name"] not in finished_tests,
            all_finished_tests
        )
        finished_tests.update(
            map(
                itemgetter("name"),
                new_finished_tests
            )
        )
        for test in new_finished_tests:
            print(
                u"[{0:2} of {1}] [{status}] '{name}' "
                u"({taken:.4} s) {message}".format(
                    test_counter,
                    total_tests_count,
                    **test
                )
            )
            test_counter += 1
        sleep(1)
