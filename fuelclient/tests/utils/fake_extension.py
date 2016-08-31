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


def get_fake_env_extensions(names=None):
    """Create a list of fake extensions for particular env"""

    return names or ['fake_ext1', 'fake_ext2', 'fake_ext3']


def get_fake_extension(name=None, version=None, provides=None,
                       description=None):
    return {'name': name or 'fake_name',
            'version': version or 'fake_version',
            'provides': provides or ['fake_method_call'],
            'description': description or 'fake_description',
            }


def get_fake_extensions(extension_count, **kwargs):
    """Create a random fake list of extensions."""
    return [get_fake_extension(**kwargs)
            for _ in range(extension_count)]
