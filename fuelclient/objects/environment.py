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

from operator import attrgetter
import os
import shutil

from fuelclient.cli import error
from fuelclient.cli.serializers import listdir_without_extensions
from fuelclient.objects.base import BaseObject
from fuelclient.objects.task import DeployTask
from fuelclient.objects.task import Task


class Environment(BaseObject):

    class_api_path = "clusters/"
    instance_api_path = "clusters/{0}/"
    deployment_tasks_path = 'clusters/{0}/deployment_tasks'
    deployment_tasks_graph_path = 'clusters/{0}/deploy_tasks/graph.gv'
    attributes_path = 'clusters/{0}/attributes'
    network_template_path = 'clusters/{0}/network_configuration/template'

    @classmethod
    def create(cls, name, release_id, net_segment_type):
        data = {
            "nodes": [],
            "tasks": [],
            "name": name,
            "release_id": release_id,
            "net_segment_type": net_segment_type,
        }

        data = cls.connection.post_request("clusters/", data)
        return cls.init_with_data(data)

    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self._testruns_ids = []

    def set(self, data):
        return self.connection.put_request(
            "clusters/{0}/".format(self.id),
            data
        )

    def delete(self):
        return self.connection.delete_request(
            "clusters/{0}/".format(self.id)
        )

    def assign(self, nodes, roles):
        return self.connection.post_request(
            "clusters/{0}/assignment/".format(self.id),
            [{'id': node.id, 'roles': roles} for node in nodes]
        )

    def unassign(self, nodes):
        return self.connection.post_request(
            "clusters/{0}/unassignment/".format(self.id),
            [{"id": n} for n in nodes]
        )

    def get_all_nodes(self):
        from fuelclient.objects.node import Node
        return sorted(map(
            Node.init_with_data,
            self.connection.get_request(
                "nodes/?cluster_id={0}".format(self.id)
            )
        ), key=attrgetter('id'))

    def unassign_all(self):
        nodes = self.get_all_nodes()
        if not nodes:
            raise error.ActionException(
                "Environment with id={0} doesn't have nodes to remove."
                .format(self.id)
            )
        return self.connection.post_request(
            "clusters/{0}/unassignment/".format(self.id),
            [{"id": n.id} for n in nodes]
        )

    def deploy_changes(self, dry_run=False, noop_run=False):
        deploy_data = self.connection.put_request(
            "clusters/{0}/changes".format(self.id),
            {}, dry_run=int(dry_run), noop_run=int(noop_run)
        )
        return DeployTask.init_with_data(deploy_data)

    def redeploy_changes(self, dry_run=False, noop_run=False):
        deploy_data = self.connection.put_request(
            "clusters/{0}/changes/redeploy".format(self.id),
            {}, dry_run=int(dry_run), noop_run=int(noop_run)
        )
        return DeployTask.init_with_data(deploy_data)

    def get_network_data_path(self, directory=os.curdir):
        return os.path.join(
            os.path.abspath(directory),
            "network_{0}".format(self.id)
        )

    def get_settings_data_path(self, directory=os.curdir):
        return os.path.join(
            os.path.abspath(directory),
            "settings_{0}".format(self.id)
        )

    def get_network_template_data_path(self, directory=None):
        directory = directory or os.curdir
        return os.path.join(
            os.path.abspath(directory),
            "network_template_{0}".format(self.id)
        )

    def write_network_data(self, network_data, directory=os.curdir,
                           serializer=None):
        self._check_dir(directory)
        return (serializer or self.serializer).write_to_path(
            self.get_network_data_path(directory),
            network_data
        )

    def write_settings_data(self, settings_data, directory=os.curdir,
                            serializer=None):
        self._check_dir(directory)
        return (serializer or self.serializer).write_to_path(
            self.get_settings_data_path(directory),
            settings_data
        )

    def write_network_template_data(self, template_data, directory=None,
                                    serializer=None):
        directory = directory or os.curdir
        return (serializer or self.serializer).write_to_path(
            self.get_network_template_data_path(directory),
            template_data
        )

    def read_network_data(self, directory=os.curdir,
                          serializer=None):
        self._check_dir(directory)
        network_file_path = self.get_network_data_path(directory)
        return (serializer or self.serializer).read_from_file(
            network_file_path)

    def read_settings_data(self, directory=os.curdir, serializer=None):
        self._check_dir(directory)
        settings_file_path = self.get_settings_data_path(directory)
        return (serializer or self.serializer).read_from_file(
            settings_file_path)

    def _check_file_path(self, file_path):
        if not os.path.exists(file_path):
            raise error.InvalidFileException(
                "File '{0}' doesn't exist.".format(file_path))

    def _check_dir(self, directory):
        if not os.path.exists(directory):
            raise error.InvalidDirectoryException(
                "Directory '{0}' doesn't exist.".format(directory))
        if not os.path.isdir(directory):
            raise error.InvalidDirectoryException(
                "Error: '{0}' is not a directory.".format(directory))

    def read_network_template_data(self, directory=os.curdir,
                                   serializer=None):
        """Used by 'fuel' command line utility."""
        self._check_dir(directory)
        network_template_file_path = self.get_network_template_data_path(
            directory)
        return (serializer or self.serializer).\
            read_from_file(network_template_file_path)

    def read_network_template_data_from_file(self, file_path=None,
                                             serializer=None):
        """Used by 'fuel2' command line utility."""
        return (serializer or self.serializer).\
            read_from_full_path(file_path)

    @property
    def status(self):
        return self.get_fresh_data()['status']

    @property
    def settings_url(self):
        return self.attributes_path.format(self.id)

    @property
    def default_settings_url(self):
        return self.settings_url + "/defaults"

    @property
    def network_url(self):
        return "clusters/{id}/network_configuration/neutron".format(
            **self.data
        )

    @property
    def network_template_url(self):
        return self.network_template_path.format(self.id)

    @property
    def network_verification_url(self):
        return self.network_url + "/verify"

    def get_network_data(self):
        return self.connection.get_request(self.network_url)

    def get_settings_data(self):
        return self.connection.get_request(self.settings_url)

    def get_default_settings_data(self):
        return self.connection.get_request(self.default_settings_url)

    def get_network_template_data(self):
        return self.connection.get_request(self.network_template_url)

    def set_network_data(self, data):
        return self.connection.put_request(
            self.network_url, data)

    def set_settings_data(self, data, force=False):
        if force:
            result = self.connection.put_request(
                self.settings_url, data, force=1)
        else:
            result = self.connection.put_request(
                self.settings_url, data)
        return result

    def verify_network(self):
        return self.connection.put_request(
            self.network_verification_url, self.get_network_data())

    def set_network_template_data(self, data):
        return self.connection.put_request(
            self.network_template_url, data)

    def delete_network_template_data(self):
        return self.connection.delete_request(self.network_template_url)

    def _get_fact_dir_name(self, fact_type, directory=os.path.curdir):
        return os.path.join(
            os.path.abspath(directory),
            "{0}_{1}".format(fact_type, self.id))

    def _get_fact_url(self, fact_type, default=False):
        fact_url = "clusters/{0}/orchestrator/{1}/{2}".format(
            self.id, fact_type, 'defaults/' if default else ''
        )
        return fact_url

    def get_default_facts(self, fact_type, **kwargs):
        """Gets default facts for cluster.
        :param fact_type: the type of facts (deployment, provision)
        """
        return self.get_facts(fact_type, default=True, **kwargs)

    def get_facts(self, fact_type, default=False, nodes=None, split=None):
        """Gets facts for cluster.
        :param fact_type: the type of facts (deployment, provision)
        :param default: if True, the default facts will be retrieved
        :param nodes: if specified, get facts only for selected nodes
        :param split: if True, the node part and common part will be split
        """
        params = {}
        if nodes is not None:
            params['nodes'] = ','.join(str(x) for x in nodes)
        if split is not None:
            params['split'] = str(int(split))

        facts = self.connection.get_request(
            self._get_fact_url(fact_type, default=default), params=params
        )
        if not facts:
            raise error.ServerDataException(
                "There is no {0} info for this "
                "environment!".format(fact_type)
            )
        return facts

    def upload_facts(self, fact_type, facts):
        self.connection.put_request(self._get_fact_url(fact_type), facts)

    def delete_facts(self, fact_type):
        self.connection.delete_request(self._get_fact_url(fact_type))

    def read_fact_info(self, fact_type, directory, serializer=None):
        return getattr(
            self, "read_{0}_info".format(fact_type)
        )(fact_type, directory=directory, serializer=serializer)

    def write_facts_to_dir(self, fact_type, facts,
                           directory=os.path.curdir, serializer=None):
        dir_name = self._get_fact_dir_name(fact_type, directory=directory)
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name)
        if isinstance(facts, dict):
            engine_file_path = os.path.join(dir_name, "engine")
            (serializer or self.serializer).write_to_path(
                engine_file_path, facts["engine"])
            facts = facts["nodes"]

            def name_builder(fact):
                return fact['name']
        else:
            def name_builder(fact):
                if 'role' in fact:
                    # from 9.0 the deployment info is serialized only per node
                    return "{role}_{uid}".format(**fact)
                return fact['uid']

        for _fact in facts:
            fact_path = os.path.join(
                dir_name,
                name_builder(_fact)
            )
            (serializer or self.serializer).write_to_path(fact_path, _fact)
        return dir_name

    def read_deployment_info(self, fact_type,
                             directory=os.path.curdir, serializer=None):
        self._check_dir(directory)
        dir_name = self._get_fact_dir_name(fact_type, directory=directory)
        self._check_dir(dir_name)
        return map(
            lambda f: (serializer or self.serializer).read_from_file(f),
            [os.path.join(dir_name, json_file)
             for json_file in listdir_without_extensions(dir_name)]
        )

    def read_provisioning_info(self, fact_type,
                               directory=os.path.curdir, serializer=None):
        dir_name = self._get_fact_dir_name(fact_type, directory=directory)
        node_facts = map(
            lambda f: (serializer or self.serializer).read_from_file(f),
            [os.path.join(dir_name, fact_file)
             for fact_file in listdir_without_extensions(dir_name)
             if "engine" != fact_file]
        )
        engine = (serializer or self.serializer).read_from_file(
            os.path.join(dir_name, "engine"))
        return {
            "engine": engine,
            "nodes": node_facts
        }

    # TODO(vkulanov): remove method when deprecate old cli
    def get_testsets(self):
        return self.connection.get_request(
            'testsets/{0}'.format(self.id),
            ostf=True
        )

    @property
    def is_customized(self):
        data = self.get_fresh_data()
        return data["is_customized"]

    # TODO(vkulanov): remove method when deprecate old cli
    def is_in_running_test_sets(self, test_set):
        return test_set["testset"] in self._test_sets_to_run

    # TODO(vkulanov): remove method when deprecate old cli
    def run_test_sets(self, test_sets_to_run, ostf_credentials=None):
        self._test_sets_to_run = test_sets_to_run

        def make_test_set(name):
            result = {
                "testset": name,
                "metadata": {
                    "config": {},
                    "cluster_id": self.id,
                }
            }
            if ostf_credentials:
                creds = result['metadata'].setdefault(
                    'ostf_os_access_creds', {})
                if 'tenant' in ostf_credentials:
                    creds['ostf_os_tenant_name'] = ostf_credentials['tenant']
                if 'username' in ostf_credentials:
                    creds['ostf_os_username'] = ostf_credentials['username']
                if 'password' in ostf_credentials:
                    creds['ostf_os_password'] = ostf_credentials['password']
            return result

        tests_data = [make_test_set(ts) for ts in test_sets_to_run]
        testruns = self.connection.post_request(
            "testruns", tests_data, ostf=True)
        self._testruns_ids = [tr['id'] for tr in testruns]
        return testruns

    # TODO(vkulanov): remove method when deprecate old cli
    def get_state_of_tests(self):
        return [
            self.connection.get_request(
                "testruns/{0}".format(testrun_id), ostf=True)
            for testrun_id in self._testruns_ids
        ]

    def stop(self):
        return Task.init_with_data(
            self.connection.put_request(
                "clusters/{0}/stop_deployment/".format(self.id),
                {}
            )
        )

    def reset(self, force=False):
        return Task.init_with_data(
            self.connection.put_request(
                "clusters/{0}/reset/?force={force}".format(self.id,
                                                           force=int(force)),
                {}
            )
        )

    def _get_method_url(self, method_type, nodes, force=False, noop_run=False):
        endpoint = "clusters/{0}/{1}/?nodes={2}".format(
            self.id,
            method_type,
            ','.join(map(lambda n: str(n.id), nodes)))

        if force:
            endpoint += '&force=1'
        if noop_run:
            endpoint += '&noop_run=1'

        return endpoint

    def install_selected_nodes(self, method_type, nodes):
        return Task.init_with_data(
            self.connection.put_request(
                self._get_method_url(method_type, nodes),
                {}
            )
        )

    def execute_tasks(self, nodes, tasks, force, noop_run):
        return Task.init_with_data(
            self.connection.put_request(
                self._get_method_url('deploy_tasks', nodes=nodes, force=force,
                                     noop_run=noop_run),
                tasks
            )
        )

    def get_tasks(self, skip=None, end=None, start=None, include=None):
        """Stores logic to filter tasks by known parameters.

        :param skip: list of tasks or None
        :param end: string or None
        :param start: string or None
        :param include: list or None
        """
        tasks = [t['id'] for t in self.get_deployment_tasks(
                 end=end, start=start, include=include)]
        if skip:
            tasks_to_execute = set(tasks) - set(skip)
            return list(tasks_to_execute)
        return tasks

    def get_deployment_tasks(self, end=None, start=None, include=None):
        url = self.deployment_tasks_path.format(self.id)
        return self.connection.get_request(
            url, params={
                'end': end,
                'start': start,
                'include': include})

    def update_deployment_tasks(self, data):
        url = self.deployment_tasks_path.format(self.id)
        return self.connection.put_request(url, data)

    def get_attributes(self):
        return self.connection.get_request(self.settings_url)

    def update_attributes(self, data, force=False):
        if force:
            result = self.connection.put_request(
                self.settings_url, data, force=1)
        else:
            result = self.connection.put_request(
                self.settings_url, data)
        return result

    def get_deployment_tasks_graph(self, tasks, parents_for=None, remove=None):
        url = self.deployment_tasks_graph_path.format(self.id)
        params = {
            'tasks': ','.join(tasks),
            'parents_for': parents_for,
            'remove': ','.join(remove) if remove else None,
        }
        resp = self.connection.get_request_raw(url, params=params)
        resp.raise_for_status()
        return resp.text

    def spawn_vms(self):
        url = 'clusters/{0}/spawn_vms/'.format(self.id)
        return self.connection.put_request(url, {})

    def _get_ip_addrs_url(self, vips=True, ip_addr_id=None):
        """Generate ip address management url.

        :param vips: manage vip properties of ip address
        :type vips: bool
        :param ip_addr_id: ip address identifier
        :type ip_addr_id: int
        :return: url
        :rtype: str
        """
        ip_addr_url = "clusters/{0}/network_configuration/ips/".format(self.id)
        if ip_addr_id:
            ip_addr_url += '{0}/'.format(ip_addr_id)
        if vips:
            ip_addr_url += 'vips/'

        return ip_addr_url

    def get_default_vips_data_path(self):
        """Get path where VIPs data is located.
        :return: path
        :rtype: str
        """
        return os.path.join(
            os.path.abspath(os.curdir),
            "vips_{0}".format(self.id)
        )

    def get_vips_data(self, ip_address_id=None, network=None,
                      network_role=None):
        """Get one or multiple vip data records.

        :param ip_address_id: ip addr id could be specified to download single
                            vip if no ip_addr_id specified multiple entities is
                            returned respecting network and network_role
                            filters
        :type ip_address_id: int
        :param network: network id could be specified to filter vips
        :type network: int
        :param network_role: network role could be specified to filter vips
        :type network_role: string
        :return: response JSON
        :rtype: list of dict
        """
        params = {}
        if network:
            params['network'] = network
        if network_role:
            params['network-role'] = network_role

        result = self.connection.get_request(
            self._get_ip_addrs_url(True, ip_addr_id=ip_address_id),
            params=params
        )
        if ip_address_id is not None:  # single vip is returned
            # wrapping with list is required to respect case when administrator
            # is downloading vip address info to change it and upload
            # back. Uploading works only with lists of records.
            result = [result]
        return result

    def write_vips_data_to_file(self, vips_data, serializer=None,
                                file_path=None):
        """Write VIP data to the given path.

        :param vips_data: vip data
        :type vips_data: list of dict
        :param serializer: serializer
        :param file_path: path
        :type file_path: str
        :return: path to resulting file
        :rtype: str
        """
        serializer = serializer or self.serializer

        if file_path:
            return serializer.write_to_full_path(
                file_path,
                vips_data
            )
        else:
            return serializer.write_to_path(
                self.get_default_vips_data_path(),
                vips_data
            )

    def read_vips_data_from_file(self, file_path=None, serializer=None):
        """Read VIPs data from given path.

        :param file_path: path
        :type file_path: str
        :param serializer: serializer object
        :type serializer: object
        :return: data
        :rtype: list|object
        """
        self._check_file_path(file_path)
        return (serializer or self.serializer).read_from_file(file_path)

    def set_vips_data(self, data):
        """Sending VIPs data to the Nailgun API.

        :param data: VIPs data
        :type data: list of dict
        :return: request result
        :rtype: object
        """
        return self.connection.put_request(self._get_ip_addrs_url(), data)

    def create_vip(self, **vip_kwargs):
        """Create VIP through request to Nailgun API

        :param vip_data: attributes of the VIP to be created
        """
        return self.connection.post_request(self._get_ip_addrs_url(),
                                            vip_kwargs)

    def get_enabled_plugins(self):
        """Get list of enabled plugins ids.

        :returns: plugins ids list
        :rtype: list[int]
        """
        attrs = self.get_attributes()['editable']
        enabled_plugins_ids = []
        for attr_name in attrs:
            metadata = attrs[attr_name].get('metadata', {})
            if metadata.get('class') == 'plugin' and metadata.get('enabled'):
                enabled_plugins_ids.append(metadata['chosen_id'])
        return enabled_plugins_ids
