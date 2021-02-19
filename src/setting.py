# -*- coding: utf-8 -*-
import configparser
from os import path


class Setting:
    """
    This class will support the initialization of all
    the attributes through the console arguments provided.
    """
    def __init__(self):
        """
        Instance initialization and config.ini interpretation
        """
        self.verbose_status = False
        self.database_info = None
        self.topology = None

        self.tags = None
        self.fields = None
        self.counters = None

    def read_params(self):
        """
        Method to set the execution setting given the user's input.
        The input might be a File or a connection to a RabbitMQ queue
        :return: None
        """
        config = configparser.ConfigParser()

        my_path = path.abspath(path.dirname(__file__))
        environment_filename = path.join(my_path, 'config.ini')

        with open(environment_filename) as f:
            config.read_file(f)

            self.verbose_status = config.getboolean('DEFAULT', 'verbose')
            self.database_info = dict(set(config.items('INFLUXDB')) - set(config.items('DEFAULT')))
            self.topology = dict(set(config.items('TOPOLOGY')) - set(config.items('DEFAULT')))
            self.tags = dict(set(config.items('MAP')) - set(config.items('DEFAULT')))
            self.fields = dict(set(config.items('MAP.Timestamp')) - set(config.items('MAP')))

            for key, val in self.topology.items():
                self.topology[key] = val.strip('][').split(', ')

            if 'counters' in self.fields:
                self.counters = self.fields['counters'].strip('][').split(', ')

        if self.verbose_status:
            print("Set up done!")
