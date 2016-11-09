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
from fuelclient.cli.actions.base import check_any
import fuelclient.cli.arguments as Args
from fuelclient.cli.arguments import group
from fuelclient.cli.formatting import format_table
from fuelclient.cli.serializers import FileFormatBasedSerializer
from fuelclient.objects.role import Role


class RoleAction(Action):
    """List all roles for specific release or cluster
    """
    action_name = "role"

    fields_mapper = (
        ('env', 'clusters'),
        ('release', 'releases')
    )

    def __init__(self):
        # NOTE(dshulyak) this serializers are really messed up
        # it gets overwritten in several places
        self.file_serializer = FileFormatBasedSerializer()
        self.args = [
            Args.get_list_arg("List all roles"),
            group(
                Args.get_env_arg(),
                Args.get_release_arg("Release id"),
                required=True
            ),
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

    def parse_model(self, args):
        for param, role_class in self.fields_mapper:
            model_id = getattr(args, param)
            if model_id:
                return role_class, model_id

    @check_any('release', 'env')
    def list(self, params):
        """Print all available roles for release or cluster

                fuel role --rel 1
                fuel role --env 1
        """
        model, model_id = self.parse_model(params)
        roles = Role(owner_type=model, owner_id=model_id).get_all()

        acceptable_keys = ("name", )

        self.serializer.print_to_output(
            roles,
            format_table(
                roles,
                acceptable_keys=acceptable_keys
            )
        )

    @check_all('role', 'file')
    @check_any('release', 'env')
    def item(self, params):
        """Save full role description to file
            fuel role --rel 1 --role controller --file some.yaml
            fuel role --env 1 --role controller --file some.yaml
        """
        model, model_id = self.parse_model(params)
        role = Role(owner_type=model, owner_id=model_id).get_role(params.role)
        self.file_serializer.write_to_file(params.file, role)
        self.file_serializer.print_to_output(
            role,
            "Role {0} for {1} successfully saved to {2}.".format(
                params.role,
                model,
                params.file))

    @check_all('file')
    @check_any('release', 'env')
    def create(self, params):
        """Create a role from file description
            fuel role --rel 1 --create --file some.yaml
            fuel role --env 1 --create --file some.yaml
        """
        model, model_id = self.parse_model(params)
        role = self.file_serializer.read_from_file(params.file)
        role = Role(owner_type=model, owner_id=model_id).create_role(role)
        self.file_serializer.print_to_output(
            role,
            "Role {0} for {1} successfully created from {2}.".format(
                role['name'], model, params.file))

    @check_all('file')
    @check_any('release', 'env')
    def update(self, params):
        """Update a role from file description
            fuel role --rel 1 --create --file some.yaml
            fuel role --env 1 --create --file some.yaml
        """
        model, model_id = self.parse_model(params)
        role = self.file_serializer.read_from_file(params.file)
        role = Role(owner_type=model, owner_id=model_id).update_role(
            role['name'],
            role)
        self.file_serializer.print_to_output(
            role,
            "Role {0} for {1} successfully updated from {2}.".format(
                params.role,
                model,
                params.file))

    @check_all('role')
    @check_any('release', 'env')
    def delete(self, params):
        """Delete role from fuel
            fuel role --delete --role controller --rel 1
            fuel role --delete --role controller --env 1
        """
        model, model_id = self.parse_model(params)
        Role(owner_type=model, owner_id=model_id).delete_role(params.role)
        self.file_serializer.print_to_output(
            {},
            "Role {0} for {1} with id {2} successfully deleted.".format(
                params.role,
                model,
                model_id))
