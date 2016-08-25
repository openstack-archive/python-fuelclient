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


def get_fake_role(name=None, meta=None, volumes_roles_mapping=None):
    """Create a random fake role

    Returns the serialized and parametrized representation of a dumped Fuel
    role. Represents the average amount of data.

    """
    return {
        "name": name or "controller",
        "meta": meta or {
            "group": "base",
            "name": "Controller",
            "conflicts": ["compute", "ceph-osd"],
            "description": "The Controller initiates orchestration activities "
                           "and provides an external API.  Other components "
                           "like Glance (image storage), Keystone (identity "
                           "management), Horizon (OpenStack dashboard) and "
                           "Nova-Scheduler are installed on the controller "
                           "as well."
        },
        "volumes_roles_mapping": volumes_roles_mapping or [
            {"id": "os", "allocate_size": "min"},
            {"id": "logs", "allocate_size": "min"},
            {"id": "image", "allocate_size": "all"},
            {"id": "mysql", "allocate_size": "min"},
            {"id": "horizon", "allocate_size": "min"}
        ]
    }


def get_fake_roles(role_count, **kwargs):
    """Create a random fake list of roles."""
    return [get_fake_role(**kwargs)
            for _ in range(role_count)]
