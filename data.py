import csv

import logging

logger = logging.getLogger(__name__)


class ModbusData:
    def __init__(self):
        self.file = open("data.csv", "w", newline="")
        self.csv_writer = csv.writer(self.file)
        self.data_buf = []

    def add_data(self, time, int_data, float_data):
        time_format = "%H:%M:%S"
        time_str = time.strftime(time_format)
        self.data_buf.append([time_str, int_data, float_data])

        if len(self.data_buf) >= 500:
            self.csv_writer.writerows(self.data_buf)
            self.data_buf = []

    def __del__(self):
        self.csv_writer.writerows(self.data_buf)
        if self.file:
            self.file.close()
            self.file = None
