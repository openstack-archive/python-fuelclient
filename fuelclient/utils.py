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

from collections import defaultdict
import glob
import io
import json
import os
import six
import subprocess
import sys
import yaml


import dictdiffer
from distutils.version import StrictVersion
from fnmatch import fnmatch

from fuelclient.cli import error


def _wait_and_check_exit_code(cmd, child):
    """Wait for child and check it's exit code

    :param cmd: command
    :param child: object which returned by subprocess.Popen
    :raises: ExecutedErrorNonZeroExitCode
    """
    child.wait()
    exit_code = child.returncode

    if exit_code != 0:
        raise error.ExecutedErrorNonZeroExitCode(
            u'Shell command executed with "{0}" '
            'exit code: {1} '.format(exit_code, cmd))


def exec_cmd(cmd, cwd=None):
    """Execute shell command logging.

    :param str cmd: shell command
    :param str cwd: None is default
    """
    child = subprocess.Popen(
        cmd, stdout=None,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=cwd)

    _wait_and_check_exit_code(cmd, child)


def exec_cmd_iterator(cmd):
    """Execute command with logging.
    :param cmd: shell command
    :returns: generator where yeach item
              is line from stdout
    """
    child = subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)

    for line in child.stdout:
        yield line

    _wait_and_check_exit_code(cmd, child)


def parse_yaml_file(path):
    """Parses yaml

    :param str path: path to yaml file
    :returns: deserialized file
    """
    with io.open(path, encoding='utf-8') as f:
        data = yaml.load(f)

    return data


def glob_and_parse_yaml(path):
    """Parses yaml files by mask.

    :param str path: mask
    :returns: iterator
    """
    for f in glob.iglob(path):
        yield parse_yaml_file(f)


def major_plugin_version(version):
    """Retrieves major version.
    "1.2.3" -> "1.2"

    :param str version: version
    :returns: only major version
    """
    version_tuple = StrictVersion(version).version
    major = '.'.join(map(str, version_tuple[:2]))

    return major


def iterfiles(dir_path, file_pattern):
    """Returns generator where each item is a path to file, that satisfies
    file_patterns condtion

    :param dir_path: path to directory, e.g /etc/puppet/
    :param file_pattern: unix filepattern to match files
    """
    for root, dirs, file_names in os.walk(dir_path):
        for file_name in file_names:
            if fnmatch(file_name, file_pattern):
                yield os.path.join(root, file_name)


def file_exists(path):
    """Checks if file exists

    :param str path: path to the file
    :returns: True if file is exist, Flase if is not
    """
    return os.path.lexists(path)


def parse_to_list_of_dicts(str_list):
    """Parse list of json strings to dictionaries

    :param list: list of dicts and json string
    :returns" list of dictionaries

    """
    dict_list = []
    for json_str in str_list:
        if not isinstance(json_str, dict):
            try:
                json_str = json.loads(json_str)
            except Exception:
                raise error.BadDataException(
                    'Not valid JSON data: {0}'.format(json_str))
        dict_list.append(json_str)
    return dict_list


def str_to_unicode(string):
    """Normalize input string from command line to unicode standard.

    :param str string: string to normalize
    :returns: normalized string

    """
    return string if six.PY3 else string.decode(sys.getfilesystemencoding())


class DictDiffer(object):
    DIFF_MAP = {
        dictdiffer.ADD: 'ADDED:',
        dictdiffer.REMOVE: 'DELETED:',
        dictdiffer.CHANGE: '-->',
    }

    @classmethod
    def generate_diff(cls, dict1, dict2):
        cmp_dict = defaultdict(list)
        for change_type, path, change in dictdiffer.diff(dict1, dict2):
            path = '.'.join(map(str, path)) if isinstance(path, list) else path

            if change_type in (dictdiffer.ADD, dictdiffer.REMOVE):
                for index, value in sorted(change, key=lambda x: x[0]):
                    cmp_dict[path].append(
                        '{type} [{index}] {value}'.format(
                            type=cls.DIFF_MAP[change_type],
                            index=index,
                            value=value))

            elif change_type == dictdiffer.CHANGE:
                from_value, to_value = change
                cmp_dict[path].append(
                    '{from_value} {type} {to_value}'.format(
                        from_value=from_value,
                        type=cls.DIFF_MAP[change_type],
                        to_value=to_value))
        return cmp_dict

    @classmethod
    def pretty_str(cls, cmp_dict):
        pr_str = ''
        for path, values in sorted(six.iteritems(cmp_dict)):
            value = '\n'.join('    {0}'.format(v) for v in values)
            pr_str += '\n\n{0}\n{1}'.format(path, value)

        return pr_str.strip() or 'None'

    @classmethod
    def diff(cls, dict1, dict2):
        return cls.pretty_str(cls.generate_diff(dict1, dict2))
