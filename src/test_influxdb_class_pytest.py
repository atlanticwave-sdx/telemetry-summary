from mock import MagicMock

from src.influxdb_manager import InfluxDB
from src.setting import Setting


class TestInfluxdbClass(object):
    """
    Class designated to test
    the InfluxDB interaction
    """

    def test_instance(self):

        setting = MagicMock()
        setting.database_info['host'] = 'test_localhost'

        # setting = Setting()
        # setting.read_params()

        influxdb = InfluxDB(setting)

        assert influxdb.host == 'localhost'
