#!/usr/bin/python

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

import argparse
import os
import subprocess


ARTIFACTS = os.getenv('ARTIFACTS')
FUEL_WEB_CLONE = os.getenv('FUEL_WEB_CLONE')
FUEL_WEB_ROOT = os.getenv('FUEL_WEB_ROOT')
NAILGUN_CONFIG = os.path.join(ARTIFACTS, 'test.yaml')
NAILGUN_PORT = os.getenv('NAILGUN_PORT')
NAILGUN_ROOT = os.path.join(FUEL_WEB_ROOT, 'nailgun')
NAILGUN_START_MAX_WAIT_TIME = os.getenv('NAILGUN_START_MAX_WAIT_TIME')


def kill_server():
    """Sends SIGING to the running instance of Nailgun, if it exists"""
    print 'Stopping Nailgun and waiting {0} seconds.'.format(
        NAILGUN_START_MAX_WAIT_TIME)
    try:
        pid = subprocess.check_output(
            ['lsof', '-ti', 'tcp:{0}'.format(NAILGUN_PORT)],
            stderr=subprocess.STDOUT)
        os.system('kill {0}'.format(pid))
        os.system('sleep {0}'.format(NAILGUN_START_MAX_WAIT_TIME))
    except subprocess.CalledProcessError:
        pass


def drop_database():
    print 'Dropping the database.'
    if (os.path.isfile(NAILGUN_CONFIG) and os.path.isdir(NAILGUN_ROOT)):
        subprocess.Popen(
            ['tox', '-e', 'venv', '--', 'python',
             'manage.py', 'dropdb', '>', '/dev/null'],
            shell=True, cwd=NAILGUN_ROOT)


def delete_files():
    print 'Deleting the files.'
    os.system('rm -rf {0}'.format(ARTIFACTS))
    if (FUEL_WEB_CLONE == 'yes' and os.path.isdir(FUEL_WEB_ROOT)):
        os.system('rm -rf {0}'.format(FUEL_WEB_ROOT))


def delete_pyc_files(dir):
    os.system('find {0} -name \'*.pyc\' -delete'.format(dir))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--delete-pyc', action='store_true', help='Delete pyc files')
    parser.add_argument(
        '-t', '--tox-ini-dir', help='Dir with tox.ini')

    args = parser.parse_args()

    print 'Doing a clean up to ensure clean environment.'

    kill_server()
    drop_database()
    delete_files()

    if args.delete_pyc:
        delete_pyc_files(args.tox_ini_dir)
