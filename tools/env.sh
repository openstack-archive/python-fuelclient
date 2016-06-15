#!/bin/bash
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

set -eu

. $(dirname $0)/env_functions.sh

case $1 in
    prepare_nailgun)
        prepare_nailgun
        ;;
    cleanup_nailgun)
        cleanup_nailgun
        ;;
    prepare_fuelclient)
        prepare_fuelclient_config
        ;;
    cleanup_fuelclient)
        cleanup_fuelclient_config
        ;;
    prepare_fuel_web_repo)
        prepare_fuel_web_repo
        ;;
    cleanup_fuel_web_repo)
        cleanup_fuel_web_repo
        ;;
    *)
        echo "Not supported subcommand. Available subcommands: "
        echo "cleanup_nailgun"
        echo "prepare_nailgun"
        echo "cleanup_fuelclient"
        echo "prepare_fuelclient"
        echo "cleanup_fuel_web_repo"
        echo "prepare_fuel_web_repo"
        exit 1
        ;;
esac
