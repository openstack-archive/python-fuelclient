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

from fuelclient.cli.serializers import Serializer
from fuelclient import objects
from fuelclient.v1 import base_v1


class VipClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Environment

    @staticmethod
    def download(env_id, ip_addr_id=None, network_id=None,
                 network_role=None, file_path=None):

        env = objects.Environment(env_id)
        vips_data = env.get_vips_data(
            ip_address_id=ip_addr_id,
            network=network_id,
            network_role=network_role
        )
        vips_data_file_path = env.write_vips_data_to_file(
            vips_data,
            file_path=file_path,
            serializer=Serializer()
        )
        return vips_data_file_path

    @staticmethod
    def upload(env_id, file_path):
        env = objects.Environment(env_id)
        vips_data = env.read_vips_data_from_file(
            file_path=file_path,
            serializer=Serializer()
        )
        env.set_vips_data(vips_data)

    @staticmethod
    def create(env_id, ip_addr, network, vip_name, vip_namespace=None):
        env = objects.Environment(env_id)
        vip_data = {
            'ip_addr': ip_addr,
            'network': network,
            'vip_name': vip_name
        }
        if vip_namespace is not None:
            vip_data['vip_namespace'] = vip_namespace

        env.create_vip(**vip_data)


def get_client(connection):
    return VipClient(connection)
