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

function cleanup_nailgun {
    echo "Cleaning up nailgun."
    pushd "$FUEL_WEB_ROOT" > /dev/null
    tox -e stop || echo "Error while stopping nailgun."
    popd > /dev/null

    pushd "$FUEL_WEB_ROOT" > /dev/null
    tox -e cleanup
    popd > /dev/null
}

function prepare_nailgun {
    echo "Preparing nailgun."
    pushd "$FUEL_WEB_ROOT" > /dev/null
    tox -e start
    popd > /dev/null
}

function prepare_fuelclient_config {
    echo "Creating fuelclient config file $FUELCLIENT_CUSTOM_SETTINGS"
    mkdir -p $(dirname $FUELCLIENT_CUSTOM_SETTINGS)
    cat > $FUELCLIENT_CUSTOM_SETTINGS <<EOL
SERVER_ADDRESS: "127.0.0.1"
SERVER_PORT: "${NAILGUN_PORT}"
OS_USERNAME: "admin"
OS_PASSWORD: "admin"
OS_TENANT_NAME: "admin"
EOL
}

function cleanup_fuelclient_config {
    echo "Removing fuelclient config file $FUELCLIENT_CUSTOM_SETTINGS"
    rm -f $FUELCLIENT_CUSTOM_SETTINGS
}

function prepare_fuel_web_repo {
    echo "Cloning $FUEL_WEB_REPO repo."

    if [[ "$FUEL_WEB_CLONE" == "yes" ]]; then
        git clone ${FUEL_WEB_REPO} ${FUEL_WEB_ROOT} || \
            { echo "Failed to clone $FUEL_WEB_REPO repo"; exit 1; }
    fi

    pushd "$FUEL_WEB_ROOT" > /dev/null

    if [[ -n $FUEL_WEB_FETCH_REPO ]]; then
        git fetch "$FUEL_WEB_FETCH_REPO" "$FUEL_WEB_FETCH_REFSPEC" || \
            { echo "Failed to fetch $FUEL_WEB_FETCH_REPO"; exit 1; }
    fi

    git checkout "$FUEL_WEB_COMMIT" || \
        { echo "Failed to checkout to $FUEL_WEB_COMMIT"; exit 1; }

    popd > /dev/null

}

function cleanup_fuel_web_repo {
    echo "Removing $FUEL_WEB_ROOT directory."

    if [[ "$FUEL_WEB_CLONE" == "yes" ]]; then
        rm -rf $FUEL_WEB_ROOT
    fi
}
