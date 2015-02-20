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

import subprocess
import yaml
import glob

from distutils.version import StrictVersion

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


def exec_cmd(cmd, cwd=None, stdout=None):
    """Execute shell command logging.

    :param str cmd: shell command
    :param str cwd: None is default
    """
    child = subprocess.Popen(
        cmd, stdout=stdout,
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



def parse_yaml(path):
    """
    """
    return yaml.load(open(path).read())


def walk_mask(path):
    """
    """
    for f in glob.iglob(path):
        yield f


def walk_and_parse_yaml(path):
    """
    """
    for f in glob.iglob(path):
        yield parse_yaml(f)


def major_version(version):
    """
    """
    version_tuple = StrictVersion(version).version
    major = '.'.join(map(str, version_tuple[:2]))

    return major
