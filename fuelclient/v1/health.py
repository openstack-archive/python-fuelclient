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

import six

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1


class HealthClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Health
    _allowed_statuses = (
        'error',
        'operational',
        'update_error',
    )

    def get_all(self, environment_id):
        """Get list of health check test sets for a given environment.

        :param environment_id: Id of environment
        :type environment_id: int
        :return: health test sets as a list of dict
        :rtype: list
        """
        return self._entity_wrapper.get_test_sets(environment_id)

    def get_status_all(self, environment_id=None):
        """Get test sets statuses. If environment_id is None then all test sets
         will be retrieved.

        :param environment_id: Id of environment
        :type environment_id: int
        :return: health test sets as a list of dict
        :rtype: list
        """
        data = self._entity_wrapper.get_tests_status()
        # OSTF API doesn't support filtering by cluster, then do it 'manually'
        if environment_id is not None:
            data = [i for i in data if i['cluster_id'] == environment_id]
        return data

    def get_status_single(self, test_id):
        data = self._entity_wrapper.get_tests_status(test_id)
        if data:
            result = []
            for tests in data.get('tests'):
                result.append("\n* {} ({}, '{}')".format(tests["name"],
                                                         tests["status"],
                                                         tests["message"]))
        else:
            msg = "Test sets with id {0} does not exist".format(test_id)
            raise error.ActionException(msg)
        data['tests'] = ' '.join(result)
        return data

    def get_last_test_status(self, environment_id):
        return self._entity_wrapper.get_last_tests_status(environment_id)

    def check(self, environment_id, ostf_credentials=None, test_sets=None,
              force=False):
        """Run health check test sets for a given environment. If test_sets
        is None then all test sets will be run

        :param environment_id: Id of environment
        :type environment_id: int
        :param ostf_credentials: ostf credentials
        :type ostf_credentials: dict
        :param test_sets: list of test sets
        :type test_sets: list
        :param force:
        :type force: bool
        :return: running health test sets as a list of dict
        :rtype: list
        """
        env_obj = objects.Environment(environment_id)

        if env_obj.status not in self._allowed_statuses and not force:
            raise error.EnvironmentException(
                "Environment is not ready to run health check "
                "because it is in {0} state. Health check is likely "
                "to fail because of this. Use --force flag "
                "to proceed anyway.".format(env_obj.status)
            )

        if env_obj.is_customized and not force:
            raise error.EnvironmentException(
                "Environment deployment facts were updated. "
                "Health check is likely to fail because of "
                "that. Use --force flag to proceed anyway."
            )
        test_sets_to_run = test_sets or set(ts['id'] for ts in
                                            self.get_all(environment_id))

        return self._entity_wrapper.run_test_sets(environment_id,
                                                  test_sets_to_run,
                                                  ostf_credentials)

    def stop(self, testrun_id):
        testrun_obj = self._entity_wrapper(obj_id=testrun_id)
        return testrun_obj.stop_test()[0]


def get_client(connection):
    return HealthClient(connection)
