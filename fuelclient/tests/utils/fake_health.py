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


def get_fake_test_set(testset_id=None, name=None):
    """Create a random fake test set for environment."""
    return {
        "id": testset_id or "fake_test_set",
        "name": name or "Fake tests. Duration 30 sec - 2 min"
    }


def get_fake_test_sets(testsets_count, **kwargs):
    """Create a random fake list of test sets for environment."""
    return [get_fake_test_set(**kwargs)
            for _ in range(testsets_count)]


def get_fake_test_set_item(testset_id=None, testset=None, cluster_id=None,
                           status=None, tests=None):
    """Create a random fake test set item."""
    return {
        "id": testset_id or 45,
        "testset": testset or "fake_test_set",
        "cluster_id": cluster_id or 65,
        "status": status or "finished",
        "started_at": "2016-09-15 09:03:07.697393",
        "ended_at": "2016-09-15 09:03:19.280296",
        "tests": tests or [
            {
                "status": "failure",
                "taken": 1.0,
                "testset": "fake_test_set",
                "name": "Create fake instance",
                "duration": "30 s.",
                "message": "Fake test message",
                "id": "fuel_health.tests.fake_test",
                "description": "fake description"
            },
            {
                "status": "stopped",
                "taken": 0.5,
                "testset": "fake_test_set",
                "name": "Check create, update and delete fake instance image",
                "duration": "70 s.",
                "message": "Can not set proxy for Health Check.",
                "id": "fuel_health.tests.fake_test.test_update_fake_images",
                "description": "fake description"
            }
        ]
    }


def get_fake_test_set_items(items_count, **kwargs):
    """Create a random fake list of test sets items."""
    return [get_fake_test_set_item(**kwargs)
            for _ in range(items_count)]
