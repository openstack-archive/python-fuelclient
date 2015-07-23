# -*- coding: utf-8 -*-
#
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


def get_fake_fuel_version():
    """Creates a fake fuel version

    Returns the serialized and parametrized representation of a dumped Fuel
    environment. Represents the average amount of data.

    """
    return {
        "astute_sha": "16b252d93be6aaa73030b8100cf8c5ca6a970a91",
        "release": "6.0",
        "build_id": "2014-12-26_14-25-46",
        "build_number": "58",
        "auth_required": True,
        "fuellib_sha": "fde8ba5e11a1acaf819d402c645c731af450aff0",
        "production": "docker",
        "nailgun_sha": "5f91157daa6798ff522ca9f6d34e7e135f150a90",
        "release_versions": {
            "2014.2-6.0": {
                "VERSION": {
                    "ostf_sha": "a9afb68710d809570460c29d6c3293219d3624d4",
                    "astute_sha": "16b252d93be6aaa73030b8100cf8c5ca6a970a91",
                    "release": "6.0",
                    "build_id": "2014-12-26_14-25-46",
                    "build_number": "58",
                    "fuellib_sha": "fde8ba5e11a1acaf819d402c645c731af450aff0",
                    "production": "docker",
                    "nailgun_sha": "5f91157daa6798ff522ca9f6d34e7e135f150a90",
                    "api": "1.0",
                    "fuelmain_sha": "81d38d6f2903b5a8b4bee79ca45a54b76c1361b8",
                    "feature_groups": [
                        "mirantis"
                    ]
                }
            }
        },
        "api": "1.0",
        "fuelmain_sha": "81d38d6f2903b5a8b4bee79ca45a54b76c1361b8",
        "feature_groups": [
            "mirantis"
        ]
    }
