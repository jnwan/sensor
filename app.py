from connect import scan_ports_and_connect, connect_port
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import tkinter as tk
import threading
import time
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from chart import LiveTimeSeriesPlot

stop_flag = threading.Event()


def read_modbus_registers(
    modbus_client: ModbusClient, slave_id, starting_address, num_registers, num_type
):
    try:
        modbus_client.connect()
        # Read holding registers from the Modbus RTU device
        response = modbus_client.read_holding_registers(
            starting_address, num_registers, unit=slave_id
        )
        if response.isError():
            print(f"Error reading Modbus registers: {response}")
        else:
            decoder = BinaryPayloadDecoder.fromRegisters(
                response.registers, byteorder=Endian.Big, wordorder=Endian.Little
            )
            data = []
            if num_type == "int":
                data = [decoder.decode_32bit_uint()]
            elif num_type == "float":
                data = [decoder.decode_32bit_float()]
            print(
                f"Data from Modbus device (Slave {slave_id}), starting address {starting_address}: {response.registers}, decoded value: {data}"
            )
            return data
    except Exception as e:
        print(f"Error: {e}")
    return []


def connect():
    global client, read_action1, read_action2, button_action, port_entry, thread1, thread2
    thread1 = None
    thread2 = None
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
        read_action2.config(state=tk.NORMAL)
        button_action.config(state=tk.DISABLED)


def read_and_update_chart(chart, starting_address, num_registers, num_type):
    global client
    while not stop_flag.is_set():
        data = read_modbus_registers(
            client, 1, int(starting_address), int(num_registers), num_type
        )
        for num in data:
            chart.add_data_point(num)
        time.sleep(1)


def validate_type(num_type):
    allowed = num_type == "int" or num_type == "float"
    if not allowed:
        print("Only int and float types are supported!")
    return allowed


def read1():
    global chart1, thread1, entry_address1, entry_len_address1, entry_type_address1
    if not validate_type(entry_type_address1.get()):
        return
    chart1 = LiveTimeSeriesPlot()
    thread1 = threading.Thread(
        target=read_and_update_chart,
        args=(
            chart1,
            entry_address1.get(),
            entry_len_address1.get(),
            entry_type_address1.get(),
        ),
    )

    thread1.start()

    chart1.show()


def read2():
    global chart2, thread2, entry_address2, entry_len_address2, entry_type_address2
    if not validate_type(entry_type_address2.get()):
        return
    chart2 = LiveTimeSeriesPlot()
    thread2 = threading.Thread(
        target=read_and_update_chart,
        args=(
            chart2,
            entry_address2.get(),
            entry_len_address2.get(),
            entry_type_address2.get(),
        ),
    )
    thread2.start()
    chart2.show()


def close():
    global thread1, thread2
    stop_flag.set()
    if thread1 and thread1.is_alive():
        thread1.join()

    if thread2 and thread2.is_alive():
        thread2.join()


def start_app():
    global app, client, status, button_action, port_entry, entry_address1, entry_len_address1, entry_type_address1, entry_address2, entry_len_address2, entry_type_address2, read_action1, read_action2

    # Create the main application window
    app = tk.Tk()
    app.title("Sensor!")

    # Set the size of the main window
    app.geometry("600x400")  # Width x Height

    label_address1 = tk.Label(app, text="Address 1:")
    label_address1.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
    entry_address1 = tk.Entry(app)
    entry_address1.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
    entry_address1.insert(0, 0)

    len_address1 = tk.Label(app, text="Count 1:")
    len_address1.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")
    entry_len_address1 = tk.Entry(app)
    entry_len_address1.grid(row=1, column=1, padx=5, pady=5, sticky="nswe")
    entry_len_address1.insert(0, 2)
    entry_len_address1.config(state=tk.DISABLED)

    type_address1 = tk.Label(app, text="Type 1:")
    type_address1.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")
    entry_type_address1 = tk.Entry(app)
    entry_type_address1.grid(row=1, column=2, padx=5, pady=5, sticky="nswe")
    entry_type_address1.insert(0, "int")

    label_address2 = tk.Label(app, text="Address 2:")
    label_address2.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
    entry_address2 = tk.Entry(app)
    entry_address2.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")
    entry_address2.insert(0, 1)

    len_address2 = tk.Label(app, text="Count 2:")
    len_address2.grid(row=2, column=1, padx=5, pady=5, sticky="nswe")
    entry_len_address2 = tk.Entry(app)
    entry_len_address2.grid(row=3, column=1, padx=5, pady=5, sticky="nswe")
    entry_len_address2.insert(0, 2)
    entry_len_address2.config(state=tk.DISABLED)

    type_address2 = tk.Label(app, text="Type 2:")
    type_address2.grid(row=2, column=2, padx=5, pady=5, sticky="nswe")
    entry_type_address2 = tk.Entry(app)
    entry_type_address2.grid(row=3, column=2, padx=5, pady=5, sticky="nswe")
    entry_type_address2.insert(0, "float")

    port_text = tk.Label(app, text="Port: ")
    port_text.grid(row=4, column=0, padx=5, pady=5, sticky="nswe")
    port_entry = tk.Entry(app)
    port_entry.grid(row=4, column=1, padx=5, pady=5, sticky="nswe")

    button_action = tk.Button(app, text="Connect", command=connect)
    button_action.grid(row=4, column=2, padx=5, pady=5, sticky="nswe")

    read_action1 = tk.Button(app, text="Read & Plot", command=read1, state=tk.DISABLED)
    read_action1.grid(row=1, column=3, padx=5, pady=5, sticky="nswe")

    read_action2 = tk.Button(app, text="Read & Plot", command=read2, state=tk.DISABLED)
    read_action2.grid(row=3, column=3, padx=5, pady=5, sticky="nswe")

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
