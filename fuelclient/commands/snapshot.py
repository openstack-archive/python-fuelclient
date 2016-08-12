# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

from oslo_utils import fileutils

from fuelclient.cli import error
from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient import utils


class SnapshotMixIn(object):

    entity_name = 'snapshot'
    supported_file_formats = ('json', 'yaml')

    @staticmethod
    def config_file(file_path):
        if not utils.file_exists(file_path):
            raise argparse.ArgumentTypeError(
                'File "{0}" does not exist'.format(file_path))
        return file_path

    @staticmethod
    def get_config_path(directory, file_format):
        return os.path.join(os.path.abspath(directory),
                            'snapshot_conf.{}'.format(file_format))


class SnapshotGenerate(SnapshotMixIn, base.BaseCommand):
    """Generate diagnostic snapshot."""

    def get_parser(self, prog_name):
        parser = super(SnapshotGenerate, self).get_parser(prog_name)
        parser.add_argument('-c',
                            '--config',
                            required=False,
                            type=self.config_file,
                            help='Configuration file.')
        return parser

    def take_action(self, parsed_args):
        file_path = parsed_args.config

        config = dict()
        if file_path:
            file_format = os.path.splitext(file_path)[1].lstrip('.')
            try:
                with open(file_path, 'r') as stream:
                    config = data_utils.safe_load(file_format, stream)
            except (OSError, IOError):
                msg = 'Could not read configuration at {}.'
                raise error.InvalidFileException(msg.format(file_path))

        result = self.client.create_snapshot(config)

        msg = "Diagnostic snapshot generation task with id {id} was started\n"
        self.app.stdout.write(msg.format(id=result.id))


class SnapshotConfigGetDefault(SnapshotMixIn, base.BaseCommand):
    """Download default config to generate custom diagnostic snapshot."""

    def get_parser(self, prog_name):
        parser = super(SnapshotConfigGetDefault, self).get_parser(prog_name)
        parser.add_argument('-f',
                            '--format',
                            required=True,
                            choices=self.supported_file_formats,
                            help='Format of serialized diagnostic snapshot '
                                 'configuration data.')
        parser.add_argument('-d',
                            '--directory',
                            required=False,
                            default=os.path.curdir,
                            help='Destination directory. Defaults to '
                                 'the current directory.')
        return parser

    def take_action(self, parsed_args):
        file_path = self.get_config_path(parsed_args.directory,
                                         parsed_args.format)
        config = self.client.get_default_config()

        try:
            fileutils.ensure_tree(os.path.dirname(file_path))
            fileutils.delete_if_exists(file_path)

            with open(file_path, 'w') as stream:
                data_utils.safe_dump(parsed_args.format, stream, config)
        except (OSError, IOError):
            msg = 'Could not store configuration at {}.'
            raise error.InvalidFileException(msg.format(file_path))

        msg = "Configuration was stored in {path}\n"
        self.app.stdout.write(msg.format(path=file_path))


class SnapshotGetLink(SnapshotMixIn, base.BaseShowCommand):
    """Show link to download diagnostic snapshot."""

    columns = ('status',
               'link')

    def take_action(self, parsed_args):
        data = self.client.get_by_id(parsed_args.id)
        if data['name'] != 'dump':
            msg = "Task with id {0} is not a snapshot generation task"
            raise error.ActionException(msg.format(data['id']))
        if data['status'] != 'ready':
            data['link'] = None
        else:
            data['link'] = self.client.connection.root + data['message']

        data = data_utils.get_display_data_single(self.columns, data)
        return self.columns, data
