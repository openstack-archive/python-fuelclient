#!/bin/bash

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

set -eu

NAILGUN_CONFIG=$ARTIFACTS/test.yaml


# Sends SIGING to the running instance of Nailgun, if it exists
kill_server() {
    echo "Stopping Nailgun and waiting $NAILGUN_START_MAX_WAIT_TIME seconds."

    local pid=$(lsof -ti tcp:$NAILGUN_PORT)
    if [[ -n "$pid" ]]; then
        kill $pid
        sleep $NAILGUN_START_MAX_WAIT_TIME
    fi
}


drop_database () {
    echo "Dropping the database."

    if [[ -f "$NAILGUN_CONFIG" ]] && [[ -d $NAILGUN_ROOT ]]; then
        pushd $NAILGUN_ROOT > /dev/null
        tox -e venv -- python manage.py dropdb > /dev/null
        popd > /dev/null
    fi
}


delete_files() {
    echo "Deleting the files."
    rm -rf "$ARTIFACTS"

    if [[ "$FUEL_WEB_CLONE" == "yes" ]] && [[ -d "$FUEL_WEB_ROOT" ]]; then
        rm -rf "$FUEL_WEB_ROOT"
    fi
}


echo "Doing a clean up to ensure clean environment."

kill_server
drop_database
delete_files

