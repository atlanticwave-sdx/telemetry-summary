#!/usr/bin/env python3
import sys
import threading

from src.influxdb_manager import InfluxDB
from src.setting import Setting
from src.telemetry_packet import TelemetryPacket

if __name__ == '__main__':

    setting = Setting()
    setting.read_params()

    influxdb = InfluxDB(setting)
    influxdb.open_connection()

    telemetry_packet = TelemetryPacket(influxdb, setting)

    try:
        thread = threading.Thread(target=telemetry_packet.packet_sender(), daemon=True)
        thread.start()
        thread.join()
    except KeyboardInterrupt:
        sys.exit(0)
