import time
import tkinter as tk
import threading
import sched
from config import ConfigSingleton
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from data_api import read_modbus, DataType

TEMP_STABLE_INDICATOR_ADDRESS = ConfigSingleton().get_config()[
    "TEMP_STABLE_INDICATOR_ADDRESS"
]
LASER_CURRENT_LOCK_ADDRESS = ConfigSingleton().get_config()[
    "LASER_CURRENT_LOCK_ADDRESS"
]
RADIO_LOCK_ADDRESS = ConfigSingleton().get_config()["RADIO_LOCK_ADDRESS"]

TEMP_STABLE_INDICATOR_VALUE = ConfigSingleton().get_config()[
    "TEMP_STABLE_INDICATOR_VALUE"
]
LASER_CURRENT_LOCK_VALUE = ConfigSingleton().get_config()["LASER_CURRENT_LOCK_VALUE"]
RADIO_LOCK_VALUE = ConfigSingleton().get_config()["RADIO_LOCK_VALUE"]


class Indicator:
    def __init__(
        self,
        modbus_client: ModbusClient,
        scheduler: sched.scheduler,
        app: tk.Tk,
        temp_label,
        laser_label,
        radio_label,
    ) -> None:
        self.client = modbus_client
        self.scheduler = scheduler
        self.app = app
        self.temp_label = temp_label
        self.laser_label = laser_label
        self.radio_label = radio_label

        self.schedule_id = self.scheduler.enter(0, 5, self.refresh)

    def __del__(self):
        self.stop()

    def stop(self):
        try:
            self.scheduler.cancel(self.schedule_id)
        except:
            pass

    def update_incidator(self, address, true_value, label):
        try:
            if (
                read_modbus(
                    self.client,
                    address,
                    data_type=DataType.UINT16,
                )
                == true_value
            ):
                self.app.after(0, lambda: label.config(bg="green"))
            else:
                self.app.after(0, lambda: label.config(bg="grey"))
        except Exception:
            print(f"Exception when reading indicator data")

    def refresh(
        self,
    ) -> None:
        self.schedule_id = self.scheduler.enter(1, 5, self.refresh)
        self.update_incidator(
            TEMP_STABLE_INDICATOR_ADDRESS,
            TEMP_STABLE_INDICATOR_VALUE,
            self.temp_label,
        )
        self.update_incidator(
            LASER_CURRENT_LOCK_ADDRESS,
            LASER_CURRENT_LOCK_VALUE,
            self.laser_label,
        )
        self.update_incidator(
            RADIO_LOCK_ADDRESS,
            RADIO_LOCK_VALUE,
            self.radio_label,
        )
