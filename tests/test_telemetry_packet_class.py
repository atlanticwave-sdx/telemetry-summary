# -*- coding: utf-8 -*-
import sys

from mock import MagicMock, patch

from src.influxdb_manager import InfluxDB
from src.setup.setting import Setting
from src.telemetry_packet import TelemetryPacket


class TestTelemetryPacketClass(object):

    def test_setting_up(self):

        test_args = ['test', '-f', 'config_test.ini']

        with patch.object(sys, 'argv', test_args):

            setting = Setting()
            setting.read_params()
            influxdb = InfluxDB(setting)
            influxdb.open_connection()

            with patch('random.randint', MagicMock(return_value=12345)):
                telemetry_packet = TelemetryPacket(influxdb, setting)

        assert telemetry_packet.sources['amlight_sdx_1']['l2vpn_bra_usa_11242']['sequence_number'] == 12345

    def test_packet_refresher(self):
        test_args = ['test', '-f', 'config_test.ini']

        with patch.object(sys, 'argv', test_args):
            setting = Setting()
            setting.read_params()
            influxdb = InfluxDB(setting)
            influxdb.open_connection()

            with patch('random.randint', MagicMock(return_value=12345)):
                telemetry_packet = TelemetryPacket(influxdb, setting)
                telemetry_packet.packet_builder()
                telemetry_packet.packet_refresher()

        assert telemetry_packet.sources['amlight_sdx_2']['l2vpn_bra_usa_22242']['out_octets'] == 12346

    def test_packet_builder(self):
        test_args = ['test', '-f', 'config_test.ini']

        with patch.object(sys, 'argv', test_args):
            setting = Setting()
            setting.read_params()
            influxdb = InfluxDB(setting)
            influxdb.open_connection()

            with patch('random.randint', MagicMock(return_value=12345)):
                telemetry_packet = TelemetryPacket(influxdb, setting)
                telemetry_packet.packet_builder()

        assert telemetry_packet.packet_info['fields']['optimizations_counter'] == 12345
