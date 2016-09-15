#    Copyright 2014 Mirantis, Inc.
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
from itertools import chain
import os

from fuelclient import __version__
from fuelclient.cli.error import ArgumentException
from fuelclient.client import DefaultAPIClient

substitutions = {
    # replace from: to
    "env": "environment",
    "nodes": "node",
    "statuses": "status",
    "net": "network",
    "rel": "release",
    "list": "--list",
    "set": "--set",
    "delete": "--delete",
    "download": "--download",
    "upload": "--upload",
    "default": "--default",
    "create": "--create",
    "remove": "--delete",
    "config": "--config",
    "--roles": "--role",
    "help": "--help",
    "change-password": "--change-password",
    "hostname": "--hostname",
}


def group(*args, **kwargs):
    required = kwargs.get("required", False)
    return (required,) + args


class ArrayAction(argparse.Action):
    """Custom argparse.Action subclass to store ids

    :returns: list of ids
    """
    def __call__(self, parser, namespace, values, option_string=None):
        list_ids = [int(value) for value in chain(*values)]
        setattr(namespace, self.dest, list_ids)


class NodeAction(argparse.Action):
    """Custom argparse.Action subclass to store node identity

    :returns: list of ids
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            node_identities = set(chain(*values))
            input_macs = set(n for n in node_identities if ":" in n)
            only_ids = set()
            for _id in (node_identities - input_macs):
                try:
                    only_ids.add(int(_id))
                except ValueError:
                    raise ArgumentException(
                        "'{0}' is not valid node id.".format(_id))
            if input_macs:
                nodes_mac_to_id_map = dict(
                    (n["mac"], n["id"])
                    for n in DefaultAPIClient.get_request("nodes/")
                )
                for short_mac in input_macs:
                    target_node = None
                    for mac in nodes_mac_to_id_map:
                        if mac.endswith(short_mac):
                            target_node = mac
                            break
                    if target_node:
                        only_ids.add(nodes_mac_to_id_map[target_node])
                    else:
                        raise ArgumentException(
                            'Node with mac endfix "{0}" was not found.'
                            .format(short_mac)
                        )
            node_ids = [int(node_id) for node_id in only_ids]
            setattr(namespace, self.dest, node_ids)


class SetAction(argparse.Action):
    """Custom argparse.Action subclass to store distinct values

    :returns: Set of arguments
    """
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            getattr(namespace, self.dest).update(values)
        except AttributeError:
            setattr(namespace, self.dest, set(values))


def get_debug_arg():
    return {
        "args": ["--debug"],
        "params": {
            "dest": "debug",
            "action": "store_true",
            "help": "prints details of all HTTP request",
            "default": False
        }
    }


def get_version_arg():
    return {
        "args": ["-v", "--version"],
        "params": {
            "action": "version",
            "version": __version__
        }
    }


def get_arg(name, flags=None, aliases=None, help_=None, **kwargs):
    name = name.replace("_", "-")
    args = ["--" + name, ]
    if flags is not None:
        args.extend(flags)
    if aliases is not None:
        substitutions.update(
            dict((alias, args[0]) for alias in aliases)
        )
    all_args = {
        "args": args,
        "params": {
            "dest": name,
            "help": help_ or name
        }
    }
    all_args["params"].update(kwargs)
    return all_args


def get_boolean_arg(name, **kwargs):
    kwargs.update({
        "action": "store_true",
        "default": False
    })
    return get_arg(name, **kwargs)


def get_env_arg(required=False):
    return get_int_arg(
        "env",
        flags=("--env-id",),
        help="environment id",
        required=required
    )


def get_single_task_arg(required=False):
    return get_int_arg(
        "task",
        flags=("--task-id", "--tid"),
        help="task id",
        required=required
    )


def get_new_password_arg(help_msg):
    return get_str_arg(
        "newpass",
        flags=("--new-pass",),
        help=help_msg,
        required=False
    )


def get_str_arg(name, **kwargs):
    default_kwargs = {
        "action": "store",
        "type": str,
        "default": None
    }
    default_kwargs.update(kwargs)
    return get_arg(name, **default_kwargs)


def get_int_arg(name, **kwargs):
    default_kwargs = {
        "action": "store",
        "type": int,
        "default": None
    }
    default_kwargs.update(kwargs)
    return get_arg(name, **default_kwargs)


def get_array_arg(name, **kwargs):
    default_kwargs = {
        "action": ArrayAction,
        "nargs": '+',
        "type": lambda v: v.split(","),
        "default": None
    }
    default_kwargs.update(kwargs)
    return get_arg(name, **default_kwargs)


def get_set_type_arg(name, **kwargs):
    default_kwargs = {
        "type": lambda v: v.split(','),
        "action": SetAction,
        "default": None
    }
    default_kwargs.update(kwargs)
    return get_arg(name, **default_kwargs)


def get_delete_from_db_arg(help_msg):
    return get_boolean_arg("delete-from-db", help=help_msg)


def get_deployment_tasks_arg(help_msg):
    return get_boolean_arg(
        "deployment-tasks", help=help_msg)


def get_attributes_arg(help_msg):
    return get_boolean_arg("attributes", help=help_msg)


def get_sync_deployment_tasks_arg():
    return get_boolean_arg(
        "sync-deployment-tasks",
        help="Update tasks for each release.")


def get_dry_run_deployment_arg():
    return get_boolean_arg(
        "dry-run",
        dest='dry_run',
        help="Specifies to dry-run a deployment by configuring task executor"
             "to dump the deployment graph to a dot file.")


def get_noop_run_deployment_arg():
    return get_boolean_arg(
        "noop",
        dest='noop_run',
        help="Specifies noop-run deployment configuring tasks executor to run "
             "puppet and shell tasks in noop mode and skip all other. "
             "Stores noop-run result summary in nailgun database")


def get_file_pattern_arg():
    return get_str_arg(
        "filepattern",
        flags=("--fp", "--file-pattern"),
        default="*tasks.yaml",
        help="Provide unix file pattern to filter tasks with files.")


def get_node_name_arg(help_msg):
    return get_str_arg("name", help=help_msg)


def get_hostname_arg(help_msg):
    return get_str_arg("hostname", help=help_msg)


def get_network_arg(help_msg):
    return get_boolean_arg("network", flags=("--net",), help=help_msg)


def get_force_arg(help_msg):
    return get_boolean_arg("force", flags=("-f",), help=help_msg)


def get_disk_arg(help_msg):
    return get_boolean_arg("disk", help=help_msg)


def get_deploy_arg(help_msg):
    return get_boolean_arg("deploy", help=help_msg)


def get_provision_arg(help_msg):
    return get_boolean_arg("provision", help=help_msg)


def get_role_arg(help_msg):
    return get_set_type_arg("role", flags=("-r",), help=help_msg)


def get_single_role_arg(help_msg):
    return get_str_arg("role", flags=('--role', ), help=help_msg)


def get_check_arg(help_msg):
    return get_set_type_arg("check", help=help_msg)


def get_ostf_username_arg():
    return get_str_arg(
        "ostf_username",
        dest="ostf_username",
        help="OSTF username",
        required=False
    )


def get_ostf_password_arg():
    return get_str_arg(
        "ostf_password",
        dest="ostf_password",
        help="OSTF password",
        required=False
    )


def get_ostf_tenant_name_arg():
    return get_str_arg(
        "ostf_tenant_name",
        dest="ostf_tenant_name",
        help="OSTF tenant name",
        required=False
    )


def get_change_password_arg(help_msg):
    return get_boolean_arg("change-password", help=help_msg)


def get_name_arg(help_msg):
    return get_str_arg("name", flags=("--env-name",), help=help_msg)


def get_graph_endpoint():
    return get_arg(
        'end',
        action="store",
        default=None,
        help="Specify endpoint for the graph traversal.",
        metavar='TASK',
    )


def get_graph_startpoint():
    return get_arg(
        'start',
        action="store",
        default=None,
        help="Specify start point for the graph traversal.",
        metavar='TASK',
    )


def get_skip_tasks():
    return get_arg(
        'skip',
        nargs='+',
        default=[],
        help="Get list of tasks to be skipped.",
        metavar='TASK',
    )


def get_tasks():
    return get_arg(
        'tasks',
        nargs='+',
        default=[],
        help="Get list of tasks to be executed.",
        metavar='TASK',
    )


def get_parents_arg():
    return get_arg(
        'parents-for',
        help="Get parent for given task",
        metavar='TASK',
    )


def get_remove_type_arg(types):
    return get_arg(
        'remove',
        nargs='+',
        default=[],
        choices=types,
        help="Select task types to remove from graph.",
    )


def get_nst_arg(help_msg):
    return get_arg("nst",
                   flags=("--net-segment-type",),
                   action="store",
                   choices=("gre", "vlan", "tun"),
                   help_=help_msg,
                   default="vlan")


def get_all_arg(help_msg):
    return get_boolean_arg("all", help=help_msg)


def get_create_arg(help_msg):
    return get_boolean_arg(
        "create",
        flags=("-c", "--env-create"),
        help=help_msg)


def get_download_arg(help_msg):
    return get_boolean_arg("download", flags=("-d",), help=help_msg)


def get_list_arg(help_msg):
    return get_boolean_arg("list", flags=("-l",), help=help_msg)


def get_dir_arg(help_msg):
    return get_str_arg("dir", default=os.curdir, help=help_msg)


def get_file_arg(help_msg):
    return get_str_arg("file", help=help_msg)


def get_verify_arg(help_msg):
    return get_boolean_arg("verify", flags=("-v",), help=help_msg)


def get_upload_arg(help_msg):
    return get_boolean_arg("upload", flags=("-u",), help=help_msg)


def get_default_arg(help_msg):
    return get_boolean_arg("default", help=help_msg)


def get_set_arg(help_msg):
    return get_boolean_arg("set", flags=("-s",), help=help_msg)


def get_delete_arg(help_msg):
    return get_boolean_arg("delete", help=help_msg)


def get_execute_arg(help_msg):
    return get_boolean_arg("execute", help=help_msg)


def get_assign_arg(help_msg):
    return get_boolean_arg("assign", help=help_msg)


def get_group_arg(help_msg):
    return get_set_type_arg("group", help=help_msg)


def get_node_group_arg(help_msg):
    return get_set_type_arg("nodegroup", flags=("--node-group",),
                            help=help_msg)


def get_vlan_arg(help_msg):
    return get_int_arg("vlan", help=help_msg)


def get_cidr_arg(help_msg):
    return get_str_arg("cidr", help=help_msg)


def get_gateway_arg(help_msg):
    return get_str_arg("gateway", help=help_msg)


def get_meta_arg(help_msg):
    return get_str_arg("meta", help=help_msg)


def get_create_network_arg(help_msg):
    return get_boolean_arg(
        "create",
        flags=("-c", "--create"),
        help=help_msg)


def get_network_group_arg(help_msg):
    return get_set_type_arg("network", help=help_msg)


def get_release_arg(help_msg, required=False):
    return get_int_arg(
        "release",
        flags=("--rel",),
        required=required,
        help=help_msg)


def get_render_arg(help_msg):
    return get_str_arg(
        "render",
        metavar='INPUT',
        help=help_msg)


def get_tred_arg(help_msg):
    return get_boolean_arg("tred", help=help_msg)


def get_node_arg(help_msg):
    default_kwargs = {
        "action": NodeAction,
        "flags": ("--node-id",),
        "nargs": '+',
        "type": lambda v: v.split(","),
        "default": None,
        "help": help_msg
    }
    return get_arg("node", **default_kwargs)


def get_single_node_arg(help_msg):
    return get_int_arg('node', flags=('--node-id',), help=help_msg)


def get_task_arg(help_msg):
    return get_array_arg(
        'task',
        flags=("--task-id", "--tid"),
        help=help_msg
    )


def get_config_id_arg(help_msg):
    return get_int_arg(
        'config-id',
        help=help_msg)


def get_deleted_arg(help_msg):
    return get_boolean_arg(
        'deleted', help=help_msg)


def get_plugin_install_arg(help_msg):
    return get_str_arg(
        "install",
        metavar='PLUGIN_FILE',
        help=help_msg
    )


def get_plugin_remove_arg(help_msg):
    return get_str_arg(
        "remove",
        metavar='PLUGIN_NAME==VERSION',
        help=help_msg
    )


def get_plugin_register_arg(help_msg):
    return get_str_arg(
        "register",
        metavar='PLUGIN_NAME==VERSION',
        help=help_msg
    )


def get_plugin_unregister_arg(help_msg):
    return get_str_arg(
        "unregister",
        metavar='PLUGIN_NAME==VERSION',
        help=help_msg
    )


def get_plugin_update_arg(help_msg):
    return get_str_arg(
        "update",
        metavar='PLUGIN_FILE',
        help=help_msg
    )


def get_plugin_downgrade_arg(help_msg):
    return get_str_arg(
        "downgrade",
        metavar='PLUGIN_FILE',
        help=help_msg
    )


def get_plugin_sync_arg(help_msg):
    return get_boolean_arg(
        "sync",
        help=help_msg
    )


def get_plugin_arg(help_msg):
    return get_array_arg(
        'plugin',
        flags=('--plugin-id',),
        help=help_msg
    )


def get_notify_all_messages_arg(help_msg):
    return get_boolean_arg(
        'all',
        flags=('-a',),
        help=help_msg
    )


def get_notify_mark_as_read_arg(help_msg):
    return get_str_arg(
        "mark-as-read",
        flags=('-r',),
        nargs='+',
        help=help_msg,
    )


def get_notify_message_arg(help_msg):
    return get_str_arg(
        "send",
        nargs='+',
        flags=('-m',),
        help=help_msg,
    )


def get_notify_send_arg(help_msg):
    return get_str_arg(
        "send",
        flags=("--send",),
        help=help_msg
    )


def get_notify_topic_arg(help_msg):
    return get_str_arg(
        "topic",
        flags=("--topic",),
        choices=(
            'discover',
            'done',
            'error',
            'warning',
            'release'
        ),
        help=help_msg
    )


def get_vip_arg(help_msg):
    return get_boolean_arg(
        "vip",
        flags=("--vip",),
        help=help_msg
    )


def get_vip_name_arg(help_msg):
    return get_str_arg(
        "vip-name",
        flags=("--name",),
        help=help_msg
    )


def get_vip_namespace_arg(help_msg, required=False):
    return get_str_arg(
        "vip-namespace",
        flags=("--namespace",),
        required=required,
        help=help_msg
    )


def get_ip_address_arg(help_msg):
    return get_str_arg(
        "ip-address",
        flags=("--address", "--ip-addr"),
        help=help_msg
    )


def get_ip_id_arg(help_msg):
    return get_int_arg(
        "ip-address-id",
        flags=("--ip-address-id",),
        help=help_msg
    )


def get_network_id_arg(help_msg):
    return get_int_arg(
        "network",
        flags=("--network",),
        help=help_msg
    )


def get_network_role_arg(help_msg):
    return get_str_arg(
        "network-role",
        flags=("--network-role",),
        help=help_msg
    )


def get_upload_file_arg(help_msg):
    return get_str_arg(
        "upload",
        flags=("-u", "--upload",),
        help=help_msg
    )


def get_status_arg(help_msg):
    default_kwargs = {
        "flags": ("--status",),
        "default": None,
        "help": help_msg
    }
    return get_arg("status", **default_kwargs)


def get_deployment_node_arg(help_msg):
    default_kwargs = {
        "flags": ("--node-id",),
        "default": None,
        "help": help_msg
    }
    return get_arg("node", **default_kwargs)


def get_tasks_names_arg(help_msg):
    default_kwargs = {
        "flags": ("-d", "--task-name",),
        "default": None,
        "help": help_msg
    }
    return get_arg("task-name", **default_kwargs)


def get_show_parameters_arg(help_msg):
    default_kwargs = {
        "flags": ("-p", "--show-parameters",),
        "help": help_msg
    }
    return get_boolean_arg("show-parameters", **default_kwargs)


def get_include_summary_arg(help_msg):
    default_kwargs = {
        "flags": ("--include-summary",),
        "help": help_msg
    }
    return get_boolean_arg("include-summary", **default_kwargs)


def get_not_split_facts_args():
    kwargs = {
        "action": "store_false",
        "default": True,
        "dest": "split",
        "help": "Do not split deployment info for node and cluster parts."
    }
    return get_arg('no-split', **kwargs)
