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

from functools import wraps
import json
import os
import sys

from keystoneclient.exceptions import Unauthorized
import requests
import textwrap


def exit_with_error(message):
    """exit_with_error - writes message to stderr and exits with exit code 1.
    """
    sys.stderr.write("{}{}".format(message, os.linesep))
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


class HTTPError(FuelClientException):
    pass


class EnvironmentException(Exception):
    pass


def exceptions_decorator(func):
    """Handles HTTP errors and expected exceptions that may occur
    in methods of DefaultAPIClient class
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        # when server returns to us bad request check that
        # and print meaningful reason
        except HTTPError as exc:
            exit_with_error(exc)
        except requests.ConnectionError:
            message = """
                Can't connect to Nailgun server!
                Please check connection settings in your configuration file."""
            exit_with_error(textwrap.dedent(message).strip())
        except Unauthorized:
            message = """
                Unauthorized: need authentication!
                Please provide user and password via client
                fuel --os-username=user --os-password=pass [action]
                or modify your credentials in your configuration file."""
            exit_with_error(textwrap.dedent(message).strip())
        except FuelClientException as exc:
            exit_with_error(exc.message)

    return wrapper


def get_error_body(error):
    try:
        error_body = json.loads(error.response.text)['message']
    except (ValueError, TypeError, KeyError):
        error_body = error.response.text

    return error_body


def get_full_error_message(error):
    return "{} ({})".format(error, get_error_body(error))
