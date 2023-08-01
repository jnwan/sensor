import serial
import time
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

BAUDRATE = 921600


def connect_port(port_name, baudrate=BAUDRATE, timeout=5):
    try:
        # Try to open the serial port
        ser = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
        time.sleep(0.1)  # Wait for a short time to ensure proper initialization

        # Try to create a Modbus RTU client for the port
        modbus_client = ModbusClient(
            method="rtu",
            port=ser.port,
            stopbits=1,
            bytesize=8,
            parity="N",
            baudrate=baudrate,
            timeout=timeout,
        )
        modbus_client.connect()
        print(f"Successfully connect to {ser.port}")
        return modbus_client

    except (OSError, serial.SerialException):
        # If there's an error opening the port or creating the client, ignore and move to the next port
        print(f"Exception connecting to {port_name}")
        return None


def scan_ports_and_connect(baudrate=BAUDRATE, timeout=5):
    # List of common Modbus RTU port names to scan
    port_names = [
        "COM{}".format(i) for i in range(1, 17)
    ]  # Assuming up to 16 COM ports, adjust as needed for your system

    modbus_clients = []

    for port_name in port_names:
        client = connect_port(port_name, baudrate, timeout)
        if client:
            modbus_clients.append(client)
    return modbus_clients


if __name__ == "__main__":
    modbus_clients = scan_ports_and_connect()

    if not modbus_clients:
        print("No Modbus RTU devices found.")
    else:
        print(f"Found {len(modbus_clients)} Modbus RTU device(s):")
        for index, client in enumerate(modbus_clients, start=1):
            print(f"Device {index}: {client}")

            # Now you can use the client to interact with the Modbus RTU device.
            # For example, you can read/write holding registers, input registers, etc.
