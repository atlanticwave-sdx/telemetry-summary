# -*- coding: utf-8 -*-
import copy
from influxdb import InfluxDBClient


class InfluxDB:
    """
    This class will support InfluxDB database connections and operations.
    It includes methods to build the schema proposed to store on the database.
    """

    db_client = None

    def __init__(self, setting):

        self.host = setting.database_info['host']
        self.port = setting.database_info['port']
        self.database = setting.database_info['database']

        self.table_results = None
        self.verbose_status = setting.verbose_status

    def open_connection(self, local=True):
        """
        Method in charge of the connection creation with the InfluxDB database.
        In a local environment, it will remove the database content and
        tables related to the application to keep test consistency.
        :param local:
        :return:
        """

        # Local connection
        self.db_client = InfluxDBClient(self.host, self.port, self.database)

        # Remote connection
        # self.db_client = InfluxDBClient(self.host, self.port,
        #                                 self.username, self.password,
        #                                 ssl=True, verify_ssl=True)

        if local:
            # Begin - This will happen only on local execution
            self.db_client.delete_series(self.database, 'telemetry_summary')
            self.db_client.create_database(self.database)

            self.db_client.get_list_database()
            # End - This will happen only on local execution

        # It assures to be pointing to the target table after the connection
        self.db_client.switch_database(self.database)

    def fetch_results(self):
        """
        Method in charge of retrieving all the information
        from the database given the user's specification
        :return:
        """

        # It builds up the query based on the filtering possibilities
        # bind_params, query, where = self.filtering()
        #
        # # It retrieves the data from the database base on the query
        # if where is not '':
        #     query = query + ' WHERE ' + where
        #     self.table_results = self.db_client.query(query, bind_params=bind_params)
        #
        # else:
        #     self.table_results = self.db_client.query('SELECT * '
        #                                               'FROM "proofoftransit"."autogen"."telemetry_summary"')

        self.table_results = self.db_client.query('SELECT * '
                                                  'FROM "telemetry_summary"."autogen"."telemetry_summary"')

        # It sorts/organizes the elements got from the database
        if not isinstance(self.table_results, list):
            # It creates a list based on the content retrieved from the database
            self.table_results = list(self.table_results.get_points(measurement='telemetry_summary'))

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
        Method in charge of the JSON structure storing
        process to the database if and only if its path
        information differs from the last inserted
        :param json_structure:
        :return: None
        """

        # It saves the information to the database
        written = self.db_client.write_points(json_structure)

        if written and self.verbose_status:
            print("Packet information saved to the database!")
        elif not written:
            print("Errors saving the information to the database!")

    def save_to(self, data):
        """
        Method that supports the schema creation given the
        JSON dataset, as well as the instantiation to save it.
        :param data: JSON data set with the packet information
        :return: None
        """
        try:
            self.save_to_database(data)

            if self.verbose_status:
                # It will visualize all the information on the console
                self.fetch_results()

        except ValueError:
            raise ValueError
