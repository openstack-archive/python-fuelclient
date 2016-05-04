#    Copyright 2016 Mirantis, Inc.
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
import fuelclient.cli.arguments as Args
from fuelclient.cli import serializers
from fuelclient.objects.environment import Environment


class VIPAction(Action):
    """Download or upload VIP settings of specific environments.
    """
    action_name = "vip"
    acceptable_keys = ("id", "upload", "download", "network", "network-role",)

    def __init__(self):
        super(VIPAction, self).__init__()
        # NOTE(aroma): 'serializer' attribute for action objects is
        # overwritten while building parser object
        # (fuelclient.cli.parser.Parser)
        self.file_serializer = serializers.FileFormatBasedSerializer()
        self.args = (
            Args.get_env_arg(required=True),
            Args.get_create_arg("Create VIP"),
            Args.get_upload_file_arg("Upload changed VIP configuration "
                                     "from given file"),
            Args.get_download_arg("Download VIP configuration"),
            Args.get_file_arg("Target file with vip data."),
            Args.get_ip_id_arg("IP address entity identifier"),
            Args.get_ip_address_arg("IP address string"),
            Args.get_network_id_arg("Network identifier"),
            Args.get_network_role_arg("Network role string"),
            Args.get_vip_name_arg("VIP name string"),
            Args.get_vip_namespace_arg("VIP namespace string"),
        )
        self.flag_func_map = (
            ("create", self.create),
            ("upload", self.upload),
            ("download", self.download)
        )

    def create(self, params):
        """To create VIP for environment:
            fuel --env 1 vip create --address 172.16.0.10 --network 1 \\
                --name public_vip --namespace haproxy
        """
        env = Environment(params.env)
        vip_kwargs = {
            "ip_addr": getattr(params, 'ip-address'),
            "network": getattr(params, 'network'),
            "vip_name": getattr(params, 'vip-name'),
        }

        vip_namespace = getattr(params, 'vip-namespace', None)
        if vip_namespace is not None:
            vip_kwargs['vip_namespace'] = vip_namespace

        env.create_vip(**vip_kwargs)
        print("VIP has been created")

    def upload(self, params):
        """To upload VIP configuration from some
            file for some environment:
                fuel --env 1 vip --upload vip.yaml
        """
        env = Environment(params.env)
        vips_data = env.read_vips_data_from_file(
            file_path=params.upload,
            serializer=self.file_serializer
        )
        env.set_vips_data(vips_data)
        print("VIP configuration uploaded.")

    def download(self, params):
        """To download VIP configuration in this
            file for some environment:
                fuel --env 1 vip --download --file vip.yaml
            where --file param is optional
        """

        env = Environment(params.env)
        vips_data = env.get_vips_data(
            ip_address_id=getattr(params, 'ip-address-id'),
            network=getattr(params, 'network'),
            network_role=getattr(params, 'network-role')
        )
        vips_data_file_path = env.write_vips_data_to_file(
            vips_data,
            file_path=params.file,
            serializer=self.serializer
        )
        print(
            "VIP configuration for environment with id={0}"
            " downloaded to {1}".format(env.id, vips_data_file_path)
        )
