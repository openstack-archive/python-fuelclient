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

import os

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.cli.formatting import format_table
from fuelclient.objects.release import Release
from fuelclient.objects.role import Role


class RoleAction(Action):
    """List all roles for specific release
    """
    action_name = "role"

    def __init__(self):
        super(RoleAction, self).__init__()
        self.args = [
            Args.get_list_arg("List all roles"),
            Args.get_release_arg("Release id"),
            Args.get_int_arg("role"),
            Args.get_file_arg("File where to download role info"),
            Args.get_create_arg("Create role from file"),
            Args.get_boolean_arg("update", help="Update role form file"),
            Args.get_delete_arg("Delete role from fuel")
        ]
        self.flag_func_map = (
            ("role", self.item),
            ("delete", self.delete),
            ("create", self.create),
            ("update", self.update),
            (None, self.list),
        )


    def list(self, params):
        """Print all available roles

                fuel role --rel 1
                fuel role
        """
        roles = Role.get_all()

        # such cases should becovered with filterin
        if params.release:
            roles = [r for r in roles if r['release_id'] == params.release]

        acceptable_keys = ("name", "id", "release_id")

        self.serializer.print_to_output(
            roles,
            format_table(
                roles,
                acceptable_keys=acceptable_keys
            )
        )

    def item(self, params):
        """Save full role description to file
            fuel role --role 1 --file some
        """
        role = Role.get_one(params.role)
        self.serializer.write_to_file(params.file, role)
        self.serializer.print_to_output(
            role,
            "Role successfully saved to {0}.".format(params.file))

    def create(self, params):
        """Create a role from file description
            fuel role --create --file some
        """
        role = self.serializer.read_from_file(params.file)
        role = Role.create(role)
        self.serializer.print_to_output(
            role,
            "Role with {0} successfully created from {1}.".format(
                role['id'], params.file))

    def update(self, params):
        """Update a role from file description
            fuel role --update --file some
        """
        role = self.serializer.read_from_file(params.file)
        role = Role.update(role['id'], role)
        self.serializer.print_to_output(
            role,
            "Role successfully updated from {0}.".format(params.file))

    def delete(self, params):
        """Delete role from fuel
            fuel role --delete --role 2
        """
        resp = Role.delete(params.role)
        self.serializer.print_to_output(
            resp,
            "Role with id successfully delete.".format(params.role))
