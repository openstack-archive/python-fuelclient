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


def get_fake_tag(tag_name=None, has_primary=False, owner_id=None,
                 owner_type=None):
    """Create a random fake tag

    Returns the serialized and parametrized representation of a dumped Fuel
    tag. Represents the average amount of data.

    """
    return {
        "id": 1,
        "tag": tag_name or "controller",
        "has_primary": has_primary,
        "owner_id": owner_id or 1,
        "owner_type": owner_type or 'release'
    }


def get_fake_tags(tag_count, **kwargs):
    """Create a random fake list of tags."""
    return [get_fake_tag(**kwargs) for _ in range(tag_count)]
