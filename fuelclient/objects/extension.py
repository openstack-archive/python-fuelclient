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


class Extension(BaseObject):

    class_api_path = "extensions/"

    @property
    def extensions_url(self):
        return 'clusters/{0}/extensions'.format(self.id)

    def get_env_extensions(self):
        """Get list of extensions through request to the Nailgun API

        """
        return self.connection.get_request(self.extensions_url)

    def set_env_extensions(self, extensions):
        """Enable extensions through request to the Nailgun API

        :param extensions: list of extenstion to be enabled
        """
        return self.connection.put_request(self.extensions_url, extensions)
