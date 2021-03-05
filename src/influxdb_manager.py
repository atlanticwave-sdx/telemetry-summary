# -*- coding: utf-8 -*-
"""
Class designed to manage all the interactions with the database,
from the establishment of the connection to saving the schema.
"""
import copy
from influxdb import InfluxDBClient


class InfluxDB:
    """
    This class will support InfluxDB database connections and operations.
    It includes methods to build the schema proposed to store on the database.
    """
    db_client = None
    table_results = None

    def __init__(self, setting):

        self.host = setting.database_info['host']
        self.port = setting.database_info['port']
        self.database = setting.database_info['database']

        self.local_connection = setting.database_info['local_connection'].lower() \
            in ['true', 'yes', 'y', '1']

        if not self.local_connection:
            self.username = setting.database_info['username']
            self.password = setting.database_info['password']

            self.ssl = setting.database_info['ssl'].lower() in ['true', 'yes', 'y', '1']

            self.verify_ssl = setting.database_info['verify_ssl'].lower() \
                in ['true', 'yes', 'y', '1']

        self.verbose_status = setting.verbose_status

        self.setting = setting

    def open_connection(self):
        """
        Method in charge of the connection creation with the InfluxDB database.
        In a local environment, it will remove the database content and
        tables related to the application to keep test consistency.
        :return:
        """

        if self.local_connection:
            # Local connection
            self.db_client = InfluxDBClient(self.host, self.port, self.database)

            # Begin - This will happen only on local execution
            if {'name': self.database} in self.db_client.get_list_database():
                self.db_client.delete_series(self.database, 'telemetry_summary')
            else:
                self.db_client.create_database(self.database)
            # End - This will happen only on local execution

        else:
            # Remote connection
            self.db_client = InfluxDBClient(self.host, self.port,
                                            username=self.username, password=self.password,
                                            database=self.database,
                                            ssl=self.ssl, verify_ssl=self.verify_ssl)
            self.db_client.create_database(self.database)

        # It assures to be pointing to the target table after the connection
        self.db_client.switch_database(self.database)

    def fetch_results(self):
        """
        Method in charge of retrieving all the information
        from the database given the user's specification
        :return:
        """

        self.table_results = \
            self.db_client.query('SELECT * '
                                 'FROM "' + self.database + '"."autogen"."telemetry_summary"')

        # It sorts/organizes the elements got from the database
        if not isinstance(self.table_results, list):
            # It creates a list based on the content retrieved from the database
            self.table_results = list(self.table_results.get_points(
                measurement='telemetry_summary'))

            # InfluxDB uses its tags as keys on its built-in sorting process
            # Switch ID tag is a string and intervenes on this process.
            # In order to get the records in a proper order based on their
            # insertion, we have to sort them based on the meta sequence number.
            self.table_results = sorted(self.table_results,
                                        key=lambda val: (val['time'], val['service_id']))
        else:
            # It creates a list based on the content retrieved from the database
            tmp = list()
            for result in self.table_results:
                tmp.append(list(result.get_points(measurement='telemetry_summary')))

            self.table_results = copy.deepcopy(tmp)
            tmp.clear()

        # It returns/visualizes the records resultant content
        for table_result in self.table_results:
            print(table_result)

    def save_to_database(self, json_structure):
        """
        Method in charge of the JSON structure
        storing process to the database
        :param json_structure:
        :return: None
        """

        # It saves the information to the database
        written = self.db_client.write_points(json_structure)

        if self.verbose_status:
            if written:
                print("Packet information saved to the database!")
            else:
                print("Errors saving the information to the database!")

    def save_to(self, data):
        """
        Method that supports the schema instantiation
        to save teh JSON Dataset.
        :param data: JSON data set with the telemetry information
        :return: None
        """
        try:
            self.save_to_database(data)

            if self.verbose_status:
                # It will visualize all the information on the console
                self.fetch_results()

        except ValueError as value_error:
            raise ValueError from value_error
