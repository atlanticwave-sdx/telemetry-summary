# -*- coding: utf-8 -*-
"""
Class designed to support the packet summary building process,
following a specific schema in a continuous feed cycle.
"""
import copy
import datetime
import random
import time


class TelemetryPacket:
    """
    This class will provide all the methods to create and maintain
    the packet summary creation as a continuous feed process.
    """

    def __init__(self, _influxdb, setting, n_seconds=2):

        self.n_seconds = n_seconds

        self.influxdb = _influxdb

        self.packet_info = None

        self.sources = dict()

        self.topology = setting.topology

        self.list_result = list()

        self.setting_up()

    def setting_up(self):
        """
        Method in charge of the initialization of basic attributes
        on the Packet Summary information structure.
        :return: None
        """

        for key, val in self.topology.items():
            self.sources[key] = dict()
            for elem in val:
                self.sources[key][elem] = dict()
                self.sources[key][elem]['sequence_number'] = random.randint(100000, 400000)
                self.sources[key][elem]['in_octets'] = random.randint(20, 100)
                self.sources[key][elem]['out_octets'] = random.randint(25, 100)
                self.sources[key][elem]['in_packets'] = random.randint(30, 100)
                self.sources[key][elem]['out_packets'] = random.randint(35, 100)

    def packet_refresher(self):
        """
        Methods in charge of update the accumulative
        information relative to the packet summary.
        :return: None
        """

        for _, val in self.sources.items():
            for _, in_val in val.items():
                in_val['in_octets'] = in_val['in_octets'] + 1
                in_val['out_octets'] = in_val['out_octets'] + 1
                in_val['in_packets'] = in_val['in_packets'] + 1
                in_val['out_packets'] = in_val['out_packets'] + 1

    def packet_builder(self):
        """
        Method in charge of create the whole packet summary
        structure following the structure and schema proposed.
        :return: None
        """

        self.list_result.clear()
        for key, val in self.sources.items():
            for in_key, in_val in val.items():
                curr_time = time.time_ns()
                _date_time = datetime.datetime.fromtimestamp(curr_time / 1e9)

                self.packet_info = dict({"measurement": "telemetry_summary"})
                self.packet_info['time'] = '{}{:03.0f}'.format(
                    _date_time.strftime('%Y-%m-%dT%H:%M:%S.%f'), curr_time % 1e9)
                self.packet_info['tags'] = dict()
                self.packet_info['tags']['version'] = '1.0'
                self.packet_info['tags']['source'] = key
                self.packet_info['tags']['sequence_number'] = in_val['sequence_number']
                self.packet_info['tags']['service_id'] = in_key

                min_total_delay = random.randint(5, 400)
                max_total_delay = random.randint(min_total_delay, 1200)
                optimizations_counter = random.randint(1, 5)
                path_changes_counter = random.randint(1, 5)

                self.packet_info['fields'] = dict()
                self.packet_info['fields']['in_octets'] = in_val['in_octets']
                self.packet_info['fields']['out_octets'] = in_val['out_octets']
                self.packet_info['fields']['in_packets'] = in_val['in_packets']
                self.packet_info['fields']['out_packets'] = in_val['out_packets']
                self.packet_info['fields']['min_total_delay'] = min_total_delay
                self.packet_info['fields']['max_total_delay'] = max_total_delay
                self.packet_info['fields']['optimizations_counter'] = optimizations_counter
                self.packet_info['fields']['path_changes_counter'] = path_changes_counter

                self.list_result.append(copy.deepcopy(self.packet_info))

    def packet_sender(self):
        """
        Method in charge of keeping a loop that guarantees a continuous feed cycle.
        :return: None
        """

        while True:

            self.packet_builder()

            self.influxdb.save_to(self.list_result)

            self.packet_refresher()

            time.sleep(self.n_seconds)
