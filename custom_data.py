import time
import threading
from config import ConfigSingleton
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from data_api import read_modbus, DataType, read_custom_data
import sched
import customtkinter

from datetime import datetime, timedelta

from enum import Enum
from collections import deque
import csv

import logging

logger = logging.getLogger(__name__)


class DataMode(Enum):
    SIN = 0
    DDS = 1


READ_SIN_DATA_CMD = ConfigSingleton().get_config()["READ_SIN_DATA_CMD"]
READ_DDS_DATA_CMD = ConfigSingleton().get_config()["READ_DDS_DATA_CMD"]
CUSTOM_PROTOCO_FREQUENCY = ConfigSingleton().get_config()["CUSTOM_PROTOCO_FREQUENCY"]
SLEEP_TIME_MS = ConfigSingleton().get_config()["SLEEP_TIME_MS"]
DATA_PRINT_AVG_COUNT = ConfigSingleton().get_config()["DATA_PRINT_AVG_COUNT"]
DISPLAY_TIME_RANGE = ConfigSingleton().get_config()["DISPLAY_TIME_RANGE"]
DATA_FREQUENCY = ConfigSingleton().get_config()["DATA_FREQUENCY"]


class CustomData:
    def __init__(
        self,
        modbus_client: ModbusClient,
        scheduler: sched.scheduler,
        data_mode: DataMode = DataMode.SIN,
    ) -> None:
        self.client = modbus_client
        self.scheduler = scheduler
        self.data_mode = data_mode
        self.stop_flag = threading.Event()
        self.processor = threading.Thread(
            target=self.process,
        )
        self.processor.daemon = True
        self.lock = threading.Lock()
        self.current_time = None
        self.sin_data = deque(maxlen=10)
        self.dds_data = deque(maxlen=10)

        self.original_sin_data = deque(maxlen=int(DISPLAY_TIME_RANGE * DATA_FREQUENCY))
        self.original_dds_data = deque(maxlen=int(DISPLAY_TIME_RANGE * DATA_FREQUENCY))

        self.processed_sin_data = deque(
            maxlen=int(DISPLAY_TIME_RANGE * DATA_FREQUENCY / DATA_PRINT_AVG_COUNT)
        )
        self.processed_dds_data = deque(
            maxlen=int(DISPLAY_TIME_RANGE * DATA_FREQUENCY / DATA_PRINT_AVG_COUNT)
        )

        self.sin_file = open("sin.csv", "w", newline="")
        self.sin_csv_writer = csv.writer(self.sin_file)

        self.dds_file = open("dds.csv", "w", newline="")
        self.dds_csv_writer = csv.writer(self.dds_file)
        self.download_on = False

        self.running = False

        self.scheduler_id = None

    def __del__(self):
        self.stop()

    def get_processed_data(self):
        with self.lock:
            if self.data_mode == DataMode.SIN:
                return self.processed_sin_data
            else:
                return self.processed_dds_data

    def get_original_data(self):
        with self.lock:
            if self.data_mode == DataMode.SIN:
                return self.original_sin_data
            else:
                return self.original_dds_data

    def process_data(
        self, q_data, original_data: deque, processed_data: deque, csv_writer
    ):
        if q_data:
            t, data = q_data.popleft()

            orginal_timed_data = [
                (t + timedelta(milliseconds=i), x) for i, x in enumerate(data)
            ]
            original_data.extend(orginal_timed_data)

            avgs = []
            for i in range(0, len(data), DATA_PRINT_AVG_COUNT):
                chunk = data[i : i + DATA_PRINT_AVG_COUNT]
                if len(chunk) > 0:  # Make sure the chunk is not empty
                    avgs.append(sum(chunk) / len(chunk))

            timed_data = [
                (t + timedelta(milliseconds=i * DATA_PRINT_AVG_COUNT), x)
                for i, x in enumerate(avgs)
            ]

            processed_data.extend(timed_data)
            if self.download_on:
                csv_writer.writerows([[val] for _, val in orginal_timed_data])
        else:
            pass

    def process(self):
        while not self.stop_flag.is_set():
            current_data_mode = DataMode.SIN
            with self.lock:
                current_data_mode = self.data_mode
            if current_data_mode == DataMode.SIN:
                self.process_data(
                    self.sin_data,
                    self.original_sin_data,
                    self.processed_sin_data,
                    self.sin_csv_writer,
                )
            else:
                self.process_data(
                    self.dds_data,
                    self.original_dds_data,
                    self.processed_dds_data,
                    self.dds_csv_writer,
                )
            time.sleep(0.05)

    def start(self):
        if not self.processor.is_alive():
            self.processor.start()

    def set_download(self, value: bool):
        self.download_on = value

    def set_mode(self, data_mode: DataMode):
        with self.lock:
            self.data_mode = data_mode
        if not self.running:
            self.running = True
            self.start()
            self.refresh()

    def stop(self):
        self.running = False
        self.stop_flag.set()

        if self.processor.is_alive():
            self.processor.join(timeout=5)

        if self.sin_file:
            self.sin_file.close()
            self.sin_file = None

        if self.dds_file:
            self.dds_file.close()
            self.dds_file = None

        if self.scheduler_id:
            try:
                self.scheduler.cancel(self.scheduler_id)
            except:
                pass

    def refresh(
        self,
    ) -> None:
        current_data_mode = DataMode.SIN
        with self.lock:
            current_data_mode = self.data_mode
        self.current_time = (
            datetime.now()
            if self.current_time is None
            else self.current_time + timedelta(milliseconds=CUSTOM_PROTOCO_FREQUENCY)
        )
        self.client.connect()
        response = read_custom_data(
            self.client.socket,
            READ_SIN_DATA_CMD
            if current_data_mode == DataMode.SIN
            else READ_DDS_DATA_CMD,
            DataType.FLOAT32 if current_data_mode == DataMode.SIN else DataType.UINT32,
        )
        if response is not None and len(response) > 0:
            if current_data_mode == DataMode.SIN:
                self.sin_data.append((self.current_time, response))
            else:
                self.dds_data.append((self.current_time, response))
            logger.info(
                f"Get {len(response)} data points from device at {self.current_time}"
            )
        if self.running:
            self.scheduler_id = self.scheduler.enter(
                SLEEP_TIME_MS * 1.0 / 1000, 1, self.refresh
            )
