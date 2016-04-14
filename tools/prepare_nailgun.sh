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

    local run_server_cmd="\
        python manage.py run \
        --port=$NAILGUN_PORT \
        --config=$NAILGUN_CONFIG \
        --fake-tasks \
        --fake-tasks-tick-count=80 \
        --fake-tasks-tick-interval=1"
    local server_log=$(mktemp $ARTIFACTS/test_nailgun_cli_server.XXXX)
    local check_url="http://0.0.0.0:${NAILGUN_PORT}${NAILGUN_CHECK_PATH}"

    # run new server instance
    pushd $NAILGUN_ROOT > /dev/null
    tox -e venv -- $run_server_cmd >> $server_log 2>&1 &
    popd > /dev/null

    # Wait for server's availability
    which curl > /dev/null

    if [[ $? -eq 0 ]]; then
        local num_retries=$((NAILGUN_START_MAX_WAIT_TIME * 10))
        local i=0

        while true; do
            # Fail if number of retries exeeded
            if [[ $i -gt $((num_retries + 1)) ]]; then return 1; fi

            local http_code=$(curl -s -w %{http_code} -o /dev/null $check_url)

            if [[ "$http_code" = "200" ]]; then return 0; fi

            sleep 0.1
            i=$((i + 1))
        done
    else
        err "Failed to start Nailgun in ${NAILGUN_START_MAX_WAIT_TIME} seconds."
        exit 1
    fi
}


# Set up test environment
prepare_env() {
    mkdir -p $ARTIFACTS
}


# Generates server configuration file
create_settings_yaml() {
    cat > $NAILGUN_CONFIG <<EOL
DEVELOPMENT: 1
STATIC_DIR: ${ARTIFACTS}/static_compressed
TEMPLATE_DIR: ${ARTIFACTS}/static_compressed
DATABASE:
  name: ${TEST_NAILGUN_DB}
  engine: "postgresql"
  host: "localhost"
  port: "5432"
  user: "nailgun"
  passwd: "nailgun"
API_LOG: ${ARTIFACTS}/api.log
APP_LOG: ${ARTIFACTS}/app.log
EOL

    # Create appropriate Fuel Client config
    cat > $FUELCLIENT_CUSTOM_SETTINGS <<EOL
# Connection settings
SERVER_ADDRESS: "127.0.0.1"
SERVER_PORT: "${NAILGUN_PORT}"
OS_USERNAME: "admin"
OS_PASSWORD: "admin"
OS_TENANT_NAME: "admin"
EOL
}


# Clones Nailgun from git, pulls specified patch and
# switches to the specified commit
obtain_nailgun() {
    err "Obtaining Nailgun with the revision $FUEL_COMMIT"

    if [[ "$FUEL_WEB_CLONE" == "yes" ]]; then
        git clone "${FUEL_WEB_REPO}" "${FUEL_WEB_ROOT}" || \
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
