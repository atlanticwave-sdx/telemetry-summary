# -*- coding: utf-8 -*-
import configparser
from os import path


class Setting:
    """
    This class will support the initialization of all
    the attributes through the console arguments provided.
    """
    database_info = None

    def __init__(self, ini_file='config.ini'):
        """
        Instance initialization and config.ini interpretation
        """
        self.verbose_status = False
        self.database_info = None
        self.topology = None

        self.tags = None
        self.fields = None
        self.counters = None
        self.ini_file = ini_file

    @staticmethod
    def check_database_attributes(database_info):
        keys = [*database_info]
        setting_parameters = ['host', 'port', 'username', 'password', 'database'
            , 'local_connection', 'ssl', 'verify_ssl']

        missing = (list(list(set(setting_parameters) - set(keys)) +
                        list(set(keys) - set(setting_parameters))))

        if len(missing) > 0:
            raise AttributeError("'Setting' object has no attribute '{}'".format(missing))
        return True

    def read_params(self):
        """
        Method to set the execution setting given the user's input.
        The input might be a File or a connection to a RabbitMQ queue
        :return: None
        """
        config = configparser.ConfigParser()

        my_path = path.abspath(path.dirname(__file__))
        environment_filename = path.join(my_path, self.ini_file)

        try:
            with open(environment_filename) as env_filename:
                config.read_file(env_filename)

                self.verbose_status = config.getboolean('DEFAULT', 'verbose')
                self.database_info = dict(set(config.items('INFLUXDB'))
                                          - set(config.items('DEFAULT')))

                if self.check_database_attributes(self.database_info):

                    self.topology = dict(set(config.items('TOPOLOGY'))
                                         - set(config.items('DEFAULT')))
                    for key, val in self.topology.items():
                        self.topology[key] = val.strip('][').split(', ')

                    self.tags = dict(set(config.items('MAP')) - set(config.items('DEFAULT')))
                    self.fields = dict(set(config.items('MAP.Timestamp'))
                                       - set(config.items('MAP')))
                    if 'counters' in self.fields:
                        self.counters = self.fields['counters'].strip('][').split(', ')

            if self.verbose_status:
                print("Set up done!")

        except FileNotFoundError as err:
            raise FileNotFoundError(err, "You must specify a valid INI file") from err

        except AttributeError as err:
            raise AttributeError(err,
                                 "It's missed some information "
                                 "relative to the database setting") from err

        except configparser.NoOptionError as err:
            raise KeyError(err, "wrong structure in the INI file") from err
