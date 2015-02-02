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

import sys

from fuelclient.cli.actions.base import Action
from fuelclient.client import APIClient


class TokenAction(Action):
    """Return a valid keystone auth token
    """
    action_name = "token"

    def __init__(self):
        super(TokenAction, self).__init__()

        self.args = []
        self.flag_func_map = (
            (None, self.get_token),
        )

    def get_token(self, params):
        """Print out a valid Keystone auth token
        """
        sys.stdout.write(APIClient.auth_token)
