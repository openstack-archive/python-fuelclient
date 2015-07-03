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

set -e

# settings
ROOT=$(dirname $(readlink -f $0))
FUEL_WEB_REPO=${FUEL_WEB_REPO:-"https://github.com/stackforge/fuel-web.git"}
FUEL_WEB_ROOT=${FUEL_WEB_ROOT:-"/tmp/fuel_web"}
NAILGUN_ROOT=$FUEL_WEB_ROOT/nailgun
FETCH_REPO=${FETCH_REPO:-""}
FETCH_REFSPEC=${FETCH_REFSPEC:-""}
FUEL_COMMIT=${FUEL_COMMIT:-master}

# Nailgun server parameters
NAILGUN_PORT=${NAILGUN_PORT:-8003}
NAILGUN_CHECK_URL=${NAILGUN_CHECK_URL:-"http://0.0.0.0:$NAILGUN_PORT/api/version"}
NAILGUN_START_MAX_WAIT_TIME=${NAILGUN_START_MAX_WAIT_TIME:-10}
TEST_NAILGUN_DB=${TEST_NAILGUN_DB:-nailgun}

# pytest options
ARTIFACTS=${ARTIFACTS:-$(pwd)/test_run}
FUELCLIENT_JUNIT=${FUELCLIENT_JUNIT:-"$ROOT/fuelclient.xml"}

# A POSIX variable
OPTIND=1

# Prints usage and exist
usage() {
    msg "Usage: $0 [OPTIONS] [-- TESTR OPTIONS]"
    msg "Run python-fuelclient test suite"
    msg ""
    msg "  -6  --py26                  Run python-2.6 tests."
    msg "  -7  --py27                  Run python-2.7 tests."
    msg "                              If neither -6 nor -7 is specified, tests for both"
    msg "                              versions will be running."
    msg "  -c  --fuel-commit           Checkout fuel-web to a specified commit. If not specified,"
    msg "                              \$FUEL_COMMIT or master will be used."
    msg "                              By default checks out to master."
    msg "  -f  --fetch-repo            URI of a remote repo for fetching changes to fuel-web."
    msg "                              If not specified, \$FETCH_REPO or nothing will be used."
    msg "  -h, --help                  Print this usage message and exit."
    msg "  -i  --integration-tests     Run only integration tests."
    msg "  -I  --no-integration-tests  Don't run integration tests."
    msg "  -n  --no-clone              Do not clone fuel-web repo and use existing"
    msg "                              one specified in \$FUEL_WEB_ROOT. Make sure it"
    msg "                              does not have pending changes."
    msg "  -p  --pep8                  Runs only flake8 tests."
    msg "  -P  --no-pep8               Do not run flake8 tests automatically."
    msg "  -r  --fetch-refspec         Refspec to fetch from the remore repo. This option"
    msg "                              requires -r or --fetch-refspec to be specified."
    msg "                              If not specified, \$FETCH_REFSPEC or nothing will be used."
    msg "  -t  --test                  Test to run. To run many tests, pass this flag multiple times."
    msg "                              Runs all tests, if not specified. "
    msg "  -u  --unit-tests            Run only unit tests."
    msg "  -U  --no-unit-tests         Don't run unit tests."
    msg "  -V  --client-version        Which version of python-fuelclient should be tested, for example:"
    msg "                              ./run_tests.sh -V v1"
    msg "                              To test multiple versions, pass this flag multiple times."
    exit
}

err() {
    printf "%s\n" "$1" >&2
}

msg() {
    printf "%s\n" "$1"
}

# Reads input options and sets appropriate parameters
process_options() {
    # Read the options
    TEMP=$(getopt \
        -o 67huUiInpPc:f:r:t:V: \
        --long py26,py27,help,integration-tests,no-integration-tests,no-pep8,pep8,unit-tests,no-unit-tests,no-clone,client-version:,fuel-commit:,fetch-repo:,fetch-refspec:,tests: \
        -n 'run_tests.sh' -- "$@")

    eval set -- "$TEMP"

    while true ; do
        case "$1" in
            -6|--py26) python_26=1;                             shift 1;;
            -7|--py27) python_27=1;                             shift 1;;
            -h|--help) usage;                                   shift 1;;
            -f|--fetch-repo) fetch_repo="$2";                   shift 2;;
            -r|--fetch-refspec) fetch_refspec="$2";             shift 2;;
            -c|--fuel-commit) fuel_commit="$2";                 shift 2;;
            -n|--no-clone) do_clone=0;                          shift 1;;
            -t|--test) certain_tests+=("$2");                   shift 2;;
            -p|--pep8) pep8_only=1;                             shift 1;;
            -P|--no-pep8) do_pep8=0;                            shift 1;;
            -i|--integration-tests) integration_tests=1;        shift 1;;
            -I|--no-integration-tests) no_integration_tests=1;  shift 1;;
            -u|--unit-tests) unit_tests=1;                      shift 1;;
            -U|--no-unit-tests) no_unit_tests=1;                shift 1;;
            -V|--client-version) client_version+=("$2");        shift 2;;
            # All parameters and alien options will be passed to testr
            --) shift 1; testropts="$@";
                break;;
            *) err "Internal error: got \"$1\" argument.";
                usage; exit 1
        esac
    done

    if [[ -z $fetch_repo && -n $fetch_refspec ]]; then
        err "--fetch-refspec option requires --fetch-repo to be specified."
        exit 1
    fi

    if [[ $unit_tests -eq 0 && \
        $integration_tests -eq 0 && \
        ${#certain_tests[@]} -eq 0 ]]; then

        if [[ $no_unit_tests -ne 1 ]]; then
            unit_tests=1
        fi

        if [[ $no_integration_tests -ne 1 ]]; then
            integration_tests=1
        fi

    else
        do_pep8=0
    fi

    # when no version specified, choose all of the versions available
    if [[ ${#client_version[@]} -eq 0 ]]; then
        client_version+=("common")
        for version in ${ROOT}/fuelclient/tests/v[0-9]; do
            client_version+=(`basename $version`)
        done
    fi

    for version in ${client_version[@]}; do
        if [[ $unit_tests -eq 1 ]]; then
            certain_tests+=("${ROOT}/fuelclient/tests/${version}/unit/")
        fi
        if [[ $integration_tests -eq 1 ]]; then
            certain_tests+=("${ROOT}/fuelclient/tests/${version}/integration/")
        fi
    done

    # Check that specified test file/dir exists. Fail otherwise.
    if [[ ${#certain_tests[@]} -ne 0 ]]; then
        for test in ${certain_tests[@]}; do
            local file_name=${test%:*}
            if [[ ! -f $file_name ]] && [[ ! -d $file_name ]]; then
                err "Specified tests were not found."
                exit 1
            fi
        done
    fi
}


# Arguments:
#
#   $1 -- path to the server config
#
# Run python-fuelclient tests.
# It is supposed that nailgun server is up and running.
run_cli_tests() {
    local config=$1
    local run_single_env=$((python_26^python_27))

    local py26_env="py26"
    local py27_env="py27"

    if [[ $run_single_env -eq 1 ]]; then
        if [[ $python_26 -eq 1 ]]; then
            env_to_run=$py26_env
        else
            env_to_run=$py27_env
        fi
    else
        env_to_run=$py26_env,$py27_env
    fi

    pushd $ROOT/fuelclient > /dev/null
    # run tests
    NAILGUN_CONFIG=$config LISTEN_PORT=$NAILGUN_PORT \
        NAILGUN_ROOT=$NAILGUN_ROOT tox -e$env_to_run -- -vv $testropts \
        ${certain_tests[@]} --junit-xml $FUELCLIENT_JUNIT || return 1
    popd > /dev/null

    return 0
}

run_pep8() {
    local ret=0

    pushd $ROOT/fuelclient > /dev/null
    tox -e pep8 || ret=$?
    popd > /dev/null

    return $ret
}

# Arguments:
#
#   $1 -- path to the server config
#
# Remove temporary files and database.
# Does not touch $FUEL_WEB_ROOT if -n or --no-clone is specified.
run_cleanup() {
    local config=$1

    msg "Doing a clean up."

    kill_server

    find . -type f -name "*.pyc" -delete

    if [[ -f "$config" ]] && [[ -d $NAILGUN_ROOT ]]; then
        pushd $NAILGUN_ROOT > /dev/null
        NAILGUN_CONFIG=$config tox -evenv -- \
            python manage.py dropdb > /dev/null
        popd > /dev/null
    fi

    if [[ -f $ARTIFACTS ]]; then
        rm -rf $ARTIFACTS
    fi

    if [[ -v server_log ]]; then
        rm -f $server_log
    fi

    if [[ "$do_clone" -ne "0" ]] && [[ -d $FUEL_WEB_ROOT ]]; then
        rm -rf $FUEL_WEB_ROOT
    fi
}


# Arguments:
#
#   $1 -- path to the server config
#   $2 -- insert default data into database if true
#
# Synchronizes the schema of the database and loads default data.
setup_db() {
    local config=$1
    local defaults=$2

    msg "Setting up database."

    pushd $NAILGUN_ROOT > /dev/null
    NAILGUN_CONFIG=$config tox -evenv -- python manage.py syncdb > /dev/null

    if [[ $# -ne 0 && $defaults = true ]]; then
        NAILGUN_CONFIG=$config tox -evenv -- \
            python manage.py loaddefault > /dev/null
    fi

    popd > /dev/null
}


# Sends SIGING to running Nailgun
kill_server() {
    # kill old server instance if exists
    local pid=$(lsof -ti tcp:$NAILGUN_PORT)
    if [[ -n "$pid" ]]; then
        kill $pid
        sleep $NAILGUN_START_MAX_WAIT_TIME
    fi
}


# Arguments:
#
#   $1 -- path to log file
#   $2 -- path to the server config
#
# Returns: a server pid, that you have to close manually
run_server() {
    local server_log=$1
    local server_config=$2

    local run_server_cmd="\
        python manage.py run \
        --port=$NAILGUN_PORT \
        --config=$server_config \
        --fake-tasks \
        --fake-tasks-tick-count=80 \
        --fake-tasks-tick-interval=1"

    kill_server

    # run new server instance
    pushd $NAILGUN_ROOT > /dev/null
    tox -evenv -- $run_server_cmd >> $server_log 2>&1 &
    popd > /dev/null

    # wait for server availability
    which curl > /dev/null

    if [[ $? -eq 0 ]]; then
        local num_retries=$((NAILGUN_START_MAX_WAIT_TIME * 10))
        local i=0

        while true; do
            # Fail if number of retries exeeded
            if [[ $i -gt $((num_retries + 1)) ]]; then return 1; fi

            local http_code=$(curl -s -w %{http_code} -o /dev/null $NAILGUN_CHECK_URL)

            if [[ "$http_code" = "200" ]]; then return 0; fi

            sleep 0.1
            i=$((i + 1))
        done
    else
        sleep $NAILGUN_START_MAX_WAIT_TIME
        lsof -ti tcp:$NAILGUN_PORT

        return $?
    fi
}


# Arguments
#
#   $1 -- path to the server config
#
# Set up test environment
prepare_env() {
    local config=$1

    msg "Preparing test environment."
    obtain_nailgun || return 1

    mkdir -p $ARTIFACTS
    create_settings_yaml $config $ARTIFACTS

    setup_db $config true

    server_log=$(mktemp /tmp/test_nailgun_cli_server.XXXX)
    run_server $server_log $config || \
        { err "Failed to start Nailgun"; return 1; }
}


# Arguments:
#
#   $1 -- path to the server config
#   $2 -- path to folder with testing artifacts
#
# Generates server configuration file
create_settings_yaml() {
    local config_path=$1
    local artifacts_path=$2
    cat > $config_path <<EOL
DEVELOPMENT: 1
STATIC_DIR: ${artifacts_path}/static_compressed
TEMPLATE_DIR: ${artifacts_path}/static_compressed
DATABASE:
  name: ${TEST_NAILGUN_DB}
  engine: "postgresql"
  host: "localhost"
  port: "5432"
  user: "nailgun"
  passwd: "nailgun"
API_LOG: ${artifacts_path}/api.log
APP_LOG: ${artifacts_path}/app.log
EOL
}


# Clones Nailgun from git, pulls specified patch and
# switches to the specified commit
obtain_nailgun() {
    err "Obtaining Nailgun with the revision $fuel_commit"

    if [[ $do_clone -ne 0 ]]; then
        git clone $FUEL_WEB_REPO $FUEL_WEB_ROOT || \
            { err "Failed to clone Nailgun"; return 1; }
    fi

    if [[ ! -d "$NAILGUN_ROOT" ]]; then
        err "Nailgun directory $NAILGUN_ROOT not found."
        exit 1
    fi
    pushd $NAILGUN_ROOT > /dev/null

    if [[ -n $fetch_repo ]]; then
        err "Fetching changes from $fetch_repo $fetch_refspec"
        git fetch $fetch_repo $fetch_refspec || \
            { err "Failed to pull changes"; return 1; }
    fi

    git checkout $fuel_commit || \
        { err "Failed to checkout to $fuel_commit"; return 1; }

    popd > /dev/null
}


# Sets default values for parameters
init_default_params() {
    certain_tests=()
    client_version=()
    do_clone=1
    do_pep8=1
    fetch_refspec=$FETCH_REFSPEC
    fetch_repo=$FETCH_REPO
    fuel_commit=$FUEL_COMMIT
    integration_tests=0
    no_integration_tests=0
    no_unit_tests=0
    pep8_only=0
    python_26=0
    python_27=0
    testropts="--with-timer --timer-warning=10 --timer-ok=2 --timer-top-n=10"
    unit_tests=0
}


# Main function
run() {
    local config=$ARTIFACTS/test.yaml
    local pep8_ret=0
    local cli_ret=0

    run_cleanup $config

    if [[ $do_pep8 -eq 1 ]]; then
        err "Starting PEP8 tests..."
        run_pep8 || pep8_ret=$?

        [[ $pep8_ret -ne 0 ]] && err "Failed tests: pep8"
        [[ $pep8_only -eq 1 ]] && exit $pep8_ret
    fi

    if [[ "${certain_tests[@]}" == *"integration"* ]]; then
        prepare_env $config
    fi

    err "Starting python-fuelclient tests..."
    run_cli_tests $config || cli_ret=$?
    [[ $cli_ret -ne 0 ]] && err "Failed tests: cli_tests"

    run_cleanup $config

    if [[ $pep8_ret -ne 0 || $cli_ret -ne 0 ]]; then
        err "Testing python-fuelclient failed."
        exit 1
    else
        err "Testing python-fuelclient succeeded."
        exit 0
    fi
}


init_default_params
process_options $@
run
