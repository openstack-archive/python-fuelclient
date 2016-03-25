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

from fuelclient.objects.base import BaseObject


class DeploymentHistory(BaseObject):

    class_api_path = "transactions/{transaction_id}/deployment_history/"\
                     "?nodes={nodes}&statuses={statuses}"

    @classmethod
    def get_all(cls, transaction_id, nodes=None, statuses=None):
        statuses = ",".join(str(s) for s in statuses) if statuses else ""
        nodes = ",".join(str(n) for n in nodes) if nodes else ""
        history = cls.connection.get_request(
            cls.class_api_path.format(
                transaction_id=transaction_id,
                nodes=nodes,
                statuses=statuses))

        return history
