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

from collections import namedtuple
import copy

from fuelclient.cli import error
from fuelclient import objects
from fuelclient.v1 import base_v1
from fuelclient.v1 import fuelversion


SplittedLabel = namedtuple('SplittedLabel', ['key', 'value', 'has_separator'])


class NodeClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Node
    _updatable_attributes = ('hostname', 'labels', 'name')

    def get_all(self, environment_id=None, labels=None):
        """Get nodes by specific environment or labels

        :param environment_id: Id of specific environment(cluster)
        :type environment_id: int
        :param labels: List of string labels for filtering nodes
        :type labels: list
        :returns: list -- filtered list of nodes
        """
        if environment_id is not None:
            result = self._entity_wrapper.get_by_env_id(
                cluster_id=environment_id)
        else:
            result = self._entity_wrapper.get_all_data()

        if labels:
            result = [item for item in result
                      if self._check_label(labels, item)]

        return result

    def undiscover_nodes(self, env_id=None, node_id=None, force=False):
        """Delete nodes from database. If node_id is None then all nodes
         from specified environment will be deleted.

        :param env_id: Id of env to delete nodes from database
        :type env_id: int
        :param node_id: Id of node to delete from database
        :type node_id: int
        :param force: Forces deletion of nodes regardless of their state
        :type force: bool
        :returns: list -- ids of nodes that were deleted from database
        """
        nodes = []
        if node_id is not None:
            nodes.append(self._entity_wrapper(obj_id=node_id).data)
        elif env_id is not None:
            nodes.extend(self.get_all(environment_id=env_id))
            if not nodes:
                raise error.ActionException(
                    "Cluster with id {0} does not exist or "
                    "does not contain any nodes".format(env_id)
                )
        else:
            raise ValueError('Expected either env_id or node_id args')

        # If 'force' flag is not specified then check nodes status
        if not force:
            online_nodes = [node for node in nodes if node['online']]
            if online_nodes:
                raise error.ActionException(
                    "Nodes with ids {0} cannot be deleted from database "
                    "because they are online. You might want to use the "
                    "--force option.".format(
                        [node['id'] for node in online_nodes]))

        node_ids = [node['id'] for node in nodes]
        objects.NodeCollection.delete_by_ids(node_ids)
        return node_ids

    def get_node_vms_conf(self, node_id):
        node = self._entity_wrapper(node_id)
        fuelversion.FuelVersionClient.check_advanced_feature()
        return node.get_node_vms_conf()

    def node_vms_create(self, node_id, config):
        node = self._entity_wrapper(node_id)
        fuelversion.FuelVersionClient.check_advanced_feature()
        return node.node_vms_create(config)

    def update(self, node_id, **updated_attributes):
        node = self._entity_wrapper(obj_id=node_id)

        for attr in updated_attributes:
            if attr not in self._updatable_attributes:
                msg = 'Only {0} are updatable'.format(
                    self._updatable_attributes)
                raise error.BadDataException(msg)

        return node.set(updated_attributes)

    def get_all_labels_for_nodes(self, node_ids=None):
        """Get list of labels for specific nodes. If no node_ids then all
        labels should be returned

        :param node_ids: List of node ids for filtering labels
        :type node_ids: list
        :returns: list -- filtered list of labels
        """
        labels = []

        result = self._entity_wrapper.get_all_data()

        if node_ids:
            result = filter(lambda node: str(node['id']) in node_ids, result)

        for node in result:
            for key, value in node.get('labels', []).items():
                labels.append({
                    'node_id': node.get('id'),
                    'label_name': key,
                    'label_value': value
                })

        return labels

    def set_labels_for_nodes(self, labels=None, node_ids=None):
        """Update nodes labels attribute with new data. If node_ids
        are empty list then labels will be updated on all nodes

        :param labels: List of string pairs `key=val` for labels
        :type labels: list
        :param node_ids: List of node ids where labels should be updated
        :type node_ids: list
        :return: list -- ids of nodes where labels were updated
        """
        data_to_return = []
        labels_to_update = {}

        for label in labels:
            key, val, _ = self._split_label(label)
            if not key:
                msg = 'Wrong label "{0}" was provided. Label key couldn\'t ' \
                      'be an empty string.'.format(label)
                raise error.LabelEmptyKeyError(msg)
            labels_to_update[key] = val

        if node_ids:
            for node_id in node_ids:
                node = self._entity_wrapper(obj_id=node_id)
                db_labels = copy.deepcopy(node.labels)
                db_labels.update(labels_to_update)

                result = self.update(node_id, **{'labels': db_labels})
                data_to_return.append(str(result.get('id')))
        else:
            nodes = self._entity_wrapper.get_all_data()
            for node in nodes:
                db_labels = copy.deepcopy(node['labels'])
                db_labels.update(labels_to_update)

                result = self.update(node['id'], **{'labels': db_labels})
                data_to_return.append(str(result.get('id')))

        return data_to_return

    def delete_labels_for_nodes(self, labels=None, node_ids=None):
        """Delete labels data from nodes labels. If node_ids are
        empty list then labels will be deleted on all nodes

        :param labels: List of string label keys
        :type labels: list
        :param node_ids: List of node ids where labels should be deleted
        :type node_ids: list
        :returns: list -- ids of nodes where labels were deleted
        """
        data_to_return = []

        if node_ids:
            nodes = (self._entity_wrapper(obj_id=n_id).data
                     for n_id in node_ids)
        else:
            nodes = self._entity_wrapper.get_all_data()

        for node in nodes:
            updated_labels = self._labels_after_delete(
                node['labels'], labels)

            result = self.update(node['id'], **{'labels': updated_labels})
            data_to_return.append(str(result.get('id')))

        return data_to_return

    def download_attributes(self, node_id, directory=None):
        node = self._entity_wrapper(node_id)
        attributes = node.get_node_attributes()
        return node.write_attribute(
            'attributes', attributes, directory=directory)

    def get_disks(self, node_id):
        """Download configuration of disks for a node

        :param node_id: Id of a node.
        :return:        dict with the configuration of disks for the node.

        """
        node = self._entity_wrapper(node_id)
        return node.get_attribute('disks')

    def get_default_disks(self, node_id):
        """Download default configuration of disks for a node

        :param node_id: Id of a node.
        :return:        dict with the default configuration of disks
                        for the node.

        """
        node = self._entity_wrapper(node_id)
        return node.get_default_attribute('disks')

    def set_disks(self, node_id, disks):
        """Upload and set configuration of disks for a node

        :param node_id:    Id of a node.
        :param interfaces: dict that contains valid configuration
                           for disks

        """
        node = self._entity_wrapper(node_id)
        return node.upload_node_attribute('disks', disks)

    def upload_attributes(self, node_id, directory=None):
        node = self._entity_wrapper(node_id)
        attributes = node.read_attribute('attributes', directory=directory)
        node.update_node_attributes(attributes)

    def get_interfaces(self, node_id):
        """Download configuration of interfaces for a node

        :param node_id: Id of a node.
        :return:        dict with the configuration of interfaces for the node.

        """
        node = self._entity_wrapper(node_id)
        return node.get_attribute('interfaces')

    def get_default_interfaces(self, node_id):
        """Download default configuration of interfaces for a node

        :param node_id: Id of a node.
        :return:        dict with the configuration of interfaces for the node.

        """
        node = self._entity_wrapper(node_id)
        return node.get_default_attribute('interfaces')

    def set_interfaces(self, node_id, interfaces):
        """Upload and set configuration of interfaces for a node

        :param node_id:    Id of a node.
        :param interfaces: dict that contains valid configuration
                           for interfaces

        """
        node = self._entity_wrapper(node_id)
        return node.upload_node_attribute('interfaces', interfaces)

    def _check_label(self, labels, item):
        checking_list = []

        for label in labels:
            key, val, has_separator = self._split_label(label)
            if key in item.get('labels'):
                if not has_separator:
                    checking_val = True
                else:
                    checking_val = item['labels'][key] == val
                checking_list.append(checking_val)

        return any(checking_list)

    @classmethod
    def _labels_after_delete(cls, labels, labels_to_delete):
        if not labels_to_delete:
            return {}

        db_labels = copy.deepcopy(labels)
        for label in labels_to_delete:
            label = label.strip()
            sl = cls._split_label(label)
            if sl.has_separator:
                if sl.key in db_labels and db_labels[sl.key] == sl.value:
                    db_labels.pop(sl.key)
            else:
                db_labels.pop(sl.key, None)

        return db_labels

    @staticmethod
    def _split_label(label):
        name, separator, value = label.partition('=')
        name = name.strip()
        value = value.strip()
        value = None if value == '' else value
        return SplittedLabel(name, value, bool(separator))


def get_client(connection):
    return NodeClient(connection)
