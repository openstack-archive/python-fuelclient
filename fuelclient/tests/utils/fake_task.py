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


def get_fake_task(task_id=None, status=None, name=None,
                  cluster=None, result=None, progress=None,
                  message=None, uuid=None):
    """Create a fake task

    Returns the serialized and parametrized representation of a dumped Fuel
    Task. Represents the average amount of data.

    """
    return {'status': status or 'running',
            'name': name or 'deploy',
            'id': task_id or 42,
            'uuid': uuid or '14474652-4f3e-4dc6-b2f3-5921b62b4a9e',
            'message': message or 'I am a human being!',
            'task_id': task_id or 42,
            'cluster': cluster or 34,
            'result': result or '',
            'progress': progress or 50}
