import customtkinter
import sched
from config import ConfigSingleton
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from data_api import read_modbus, DataType

import logging

logger = logging.getLogger(__name__)

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
        app: customtkinter.CTk,
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

        self.temp_on = False
        self.laser_on = False
        self.radio_on = False

        self.schedule_id = None

        self.running = True

        self.ui_event = None

        self.refresh()
        self.refresh_ui()

    def __del__(self):
        self.stop()

    def stop(self):
        self.running = False
        if self.schedule_id:
            try:
                self.scheduler.cancel(self.schedule_id)
            except:
                pass
        if self.ui_event:
            self.app.after_cancel(self.ui_event)

    def refresh_ui(
        self,
    ) -> None:
        if self.running:
            self.ui_event = self.app.after(1000, self.refresh_ui)
        self.temp_label.configure(fg_color="green" if self.temp_on else "grey")
        self.laser_label.configure(fg_color="green" if self.laser_on else "grey")
        self.radio_label.configure(fg_color="green" if self.radio_on else "grey")

    def refresh(
        self,
    ) -> None:
        try:
            self.temp_on = (
                read_modbus(
                    self.client,
                    TEMP_STABLE_INDICATOR_ADDRESS,
                    data_type=DataType.UINT16,
                )
                == TEMP_STABLE_INDICATOR_VALUE
            )

            self.laser_on = (
                read_modbus(
                    self.client,
                    LASER_CURRENT_LOCK_ADDRESS,
                    data_type=DataType.UINT16,
                )
                == LASER_CURRENT_LOCK_VALUE
            )

            self.radio_on = (
                read_modbus(
                    self.client,
                    RADIO_LOCK_ADDRESS,
                    data_type=DataType.UINT16,
                )
                == RADIO_LOCK_VALUE
            )
        except:
            logger.info(f"Exception when reading indicator data")

        if self.running:
            self.schedule_id = self.scheduler.enter(1, 5, self.refresh)
