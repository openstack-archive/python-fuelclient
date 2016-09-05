# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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


class Health(BaseObject):

    # class_api_path = "clusters/"
    instance_api_path = "clusters/{0}/"

    def get_test_sets(self):
        return self.connection.get_request(
            'testsets/{0}'.format(self.id),
            ostf=True
        )

    @classmethod
    def get_tests_status(cls, test_id=None):
        """Get test sets statuses. If test_id is None then all test sets will
        be retrieved.

        :param test_id: Id of test set
        :type test_id: int
        :return: status of health test set
        :rtype: list
        """

        test_id = test_id if test_id is not None else ''
        return cls.connection.get_request(
            'testruns/{0}'.format(test_id),
            ostf=True
        )

    def get_last_tests_status(self):
        return self.connection.get_request(
            'testruns/last/{0}'.format(self.id),
            ostf=True
        )

    def run_test_sets(self, test_sets_to_run, ostf_credentials=None):

        def make_test_set(name):
            result = {
                "testset": name,
                "metadata": {
                    "config": {},
                    "cluster_id": self.id,
                }
            }
            if ostf_credentials:
                creds = result['metadata'].setdefault(
                    'ostf_os_access_creds', {})
                if 'tenant' in ostf_credentials:
                    creds['ostf_os_tenant_name'] = ostf_credentials['tenant']
                if 'username' in ostf_credentials:
                    creds['ostf_os_username'] = ostf_credentials['username']
                if 'password' in ostf_credentials:
                    creds['ostf_os_password'] = ostf_credentials['password']
            return result

        tests_data = [make_test_set(ts) for ts in test_sets_to_run]
        test_runs = self.connection.post_request('testruns',
                                                 tests_data,
                                                 ostf=True)

        return test_runs

    @property
    def is_customized(self):
        return self.get_fresh_data()['is_customized']

    @property
    def status(self):
        return self.get_fresh_data()['status']
