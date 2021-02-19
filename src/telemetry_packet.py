# -*- coding: utf-8 -*-
import copy
import datetime
import random
import time


class TelemetryPacket:

    def __init__(self, _influxdb, setting, n_seconds=2):

        self.n_seconds = n_seconds

        self.influxdb = _influxdb

        self.packet_info = None

        self.sources = dict()

        self.topology = setting.topology

        # self.topology = dict()
        # self.topology['amlight_sdx_1'] = list()
        # self.topology['amlight_sdx_1'] = ['l2vpn_bra_usa_11242', 'l2vpn_bra_usa_11343']
        #
        # self.topology['amlight_sdx_2'] = list()
        # self.topology['amlight_sdx_2'] = ['l2vpn_bra_usa_22242', 'l2vpn_bra_usa_22343']
        #
        # self.topology['amlight_sdx_3'] = list()
        # self.topology['amlight_sdx_3'] = ['l2vpn_bra_usa_33242', 'l2vpn_bra_usa_33343']

        self.setting_up()

        self.list_result = list()

    def setting_up(self):

        for key, val in self.topology.items():
            self.sources[key] = dict()
            for elem in val:
                self.sources[key][elem] = dict()
                self.sources[key][elem]['sequence_number'] = random.randint(100000, 400000)
                self.sources[key][elem]['out_packets'] = random.randint(20, 100)
                self.sources[key][elem]['in_packets'] = random.randint(25, 100)
                self.sources[key][elem]['out_octets'] = random.randint(30, 100)
                self.sources[key][elem]['in_octets'] = random.randint(35, 100)

    def refresh(self):

        for key, val in self.sources.items():
            for in_key, in_val in val.items():
                in_val['in_octets'] = in_val['in_octets'] + 1
                in_val['out_octets'] = in_val['out_octets'] + 1
                in_val['in_packets'] = in_val['in_packets'] + 1
                in_val['out_packets'] = in_val['out_packets'] + 1

    def packet_builder(self):

        self.list_result.clear()
        for key, val in self.sources.items():
            for in_key, in_val in val.items():
                curr_time = time.time_ns()
                _date_time = datetime.datetime.fromtimestamp(curr_time / 1e9)

                self.packet_info = dict({"measurement": "telemetry_summary"})
                self.packet_info['time'] = '{}{:03.0f}'.format(_date_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                               curr_time % 1e9)
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

    def send_packet(self):

        while True:

            self.packet_builder()

            self.influxdb.save_to(self.list_result)

            self.refresh()

            time.sleep(self.n_seconds)
