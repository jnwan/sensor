from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from config import ConfigSingleton
import serial
import random
import crcmod
import numpy as np

from enum import Enum

import logging

logger = logging.getLogger(__name__)

SLAVE_ID = ConfigSingleton().get_config()["SLAVE_ID"]
DISABLE_CRC = ConfigSingleton().get_config()["DISABLE_CRC"]


class DataType(Enum):
    UINT16 = 1
    UINT32 = 2
    FLOAT32 = 3


def decode_data(data, data_type: DataType):
    decoder = BinaryPayloadDecoder.fromRegisters(
        data, byteorder=Endian.Big, wordorder=Endian.Little
    )
    if data_type == DataType.UINT16:
        assert len(data) == 1
        return decoder.decode_16bit_uint()
    elif data_type == DataType.UINT32:
        assert len(data) == 2
        return decoder.decode_32bit_uint()
    elif data_type == DataType.FLOAT32:
        assert len(data) == 2
        return decoder.decode_32bit_float()
    else:
        raise TypeError(f"DataType {data_type} not supported!")


def read_modbus(
    modbus_client: ModbusClient,
    address,
    data_type: DataType,
):
    try:
        modbus_client.connect()
        if data_type == DataType.UINT16:
            response = modbus_client.read_holding_registers(address, 1, unit=SLAVE_ID)
        elif data_type == DataType.UINT32:
            response = modbus_client.read_holding_registers(address, 2, unit=SLAVE_ID)
        elif data_type == DataType.FLOAT32:
            response = modbus_client.read_holding_registers(address, 2, unit=SLAVE_ID)
        else:
            raise TypeError(f"DataType {data_type} not supported!")

        if response.isError():
            logger.error(f"Error reading Modbus registers: {response}")
        else:
            data = decode_data(response.registers, data_type)
            logger.info(
                f"Data from Modbus device (Slave {SLAVE_ID}), "
                f"starting address {address}: {response.registers}, "
                f"Decoded value: {data}"
            )
            return data
    except Exception as e:
        logger.error(f"Error: {e}")
    return []


def write_modbus(
    modbus_client: ModbusClient,
    address,
    value,
):
    try:
        modbus_client.connect()
        response = modbus_client.write_register(address, value, unit=SLAVE_ID)
        logger.info(
            f"Write {value} to addres {address} on unit {SLAVE_ID} response: {response}"
        )
    except Exception as e:
        logger.error(f"Error: {e}")


def calculate_crc(data, polynomial=0x8005):
    # Create a CRC calculator with the specified CRC width and polynomial
    crc_func = crcmod.mkCrcFun(polynomial, initCrc=0, rev=True, xorOut=0xFFFFFFFF)

    # Calculate the CRC value for the input data
    crc = crc_func(data)

    # Return the calculated CRC value
    return crc


def validate_crc(data, provided_crc, polynomial=0x8005):
    # Calculate the CRC value for the input data
    calculated_crc = calculate_crc(data, polynomial)

    # Compare the calculated CRC value with the provided CRC value
    return calculated_crc == provided_crc


CUSTOM_PROTOCO_ADDITIONAL_BYTE_COUNT = ConfigSingleton().get_config()[
    "CUSTOM_PROTOCO_ADDITIONAL_BYTE_COUNT"
]
CUSTOM_PROTOCO_DATA_BYTE_COUNT = ConfigSingleton().get_config()[
    "CUSTOM_PROTOCO_DATA_BYTE_COUNT"
]
FAKE_CUSTOM_DATA = ConfigSingleton().get_config()["FAKE_CUSTOM_DATA"]


def get_fake_data():
    t = np.arange(0, 200)  # 时间序列
    f1 = 5  # 低频信号频率
    f2 = 50  # 高频信号频率
    signal = (
        np.sin(2 * np.pi * f1 * t)
        + 0.5 * np.sin(2 * np.pi * f2 * t)
        + np.random.normal(0, 0.5, len(t))
    )
    return signal


def read_custom_data(device: serial.Serial, command, data_type: DataType):
    if FAKE_CUSTOM_DATA:
        return get_fake_data()
    try:
        device.write(bytes.fromhex(command))  # Send the command as bytes
    except Exception as e:
        logger.error(f"Error: Failed to send command to the device: {e}")
        return None

    # Read data from the device (assuming the data follows the custom protocol)
    try:
        total_count = (
            CUSTOM_PROTOCO_DATA_BYTE_COUNT + CUSTOM_PROTOCO_ADDITIONAL_BYTE_COUNT
        )
        byte_array = bytearray()
        byte_array.extend(device.read(total_count))
        assert len(byte_array) == total_count
        provided_crc = byte_array[total_count - 2] << 8 | byte_array[total_count - 1]
        if not DISABLE_CRC and not validate_crc(
            byte_array[: (total_count - 2)], provided_crc
        ):
            logger.error("CRC validation failed")
            return None

        # logger.info("*************************************************")
        # logger.info("".join(format(byte, "02x") for byte in byte_array))
        # logger.info("*************************************************")
        data_byte = byte_array[5 : (5 + CUSTOM_PROTOCO_DATA_BYTE_COUNT)]
        num_16bit_list = []
        for i in range(0, len(data_byte), 2):
            num = (data_byte[i] << 8) | data_byte[i + 1]
            num_16bit_list.append(num)
        decoder = BinaryPayloadDecoder.fromRegisters(
            num_16bit_list,
            byteorder=Endian.Big,
            wordorder=Endian.Little,
        )
        result = []
        for i in range(0, CUSTOM_PROTOCO_DATA_BYTE_COUNT, 4):
            if data_type == DataType.UINT32:
                result.append(decoder.decode_32bit_uint())
            elif data_type == DataType.FLOAT32:
                result.append(decoder.decode_32bit_float())

        return result
    except Exception as e:
        logger.error(f"Error: Failed to read data from the device: {e}")
        return None
