#!/usr/bin/env python3
import sys
from argparse import ArgumentParser, ArgumentError
from sys import argv
import threading

from src.influxdb_manager import InfluxDB
from src.setup.setting import Setting
from src.telemetry_packet import TelemetryPacket

if __name__ == '__main__':

    opts = ArgumentParser()

    try:
        opts.add_argument("-f", "--file", dest="ini_file",
                          help="read the configuration file (ini)")
        arguments = opts.parse_args(argv[1:])

        if arguments.ini_file is None and ('-f' in argv[1:] or "--file" in argv[1:]):
            raise ArgumentError(None, "You must specify a file name")

        if arguments.ini_file is not None:
            setting = Setting(arguments.ini_file)
        else:
            setting = Setting()

        setting.read_params()

        influxdb = InfluxDB(setting)
        influxdb.open_connection()

        telemetry_packet = TelemetryPacket(influxdb, setting)

    try:
        thread = threading.Thread(target=telemetry_packet.packet_sender(), daemon=True)
        thread.start()
        thread.join()

    except FileNotFoundError as err:
        print(err.strerror)

    except KeyError as err:
        print(err)

    except KeyboardInterrupt as err:
        print(err)

    except ArgumentError as err:
        print(err)
        opts.parse_args(args=['--help'])

    except AttributeError as err:
        print(err)

    finally:
        sys.exit(0)
