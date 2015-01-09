#!/bin/bash

#    Copyright 2013-2015 Mirantis, Inc.
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

set -euxx

# settings
ROOT=$(dirname `readlink -f $0`)
FUEL_WEB_REPO=${FUEL_WEB_REPO:-"https://github.com/stackforge/fuel-web.git"}
FUEL_WEB_ROOT=${FUEL_WEB_ROOT:-"/tmp/fuel_web"}
NAILGUN_ROOT=$FUEL_WEB_ROOT/nailgun
TEST_NAILGUN_DB=${TEST_NAILGUN_DB:-nailgun}
TESTRTESTS="nosetests"

# test options
testrargs=
testropts="--with-timer --timer-warning=10 --timer-ok=2 --timer-top-n=10"

# nosetest xunit options
FUELCLIENT_XUNIT=${FUELCLIENT_XUNIT:-"$ROOT/fuelclient.xml"}
FUELCLIENT_SERVER_PORT=${FUELCLIENT_SERVER_PORT:-8003}
NAILGUN_CHECK_URL=${NAILGUN_CHECK_URL:-"http://0.0.0.0:$FUELCLIENT_SERVER_PORT/api/version"}
NAILGUN_START_MAX_WAIT_TIME=${NAILGUN_START_MAX_WAIT_TIME:-10}
ARTIFACTS=${ARTIFACTS:-`pwd`/test_run}
TEST_WORKERS=${TEST_WORKERS:-0}
mkdir -p $ARTIFACTS

function usage {
  echo "Usage: $0 [OPTION]..."
  echo "Run python-fuelclient test suite"
  echo ""
  echo "  -h, --help                  Print this usage message"
  echo "  -t, --tests                 Run a given test files"
  exit
}


function process_options {
  for arg in $@; do
    case "$arg" in
      -h|--help) usage;;
      -t|--tests) certain_tests=1;;
      -*) testropts="$testropts $arg";;
      *) testrargs="$testrargs $arg"
    esac
  done
}


# disabled/enabled flags that are setted from the cli.
# used for manipulating run logic.


function run_tests {
  run_cleanup

  echo "Starting Fuel client tests..."
  run_cli_tests || { echo "Failed tests: cli_tests"; return 1; }

  exit
}

# Run fuelclient tests.
#
# Arguments:
#
#   $@ -- tests to be run; with no arguments all tests will be run
#
# It is supposed that nailgun server is up and working.
# We are going to pass nailgun url to test runner.
function run_cli_tests {
  local SERVER_PORT=$FUELCLIENT_SERVER_PORT
  local TESTS=$ROOT/fuelclient/tests
  local config=$ARTIFACTS/test.yaml
  local pid

  prepare_artifacts $ARTIFACTS $config
  obtain_nailgun || return 1

  if [ $# -ne 0 ]; then
    TESTS=$@
  fi

  local server_log=`mktemp /tmp/test_nailgun_cli_server.XXXX`
  local result=0

  dropdb $config
  syncdb $config true

  pid=`run_server $SERVER_PORT $server_log $config` || \
      { echo 'Failed to start Nailgun'; return 1; }

  if [ "$pid" -ne "0" ]; then

    pushd $ROOT/fuelclient >> /dev/null
    # run tests
    NAILGUN_CONFIG=$config LISTEN_PORT=$SERVER_PORT \
    tox -epy26 -- -vv $testropts $TESTS --xunit-file $FUELCLIENT_XUNIT || result=1
    popd >> /dev/null

    kill $pid
    wait $pid 2> /dev/null
  else
    cat $server_log
    result=1
  fi

  rm $server_log

  return $result
}


# Remove temporary files. No need to run manually, since it's
# called automatically in `run_tests` function.
function run_cleanup {
  find . -type f -name "*.pyc" -delete
  rm -f *.log
  rm -f *.pid
  rm -rf $FUEL_WEB_ROOT
}


# Arguments:
#
#   $1 -- insert default data into database if true
function syncdb {
  pushd $NAILGUN_ROOT >> /dev/null
  local config=$1
  local defaults=$2
  NAILGUN_CONFIG=$config tox -evenv -- python manage.py syncdb > /dev/null

  if [[ $# -ne 0 && $defaults = true ]]; then
    NAILGUN_CONFIG=$config tox -evenv -- python manage.py loaddefault > /dev/null
  fi

  popd >> /dev/null
}


function dropdb {
  pushd $NAILGUN_ROOT >> /dev/null
  local config=$1
  NAILGUN_CONFIG=$config tox -evenv -- python manage.py dropdb > /dev/null

  popd >> /dev/null
}


# Arguments:
#
#   $1 -- server port
#   $2 -- path to log file
#   $3 -- path to the server config
#
# Returns: a server pid, that you have to close manually
function run_server {
  local SERVER_PORT=$1
  local SERVER_LOG=$2
  local SERVER_SETTINGS=$3

  local RUN_SERVER="\
    python manage.py run \
      --port=$SERVER_PORT \
      --config=$SERVER_SETTINGS \
      --fake-tasks \
      --fake-tasks-tick-count=80 \
      --fake-tasks-tick-interval=1"

  pushd $NAILGUN_ROOT >> /dev/null

  # kill old server instance if exists
  local pid=`lsof -ti tcp:$SERVER_PORT`
  if [ -n "$pid" ]; then
    kill $pid
    sleep 5
  fi

  # run new server instance
  tox -evenv -- $RUN_SERVER >> $SERVER_LOG 2>&1 &

  # wait for server availability
  which curl > /dev/null
  ret=$?
  if [ $ret -eq 0 ]; then

    local num_retries=$[$NAILGUN_START_MAX_WAIT_TIME * 10]

    for i in $(seq 1 $num_retries); do
      local http_code=`curl -s -w %{http_code} -o /dev/null $NAILGUN_CHECK_URL`
      if [ "$http_code" == "200" ]; then break; fi
      sleep 0.1
    done
  else
    sleep 5
  fi
  popd >> /dev/null

  pid=`lsof -ti tcp:$SERVER_PORT`
  local nailgun_launched=$?
  echo $pid

  return $nailgun_launched
}

function prepare_artifacts {
  local artifacts=$1
  local config=$2
  mkdir -p $artifacts
  create_settings_yaml $config $artifacts
}

function create_settings_yaml {
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

function obtain_nailgun {
  git clone $FUEL_WEB_REPO $FUEL_WEB_ROOT || \
      { echo "Failed to clone nailgun"; return 1; }
}

# Detect test runner for a given testfile and then run the test with
# this runner.
#
# Arguments:
#
#   $1 -- path to the test file
function guess_test_run {
  if [[ $1 == *ui_tests* && $1 == *.js ]]; then
    run_webui_tests $1 || echo "ERROR: $1"
  elif [[ $1 == *fuelclient* ]]; then
    run_cli_tests $1 || echo "ERROR: $1"
  elif [[ $1 == *fuel_upgrade_system* ]]; then
    run_upgrade_system_tests $1 || echo "ERROR: $1"
  elif [[ $1 == *shotgun* ]]; then
    run_shotgun_tests $1 || echo "ERROR: $1"
  else
    run_nailgun_tests $1 || echo "ERROR: $1"
  fi
}


# parse command line arguments and run the tests
process_options $@
run_tests
