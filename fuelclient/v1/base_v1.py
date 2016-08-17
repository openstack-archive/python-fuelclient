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

import abc

import six

from fuelclient import client


@six.add_metaclass(abc.ABCMeta)
class BaseV1Client(object):

    @abc.abstractproperty
    def _entity_wrapper(self):
        pass

    def __init__(self, connection=None):
        if connection is None:
            connection = client.DefaultAPIClient
        self.connection = connection

        cls_wrapper = self.__class__._entity_wrapper
        self._entity_wrapper = type(
            cls_wrapper.__name__,
            (cls_wrapper, ),
            {'connection': self.connection}
        )

    def get_all(self, **kwargs):
        filters = {}
        for k, v in six.iteritems(kwargs):
            if isinstance(v, list):
                if v:
                    filters[k] = ','.join(str(s) for s in v)
            elif v is not None:
                filters[k] = str(v)
        result = self._entity_wrapper.get_all_data(**filters)

        return result

    def get_by_id(self, entity_id):
        obj = self._entity_wrapper(obj_id=entity_id)

        return obj.data
