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


class DeploymentInfoClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Task

    def download(self, transaction_id, file_path=None):

        task = self._entity_wrapper(transaction_id)
        deployment_info = task.get_deployment_info()
        deployment_info_file_path = task.write_deployment_info_to_file(
            deployment_info,
            file_path=file_path,
            serializer=Serializer()
        )
        return deployment_info_file_path


def get_client():
    return DeploymentInfoClient()
