import os

import mock

from fuelclient import fuelclient_settings
from fuelclient.tests.unit.v1 import base


class TestSettings(base.UnitTestCase):

    @mock.patch('shutil.copy')
    @mock.patch('os.chmod')
    @mock.patch('os.path.exists')
    def test_config_generation(self, m_exists, m_chmod, m_copy):
        project_dir = os.path.dirname(fuelclient_settings.__file__)

        expected_mode = 0o600
        expected_default = os.path.join(project_dir,
                                        'fuelclient_settings.yaml')
        expected_path = os.path.expanduser('~/.config/fuel_client.yaml')

        fuelclient_settings._SETTINGS = None
        m_exists.return_value = False

        fuelclient_settings.get_settings()

        m_copy.assert_called_once_with(expected_default, expected_path)
        m_chmod.assert_called_once_with(expected_path, expected_mode)
