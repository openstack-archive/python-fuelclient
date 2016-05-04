# -*- coding: utf-8 -*-
#
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

from fuelclient.commands import base


class VipMixIn(object):
    entity_name = 'vip'

    @staticmethod
    def add_env_id_arg(parser):
        parser.add_argument(
            '-e',
            '--env',
            type=int,
            required=True,
            help='Environment identifier'
        )

    @staticmethod
    def add_network_id_arg(parser):
        parser.add_argument(
            "-n",
            "--network",
            type=int,
            default=None,
            required=False,
            help="Network identifier"
        )


class VipDownload(VipMixIn, base.BaseCommand):
    """Download VIPs configuration."""

    @staticmethod
    def add_ip_address_id_arg(parser):
        parser.add_argument(
            "-a",
            "--ip-address-id",
            type=int,
            default=None,
            required=False,
            help="IP address entity identifier"
        )

    @staticmethod
    def add_network_role_arg(parser):
        parser.add_argument(
            "-r",
            "--network-role",
            type=str,
            default=None,
            required=False,
            help="Network role string"
        )

    @staticmethod
    def add_file_arg(parser):
        parser.add_argument(
            '-f',
            '--file',
            type=str,
            required=False,
            default=None,
            help='YAML file that contains openstack configuration.'
        )

    def get_parser(self, prog_name):
        parser = super(VipDownload, self).get_parser(prog_name)
        self.add_env_id_arg(parser)
        self.add_ip_address_id_arg(parser)
        self.add_file_arg(parser)
        self.add_network_id_arg(parser)
        self.add_network_role_arg(parser)
        return parser

    def take_action(self, args):
        vips_data_file_path = self.client.download(
            env_id=args.env,
            ip_addr_id=args.ip_address_id,
            network_id=args.network,
            network_role=args.network_role,
            file_path=args.file
        )

        self.app.stdout.write(
            "VIP configuration for environment with id={0}"
            " downloaded to {1}".format(args.env, vips_data_file_path)
        )


class VipUpload(VipMixIn, base.BaseCommand):
    """Upload new VIPs configuration from file."""

    @staticmethod
    def add_file_arg(parser):
        parser.add_argument(
            '-f',
            '--file',
            required=True,
            type=str,
            help='YAML file that contains openstack configuration.'
        )

    def get_parser(self, prog_name):
        parser = super(VipUpload, self).get_parser(prog_name)
        self.add_env_id_arg(parser)
        self.add_file_arg(parser)
        return parser

    def take_action(self, args):
        self.client.upload(env_id=args.env, file_path=args.file)
        self.app.stdout.write("VIP configuration uploaded.")


class VipCreate(VipMixIn, base.BaseCommand):
    """Create VIP"""

    @staticmethod
    def add_vip_name_arg(parser):
        parser.add_argument(
            '-N',
            '--name',
            required=True,
            type=str,
            help="VIP name"
        )

    @staticmethod
    def add_ip_addr_arg(parser):
        parser.add_argument(
            '-a',
            '--address',
            required=True,
            type=str,
            help="IP-address for the VIP"
        )

    @staticmethod
    def add_vip_namespace_arg(parser):
        parser.add_argument(
            '--namespace',
            required=False,
            type=str,
            help="VIP namespace"
        )

    def get_parser(self, prog_name):
        parser = super(VipCreate, self).get_parser(prog_name)
        self.add_env_id_arg(parser)
        self.add_network_id_arg(parser)
        self.add_vip_name_arg(parser)
        self.add_ip_addr_arg(parser)
        self.add_vip_namespace_arg(parser)
        return parser

    def take_action(self, args):
        vip_kwargs = {
            "env_id": args.env,
            "ip_addr": args.address,
            "network": args.network,
            "vip_name": args.name,
        }
        if args.namespace is not None:
            vip_kwargs['vip_namespace'] = args.namespace

        self.client.create(**vip_kwargs)

        self.app.stdout.write("VIP has been created.")
