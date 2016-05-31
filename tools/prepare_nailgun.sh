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

export NAILGUN_DB=${NAILGUN_DB:-'nailgun'}
export NAILGUN_DB_USER=${NAILGUN_DB_USER:-'nailgun'}
export NAILGUN_DB_USERPW=${NAILGUN_DB_USERPW:-'nailgun'}

NAILGUN_CONFIG=$ARTIFACTS/test.yaml

err() {
    printf "%s\n" "$1" >&2
}

msg() {
    printf "%s\n" "$1"
}

# Synchronizes the schema of the database and loads default data.
setup_db() {
    msg "Setting up database."

    pushd $NAILGUN_ROOT > /dev/null
    tox -e venv -- python manage.py syncdb > /dev/null
    tox -e venv -- python manage.py loaddefault > /dev/null

    popd > /dev/null
}


# Returns: a server pid, that you have to close manually
run_server() {

    pushd $NAILGUN_ROOT > /dev/null
    tox -e venv -- $NAILGUN_ROOT/tools/env.sh prepare_nailgun_server
    popd > /dev/null
}


# Set up test environment
prepare_env() {
    mkdir -p $ARTIFACTS
}


# Generates server configuration file
create_settings_yaml() {
    pushd $NAILGUN_ROOT > /dev/null
    tox -e venv -- $NAILGUN_ROOT/tools/env.sh prepare_nailgun_env
    popd > /dev/null
}


# Clones Nailgun from git, pulls specified patch and
# switches to the specified commit
obtain_nailgun() {
    err "Obtaining Nailgun with the revision $FUEL_COMMIT"

    if [[ "$FUEL_WEB_CLONE" == "yes" ]]; then
        git clone --depth 1 $FUEL_WEB_REPO $FUEL_WEB_ROOT || \
            { err "Failed to clone Nailgun"; exit 1; }
    fi

    if [[ ! -d "$NAILGUN_ROOT" ]]; then
        err "Nailgun directory $NAILGUN_ROOT not found."
        exit 1
    fi

    pushd "$NAILGUN_ROOT" > /dev/null

    echo $FETCH_REPO

    if [[ -n $FETCH_REPO ]]; then
        err "Fetching changes from $FETCH_REPO $FETCH_REFSPEC"
        git fetch "$FETCH_REPO" "$FETCH_REFSPEC" || \
            { err "Failed to pull changes"; exit 1; }
    fi

    git checkout "$FUEL_COMMIT" || \
        { err "Failed to checkout to $FUEL_COMMIT"; exit 1; }

    popd > /dev/null
}


prepare_env
obtain_nailgun
create_settings_yaml
setup_db
run_server
