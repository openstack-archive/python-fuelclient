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

    class_api_path = "testruns/"
    instance_api_path = "testruns/{0}"
    test_sets_api_path = "testsets/{0}"

    @classmethod
    def get_test_sets(cls, environment_id):
        return cls.connection.get_request(
            cls.test_sets_api_path.format(environment_id),
            ostf=True
        )

    @classmethod
    def get_tests_status(cls, testrun_id=None):
        """Get test sets status. If test_id is None then all test sets will
        be retrieved.

        :param testrun_id: Id of test set
        :type testrun_id: int
        :return: status of health test set
        :rtype: list
        """
        testrun_id = testrun_id if testrun_id is not None else ''
        return cls.connection.get_request(
            cls.instance_api_path.format(testrun_id),
            ostf=True
        )

    @classmethod
    def get_last_tests_status(cls, environment_id):
        return cls.connection.get_request(
            'testruns/last/{0}'.format(environment_id),
            ostf=True
        )

    @classmethod
    def run_test_sets(cls, environment_id, test_sets_to_run,
                      ostf_credentials=None):

        def make_test_set(name):
            result = {
                "testset": name,
                "metadata": {
                    "config": {},
                    "cluster_id": environment_id,
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
        test_runs = cls.connection.post_request(cls.class_api_path,
                                                tests_data,
                                                ostf=True)
        return test_runs

    def stop_test(self):
        data = [
            {"id": self.id,
             "status": "stopped"}
        ]
        return self.connection.put_request(
            'testruns/', data, ostf=True
        )
