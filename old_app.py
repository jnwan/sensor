from connect import scan_ports_and_connect, connect_port
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import tkinter as tk
import threading
import time
import matplotlib.pyplot as plt
from data import ModbusData
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from datetime import datetime

from chart import LiveTimeSeriesPlot

import logging

logger = logging.getLogger(__name__)


def read_modbus_registers(modbus_client: ModbusClient, slave_id, starting_address):
    try:
        modbus_client.connect()
        # Read holding registers from the Modbus RTU device
        response = modbus_client.read_holding_registers(
            starting_address, 4, unit=slave_id
        )
        if response.isError():
            logger.info(f"Error reading Modbus registers: {response}")
        else:
            ints = response.registers[:2]
            floats = response.registers[2:]
            int_decoder = BinaryPayloadDecoder.fromRegisters(
                ints, byteorder=Endian.Big, wordorder=Endian.Little
            )
            float_decoder = BinaryPayloadDecoder.fromRegisters(
                floats, byteorder=Endian.Big, wordorder=Endian.Little
            )
            int_val = int_decoder.decode_32bit_uint()
            float_val = float_decoder.decode_32bit_float()
            logger.info(
                f"Data from Modbus device (Slave {slave_id}), "
                f"starting address {starting_address}: {response.registers}, "
                f"decoded value int: {int_val}, float: {float_val}"
            )
            return (int_val, float_val)
    except Exception as e:
        logger.info(f"Error: {e}")
    return []


def connect():
    global client, read_action1, button_action, port_entry, thread1
    thread1 = None
    port = port_entry.get()
    client = None
    if port:
        client = connect_port(port)
        if client:
            status_text = f"Connection Success? {client.connect()}"
        else:
            status_text = f"Couldn't connect to {port}"
    else:
        clients = scan_ports_and_connect()
        status_text = ""
        if len(clients) == 0:
            status_text = "No Modbus client found!"
        elif len(clients) > 1:
            status_text = "More than 1 Modbus devices found!"
        else:
            client = clients[0]
            status_text = f"Connection Success? {client.connect()}"

    status.config(state=tk.NORMAL)  # Allow editing
    status.delete(1.0, tk.END)  # Clear previous content
    status.insert(tk.END, status_text)  # Insert new content
    status.config(state=tk.DISABLED)  # Disable editing
    if client is not None:
        read_action1.config(state=tk.NORMAL)
        button_action.config(state=tk.DISABLED)


def read_and_update_chart(
    data, client, chart1, chart2, address, stop_flag1, stop_flag2
):
    while not stop_flag1.is_set() or not stop_flag2.is_set():
        int_val, float_val = read_modbus_registers(client, 1, address)
        now = datetime.now()
        chart1.add_data_point(now, int_val)
        chart2.add_data_point(now, float_val)
        data.add_data(now, int_val, float_val)
        time.sleep(0.5)


def read():
    global data, chart1, chart2, thread1, entry_address1, stop_flag1, stop_flag2, read_action1
    read_action1.config(state=tk.DISABLED)
    stop_flag1 = threading.Event()
    stop_flag2 = threading.Event()
    chart1 = LiveTimeSeriesPlot(stop_flag1)
    chart2 = LiveTimeSeriesPlot(stop_flag2)
    thread1 = threading.Thread(
        target=read_and_update_chart,
        args=(
            data,
            client,
            chart1,
            chart2,
            int(entry_address1.get()),
            stop_flag1,
            stop_flag2,
        ),
    )
    thread1.start()
    chart1.show()
    chart2.show()


def close():
    global app, thread1, stop_flag1, stop_flag2
    stop_flag1.set()
    stop_flag2.set()
    if thread1 and thread1.is_alive():
        thread1.join()


def start_app():
    global app, data, chart1, chart2, client, status, button_action, port_entry, entry_address1, read_action1, stop_flag1, stop_flag2

    data = ModbusData()

    chart1 = None
    chart2 = None
    stop_flag1 = threading.Event()
    stop_flag2 = threading.Event()

    # Create the main application window
    app = tk.Tk()
    app.title("Sensor!")

    # Set the size of the main window
    app.geometry("400x300")  # Width x Height

    label_address1 = tk.Label(app, text="Data Address")
    label_address1.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
    entry_address1 = tk.Entry(app)
    entry_address1.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")
    entry_address1.insert(0, 0)

    port_text = tk.Label(app, text="Port")
    port_text.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
    port_entry = tk.Entry(app)
    port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="nswe")

    button_action = tk.Button(app, text="Connect", command=connect)
    button_action.grid(row=1, column=2, padx=5, pady=5, sticky="nswe")

    read_action1 = tk.Button(app, text="Read & Plot", command=read, state=tk.DISABLED)
    read_action1.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")

    # Create a readonly text widget
    status = tk.Text(app, font=("Arial", 12), wrap=tk.WORD, state=tk.DISABLED, height=8)
    status.insert(tk.END, "Click Connect to Start")
    app.columnconfigure(0, weight=2)
    status.grid(row=5, column=0, padx=5, pady=5, sticky="nswe")

    # Start the application's main event loop
    app.mainloop()
    close()


if __name__ == "__main__":
    start_app()
