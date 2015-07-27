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


from fuelclient.cli.actions.base import Action
from fuelclient.cli.actions.base import check_all
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli.formatting import format_table
from fuelclient.cli.serializers import FileFormatBasedSerializer
from fuelclient.objects.role import Role


class RoleAction(Action):
    """List all roles for specific release
    """
    action_name = "role"

    def __init__(self):
        # NOTE(dshulyak) this serializers are really messed up
        # it gets overwritten in several places
        self.file_serializer = FileFormatBasedSerializer()
        self.args = [
            Args.get_list_arg("List all roles"),

            Args.get_release_arg("Release id"),
            Args.get_str_arg("role", help="Name of the role"),
            Args.get_file_arg("File with role description"),

            group(
                Args.get_create_arg("Create role from file"),
                Args.get_boolean_arg("update", help="Update role from file"),
                Args.get_delete_arg("Delete role from fuel")
            )
        ]
        self.flag_func_map = (
            ("delete", self.delete),
            ("create", self.create),
            ("update", self.update),
            ("role", self.item),
            (None, self.list),
        )

    @check_all('release')
    def list(self, params):
        """Print all available roles

                fuel role --rel 1
        """
        roles = Role.get_all(params.release)

        acceptable_keys = ("name", )

        self.serializer.print_to_output(
            roles,
            format_table(
                roles,
                acceptable_keys=acceptable_keys
            )
        )

    @check_all('role', 'release', 'file')
    def item(self, params):
        """Save full role description to file
            fuel role --rel 1 --role controller --file some.yaml
        """
        role = Role.get_one(params.release, params.role)
        self.file_serializer.write_to_file(params.file, role)
        self.file_serializer.print_to_output(
            role,
            "Role successfully saved to {0}.".format(params.file))

    @check_all('file', 'release')
    def create(self, params):
        """Create a role from file description
            fuel role --rel 1 --create --file some.yaml
        """
        role = self.file_serializer.read_from_file(params.file)
        role = Role.create(params.release, role)
        self.file_serializer.print_to_output(
            role,
            "Role {0} successfully created from {1}.".format(
                role['name'], params.file))

    @check_all('file', 'release')
    def update(self, params):
        """Update a role from file description
            fuel role --rel 1 --update --file some.yaml
        """
        role = self.file_serializer.read_from_file(params.file)
        role = Role.update(params.release, role['name'], role)
        self.file_serializer.print_to_output(
            role,
            "Role successfully updated from {0}.".format(params.file))

    @check_all('role', 'release')
    def delete(self, params):
        """Delete role from fuel
            fuel role --delete --role controller --rel 1
        """
        Role.delete(params.release, params.role)
        self.file_serializer.print_to_output(
            {},
            "Role with id {0} successfully deleted.".format(params.role))
