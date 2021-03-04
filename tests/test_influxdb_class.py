# -*- coding: utf-8 -*-
import pytest
import requests_mock
from influxdb import InfluxDBClient
from mock import MagicMock, patch

from src.influxdb_manager import InfluxDB


class TestInfluxdbClass(object):
    """
    Class designated to test
    the InfluxDB interaction
    """
    @pytest.fixture
    def setting_mock(self):
        setting = MagicMock()
        setting.database_info = {'ssl': 'True',
                                 'password': "test_pss",
                                 'database': 'test_telemetry_summary',
                                 'username': "test_usr",
                                 'verify_ssl': 'True',
                                 'local_connection': 'True',
                                 'port': '8086',
                                 'host': 'localhost'}
        setting.read_params()

        return setting

    @staticmethod
    def mock_db_instance():
        """
        Method designed to prepare the some stage
        in the middle end test related to the
        InfluxDB instance creation and performance
        :return: Objects to reuse as primaries elements
        on the database instantiation
        """
        setting = MagicMock()
        setting.database_info = {'ssl': 'True',
                                 'password': "test_pss",
                                 'database': 'test_telemetry_summary',
                                 'username': "test_usr",
                                 'verify_ssl': 'True',
                                 'local_connection': 'True',
                                 'port': '8086',
                                 'host': 'localhost'}
        setting.read_params()
        db_instance = InfluxDB(setting)
        db_client = InfluxDBClient(db_instance.host,
                                   db_instance.port,
                                   db_instance.database)
        db_instance.db_client = db_client

        point = [{'measurement': 'telemetry_summary',
                  'time': '2021-02-28T20:25:49.688331Z',
                  'tags': {'version': '1.0', 'source': 'amlight_sdx_1',
                           'sequence_number': '283289', 'service_id': 'l2vpn_bra_usa_11242'},
                  'fields': {'in_octets': 57, 'out_octets': 80,
                             'in_packets': 98, 'out_packets': 78,
                             'min_total_delay': 74, 'max_total_delay': 459,
                             'optimizations_counter': 3, 'path_changes_counter': 5}}]

        return db_instance, point, db_client

    def test_setting_host(self):
        setting = MagicMock()
        setting.database_info = {'ssl': 'True',
                                 'password': "test_pss",
                                 'database': 'test_telemetry_summary',
                                 'username': "test_usr",
                                 'verify_ssl': 'True',
                                 'local_connection': 'True',
                                 'port': '8086',
                                 'host': 'remote_localhost'}
        setting.read_params()
        influxdb = InfluxDB(setting)

        assert influxdb.host == 'remote_localhost'

    def test_setting_in_localhost(self):
        setting = MagicMock()
        setting.database_info = {'ssl': 'True',
                                 'password': "test_pss",
                                 'database': 'test_telemetry_summary',
                                 'username': "test_usr",
                                 'verify_ssl': 'True',
                                 'local_connection': 'False',
                                 'port': '8086',
                                 'host': 'remote_localhost'}
        setting.read_params()
        influxdb = InfluxDB(setting)

        assert influxdb.username == 'test_usr'

    def test_open_connection_createdb(self, setting_mock):

        influxdb = InfluxDB(setting_mock)
        influxdb.open_connection()

        assert influxdb.db_client._baseurl == 'http://localhost:8086'

    def test_open_connection_cleardb(self, setting_mock):

        influxdb = InfluxDB(setting_mock)
        influxdb.open_connection()

        assert influxdb.db_client._baseurl == 'http://localhost:8086'
        influxdb.db_client.drop_database(setting_mock.database_info['database'])

    def test_save_to_database(self):
        """
        Method to test the encoding process on storing
        :return: assert about the data expected
        """
        with requests_mock.Mocker() as m:
            m.register_uri(
                requests_mock.POST,
                "http://localhost:8086/write",
                status_code=204
            )

            db_instance, point, _ = self.mock_db_instance()

            db_instance.save_to_database(point)

            assert m.last_request.body.decode('utf-8') == ('telemetry_summary,'
                                                           'sequence_number=283289,'
                                                           'service_id=l2vpn_bra_usa_11242,'
                                                           'source=amlight_sdx_1,'
                                                           'version=1.0 '
                                                           'in_octets=57i,'
                                                           'in_packets=98i,'
                                                           'max_total_delay=459i,'
                                                           'min_total_delay=74i,'
                                                           'optimizations_counter=3i,'
                                                           'out_octets=80i,'
                                                           'out_packets=78i,'
                                                           'path_changes_counter=5i '
                                                           '1614543949688331000\n')

    def test_fetch_results(self):
        """
        Method to test the database fetching process based on a sample response
        :return: assert about the value expected
        """
        example_response = (
            '{"results": ['
            '{"series": '
            '[{"measurement": "telemetry_summary", '
            '"columns": ["time", "source", "sequence_number", "service_id"], '
            '"values": [["2021-02-28T20:25:49.688331Z", "amlight_sdx_1", 283289, "l2vpn_bra_usa_11242"]]}]}, '
            '{"series": '
            '[{"measurement": "telemetry_summary", '
            '"columns": ["time", "source", "sequence_number", "service_id"], '
            '"values": [["2021-02-28T20:51:39.512470Z", "amlight_sdx_2", 394767, "l2vpn_bra_usa_22343"]]}]}]}'
        )

        with requests_mock.Mocker() as m:
            m.register_uri(
                requests_mock.GET,
                "http://localhost:8086/query",
                text=example_response
            )

            db_instance, point, _ = self.mock_db_instance()

            db_instance.fetch_results()

        assert db_instance.table_results == [
            [{'time': '2021-02-28T20:25:49.688331Z', 'source': 'amlight_sdx_1',
              'sequence_number': 283289, 'service_id': 'l2vpn_bra_usa_11242'}],
            [{'time': '2021-02-28T20:51:39.512470Z', 'source': 'amlight_sdx_2',
              'sequence_number': 394767, 'service_id': 'l2vpn_bra_usa_22343'}]
        ]

    def test_fetch_results_simple(self):
        """
        Method to test the database fetching process based on a sample response
        :return: assert about the value expected
        """
        example_response = (
            '{"results": ['
            '{"series": '
            '[{"measurement": "telemetry_summary", '
            '"columns": ["time", "source", "sequence_number", "service_id"], '
            '"values": [["2021-02-28T20:25:49.688331Z", "amlight_sdx_1", 283289, "l2vpn_bra_usa_11242"]]}]}]}'
        )

        with requests_mock.Mocker() as m:
            m.register_uri(
                requests_mock.GET,
                "http://localhost:8086/query",
                text=example_response
            )

            db_instance, point, _ = self.mock_db_instance()

            db_instance.fetch_results()

        assert db_instance.table_results == [{'time': '2021-02-28T20:25:49.688331Z', 'source': 'amlight_sdx_1',
                                              'sequence_number': 283289, 'service_id': 'l2vpn_bra_usa_11242'}]

    def test_save_to(self, setting_mock):
        data = [
            {'measurement': 'telemetry_summary', 'time': '2021-02-28T23:41:39.263264263264000',
             'tags': {'version': '1.0', 'source': 'amlight_sdx_2',
                      'sequence_number': 341187, 'service_id': 'l2vpn_bra_usa_22242'},
             'fields': {'in_octets': 36, 'out_octets': 92, 'in_packets': 40, 'out_packets': 81,
                        'min_total_delay': 228, 'max_total_delay': 1153,
                        'optimizations_counter': 1, 'path_changes_counter': 4}},
            {'measurement': 'telemetry_summary', 'time': '2021-02-28T23:41:39.263739263738880',
             'tags': {'version': '1.0', 'source': 'amlight_sdx_2',
                      'sequence_number': 335956, 'service_id': 'l2vpn_bra_usa_22343'},
             'fields': {'in_octets': 57, 'out_octets': 37, 'in_packets': 97, 'out_packets': 86,
                        'min_total_delay': 313, 'max_total_delay': 1197,
                        'optimizations_counter': 2, 'path_changes_counter': 2}}]

        influxdb = InfluxDB(setting_mock)
        influxdb.open_connection()

        influxdb.save_to(data)

        influxdb.fetch_results()

        assert influxdb.table_results == [{'in_octets': 36, 'in_packets': 40,
                                           'max_total_delay': 1153, 'min_total_delay': 228,
                                           'optimizations_counter': 1,
                                           'out_octets': 92, 'out_packets': 81,
                                           'path_changes_counter': 4,
                                           'sequence_number': '341187',
                                           'service_id': 'l2vpn_bra_usa_22242',
                                           'source': 'amlight_sdx_2',
                                           'time': '2021-02-28T23:41:39.263264Z',
                                           'version': '1.0'},
                                          {'in_octets': 57, 'in_packets': 97,
                                           'max_total_delay': 1197, 'min_total_delay': 313,
                                           'optimizations_counter': 2,
                                           'out_octets': 37, 'out_packets': 86,
                                           'path_changes_counter': 2,
                                           'sequence_number': '335956',
                                           'service_id': 'l2vpn_bra_usa_22343',
                                           'source': 'amlight_sdx_2',
                                           'time': '2021-02-28T23:41:39.263739Z',
                                           'version': '1.0'}]

    def test_save_to_exception(self, setting_mock):

        influxdb = InfluxDB(setting_mock)
        influxdb.open_connection()

        data = MagicMock()
        with patch('src.influxdb_manager.InfluxDB.save_to_database', side_effect=ValueError):
            with pytest.raises(Exception) as excinfo:

                influxdb.save_to(data)
                influxdb.fetch_results()

            assert str(excinfo.typename) == "ValueError"


def test_save_to_database_ext(capsys):
    """
    Method designed to test actions on the
    database related to the storing process.
    It tests the storing actions of an empty
    set evaluating the console output.
    :param capsys:
    :return:
    """
    example_response = (
        '{"results": ['
        '{"series": '
        '[{"measurement": "telemetry_summary", '
        '"columns": ["time", "source", "sequence_number", "service_id"], '
        '"values": '
        '[]}]}]}'
    )

    with requests_mock.Mocker() as m:
        m.register_uri(
            requests_mock.POST,
            "http://localhost:8086/write",
            status_code=204
        )

        m.register_uri(
            requests_mock.GET,
            "http://localhost:8086/query",
            text=example_response
        )

        db_instance, point, db_client = TestInfluxdbClass.mock_db_instance()

        with patch.object(db_client, 'write_points') as mlp:
            mlp.return_value = False
            db_instance.save_to_database(point)

            out, _ = capsys.readouterr()

            assert out == 'Errors saving the information to the database!\n'
