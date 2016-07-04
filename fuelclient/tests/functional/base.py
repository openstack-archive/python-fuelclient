#    Copyright 2013-2014 Mirantis, Inc.
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
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

from fuelclient import consts
from fuelclient.objects import Release

from oslotest import base as oslo_base

logging.basicConfig(stream=sys.stderr)
log = logging.getLogger("CliTest.ExecutionLog")
log.setLevel(logging.DEBUG)


class CliExecutionResult(object):
    def __init__(self, process_handle, out, err):
        self.return_code = process_handle.returncode
        self.stdout = out
        self.stderr = err

    @property
    def has_errors(self):
        return self.return_code != 0

    @property
    def is_return_code_zero(self):
        return self.return_code == 0


class BaseTestCase(oslo_base.BaseTestCase):

    handler = ''
    nailgun_root = os.environ.get('NAILGUN_ROOT', '/tmp/fuel_web/nailgun')
    fuel_web_root = os.environ.get('FUEL_WEB_ROOT', '/tmp/fuel_web')

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.reload_nailgun_server()
        self.temp_directory = tempfile.mkdtemp()

        self.addCleanup(shutil.rmtree, self.temp_directory)

    @staticmethod
    def run_command(*args, **kwargs):
        handle = subprocess.Popen(
            [" ".join(args)],
            stdout=kwargs.pop('stdout', subprocess.PIPE),
            stderr=kwargs.pop('stderr', subprocess.PIPE),
            shell=kwargs.pop('shell', True),
            **kwargs
        )
        log.debug("Running " + " ".join(args))
        out, err = handle.communicate()
        log.debug("Finished command with {0} - {1}".format(out, err))

    def upload_command(self, cmd):
        return "{0} --upload --dir {1}".format(cmd, self.temp_directory)

    def download_command(self, cmd):
        return "{0} --download --dir {1}".format(cmd, self.temp_directory)

    @classmethod
    def reload_nailgun_server(cls):
        for action in ("dropdb", "syncdb", "loaddefault"):
            cmd = 'tox -evenv -- {0}/manage.py {1}'.format(
                cls.nailgun_root, action)
            cls.run_command(cmd, cwd=cls.fuel_web_root)

    @classmethod
    def load_data_to_nailgun_server(cls):
        file_path = os.path.join(cls.nailgun_root,
                                 'nailgun/fixtures/sample_environment.json')
        cmd = 'tox -evenv -- {0}/manage.py loaddata {1}'.format(
            cls.nailgun_root, file_path)
        cls.run_command(cmd, cwd=cls.fuel_web_root)

    def run_cli_command(self, command_line, handler=None,
                        check_errors=True, env=os.environ.copy()):

        command_args = [" ".join((handler or self.handler, command_line))]
        process_handle = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=env
        )
        out, err = process_handle.communicate()
        result = CliExecutionResult(process_handle, out, err)
        log.debug("command_args: '%s',stdout: '%s', stderr: '%s'",
                  command_args[0], out, err)
        if check_errors:
            if not result.is_return_code_zero or result.has_errors:
                self.fail(err)
        return result

    def get_first_deployable_release_id(self):
        releases = sorted(Release.get_all_data(),
                          key=lambda x: x['id'])
        for r in releases:
            if r['is_deployable']:
                return r['id']
        self.fail("There are no deployable releases.")

    def run_cli_commands(self, command_lines, **kwargs):
        for command in command_lines:
            self.run_cli_command(command, **kwargs)

    def check_if_required(self, command):
        call = self.run_cli_command(command, check_errors=False)
        # should not work without env id
        self.assertIn("required", call.stderr)

    def check_for_stdout(self, command, msg, check_errors=True):
        call = self.run_cli_command(command, check_errors=check_errors)
        self.assertEqual(call.stdout, msg)

    def check_for_stdout_by_regexp(self, command, pattern, check_errors=True):
        call = self.run_cli_command(command, check_errors=check_errors)
        result = re.search(pattern, call.stdout)
        self.assertIsNotNone(result)
        return result

    def check_for_stderr(self, command, msg, check_errors=True):
        call = self.run_cli_command(command, check_errors=check_errors)
        self.assertIn(msg, call.stderr)

    def check_all_in_msg(self, command, substrings, **kwargs):
        output = self.run_cli_command(command, **kwargs)
        for substring in substrings:
            self.assertIn(substring, output.stdout)

    def check_for_rows_in_table(self, command):
        output = self.run_cli_command(command)
        message = output.stdout.split("\n")
        # no env
        self.assertEqual(message[2], '')

    def check_number_of_rows_in_table(self, command, number_of_rows):
        output = self.run_cli_command(command)
        self.assertEqual(len(output.stdout.split("\n")), number_of_rows + 3)

    def _get_task_info(self, task_id):
        """Get info about task with given ID.

        :param task_id: Task ID
        :type task_id: str or int
        :return: Task info
        :rtype: dict
        """
        return {}

    def wait_task_ready(self, task_id, timeout=60, interval=3):
        """Wait for changing task status to 'ready'.

        :param task_id: Task ID
        :type task_id: str or int
        :param timeout: Max time of waiting, in seconds
        :type timeout: int
        :param interval: Interval of getting task info, in seconds
        :type interval: int
        """
        wait_until_in_statuses = (consts.TASK_STATUSES.running,
                                  consts.TASK_STATUSES.pending)
        timer = time.time()
        while True:
            task = self._get_task_info(task_id)
            status = task.get('status', '')
            if status not in wait_until_in_statuses:
                self.assertEqual(status, consts.TASK_STATUSES.ready)
                break

            if time.time() - timer > timeout:
                raise Exception(
                    "Task '{0}' seems to be hanged".format(task['name'])
                )
            time.sleep(interval)


class CLIv1TestCase(BaseTestCase):

    handler = 'fuel'

    def _get_task_info(self, task_id):
        command = "task show -f json {0}".format(str(task_id))
        call = self.run_cli_command(command, handler='fuel2')
        return json.loads(call.stdout)


class CLIv2TestCase(BaseTestCase):

    handler = 'fuel2'

    def _get_task_info(self, task_id):
        command = "task show -f json {0}".format(str(task_id))
        call = self.run_cli_command(command)
        return json.loads(call.stdout)
