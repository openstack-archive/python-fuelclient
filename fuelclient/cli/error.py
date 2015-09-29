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

from contextlib import contextmanager
import json
from keystoneclient.exceptions import Unauthorized
import requests
import sys

import six


def exit_with_error(message):
    """Writes message to stderr and exits with exit code 1."""
    sys.stderr.write(message + "\n")
    exit(1)


class FuelClientException(Exception):
    """Base Exception for Fuel-Client

    All child classes must be instantiated before raising.
    """
    def __init__(self, *args, **kwargs):
        super(FuelClientException, self).__init__(*args, **kwargs)
        self.message = args[0]


class BadDataException(FuelClientException):
    """Should be raised when user provides corrupted data."""


class WrongEnvironmentError(FuelClientException):
    """Raised when particular action is not supported on environment."""


class ServerDataException(FuelClientException):
    """ServerDataException - must be raised when
    data returned from server cannot be processed by Fuel-Client methods.
    """


class DeployProgressError(FuelClientException):
    """DeployProgressError - must be raised when
    deployment process interrupted on server.
    """


class ArgumentException(FuelClientException):
    """ArgumentException - must be raised when
    incorrect arguments inputted through argparse or some function.
    """


class ActionException(FuelClientException):
    """ActionException - must be raised when
    though arguments inputted to action are correct but they contradict
    to logic in action.
    """


class ParserException(FuelClientException):
    """ParserException - must be raised when
    some problem occurred in process of argument parsing,
    in argparse extension or in Fuel-Client Parser submodule.
    """


class ProfilingError(FuelClientException):
    """Indicates errors and other issues related to performance profiling."""


class SettingsException(FuelClientException):
    """Indicates errors or unexpected behaviour in processing settings."""


class ExecutedErrorNonZeroExitCode(FuelClientException):
    """Subshell command returned non-zero exit code."""


class LabelEmptyKeyError(BadDataException):
    """Should be raised when user provides labels with empty key."""


class InvalidDirectoryException(FuelClientException):
    pass


class InvalidFileException(FuelClientException):
    pass


@contextmanager
def exceptions_handler(debug=False):
    """Handles HTTP errors and expected exceptions that may occur
    in methods of APIClient class
    """
    try:
        yield
    # when server returns to us bad request check that
    # and print meaningful reason
    except requests.HTTPError as exc:
        exit_with_error("{0} ({1})".format(exc, get_error_body(exc)))
    except requests.ConnectionError:
        exit_with_error("""
        Can't connect to Nailgun server!
        Please modify "SERVER_ADDRESS" and "LISTEN_PORT"
        in the file /etc/fuel/client/config.yaml""")
    except Unauthorized:
        exit_with_error("""
        Unauthorized: need authentication!
        Please provide user and password via client
         fuel --user=user --password=pass [action]
        or modify "KEYSTONE_USER" and "KEYSTONE_PASS" in
        /etc/fuel/client/config.yaml""")
    except FuelClientException as e:
        exit_with_error(six.text_type(e))
    except Exception as e:
        if not debug:
            error = "Error: Unexpected error happened while " \
                    "attempting to execute operation.\n" \
                    "Error: {0}.".format(six.text_type(e))
            error += "\n\nPlease file a bug report at " \
                     "https://bugs.launchpad.net/fuel/.\n\nExecute " \
                     "again the last command with --debug option. " \
                     "Please include the output in your bug report."
            exit_with_error(error)
        else:
            raise e


def get_error_body(error):
    try:
        error_body = json.loads(error.response.text)['message']
    except (ValueError, TypeError, KeyError):
        error_body = error.response.text

    return error_body
