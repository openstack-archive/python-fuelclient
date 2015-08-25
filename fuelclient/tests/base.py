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
from fuelclient.objects import Release

try:
    from unittest.case import TestCase
except ImportError:
    # Runing unit-tests in production environment
    from unittest2.case import TestCase

import logging
import os
import shutil
import subprocess
import sys
import tempfile

from StringIO import StringIO

import mock

from fuelclient.cli.parser import main


logging.basicConfig(stream=sys.stderr)
log = logging.getLogger("CliTest.ExecutionLog")
log.setLevel(logging.DEBUG)


class FakeFile(StringIO):
    """It's a fake file which returns StringIO
    when file opens with 'with' statement.
    NOTE(eli): We cannot use mock_open from mock library
    here, because it hangs when we use 'with' statement,
    and when we want to read file by chunks.
    """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class CliExectutionResult:
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


class UnitTestCase(TestCase):
    """Base test class which does not require nailgun server to run."""

    def setUp(self):
        """Mocks keystone authentication."""
        self.auth_required_patcher = mock.patch(
            'fuelclient.client.Client.auth_required',
            new_callable=mock.PropertyMock
        )
        self.auth_required_mock = self.auth_required_patcher.start()
        self.auth_required_mock.return_value = False
        super(UnitTestCase, self).setUp()

    def tearDown(self):
        super(UnitTestCase, self).tearDown()
        self.auth_required_patcher.stop()

    def execute(self, command):
        return main(command)

    def mock_open(self, text, filename='some.file'):
        """Mocks builtin open function.
        Usage example:

          with mock.patch('__builtin__.open', self.mock_open('file content')):
              # call mocked code
        """
        fileobj = FakeFile(text)
        setattr(fileobj, 'name', filename)
        return mock.MagicMock(return_value=fileobj)


class BaseTestCase(UnitTestCase):
    nailgun_root = os.environ.get('NAILGUN_ROOT', '/tmp/fuel_web/nailgun')

    def setUp(self):
        self.reload_nailgun_server()
        self.temp_directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_directory)

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
            cmd = 'tox -evenv -- manage.py %s' % action
            cls.run_command(cmd, cwd=cls.nailgun_root)

    @classmethod
    def load_data_to_nailgun_server(cls):
        file_path = os.path.join(cls.nailgun_root,
                                 'nailgun/fixtures/sample_environment.json')

        cmd = 'tox -evenv -- manage.py loaddata %s' % file_path
        cls.run_command(cmd, cwd=cls.nailgun_root)

    def run_cli_command(self, command_line,
                        check_errors=True, env=os.environ.copy()):

        command_args = [" ".join(('fuel', command_line))]
        process_handle = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=env
        )
        out, err = process_handle.communicate()
        result = CliExectutionResult(process_handle, out, err)
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
