from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

import struct

import logging

logger = logging.getLogger(__name__)

hex_string = "AB 01 04 03 20 00 00 00 00 00 00 3F 80 00 00 40 00 00 00 40 40 00 00 40 80 00 00 40 A0 00 00 40 C0 00 00 40 E0 00 00 41 00 00 00 41 10 00 00 41 20 00 00 41 30 00 00 41 40 00 00 41 50 00 00 41 60 00 00 41 70 00 00 41 80 00 00 41 88 00 00 41 90 00 00 41 98 00 00 41 A0 00 00 41 A8 00 00 41 B0 00 00 41 B8 00 00 41 C0 00 00 41 C8 00 00 41 D0 00 00 41 D8 00 00 41 E0 00 00 41 E8 00 00 41 F0 00 00 41 F8 00 00 42 00 00 00 42 04 00 00 42 08 00 00 42 0C 00 00 42 10 00 00 42 14 00 00 42 18 00 00 42 1C 00 00 42 20 00 00 42 24 00 00 42 28 00 00 42 2C 00 00 42 30 00 00 42 34 00 00 42 38 00 00 42 3C 00 00 42 40 00 00 42 44 00 00 42 48 00 00 42 4C 00 00 42 50 00 00 42 54 00 00 42 58 00 00 42 5C 00 00 42 60 00 00 42 64 00 00 42 68 00 00 42 6C 00 00 42 70 00 00 42 74 00 00 42 78 00 00 42 7C 00 00 42 80 00 00 42 82 00 00 42 84 00 00 42 86 00 00 42 88 00 00 42 8A 00 00 42 8C 00 00 42 8E 00 00 42 90 00 00 42 92 00 00 42 94 00 00 42 96 00 00 42 98 00 00 42 9A 00 00 42 9C 00 00 42 9E 00 00 42 A0 00 00 42 A2 00 00 42 A4 00 00 42 A6 00 00 42 A8 00 00 42 AA 00 00 42 AC 00 00 42 AE 00 00 42 B0 00 00 42 B2 00 00 42 B4 00 00 42 B6 00 00 42 B8 00 00 42 BA 00 00 42 BC 00 00 42 BE 00 00 42 C0 00 00 42 C2 00 00 42 C4 00 00 42 C6 00 00 42 C8 00 00 42 CA 00 00 42 CC 00 00 42 CE 00 00 42 D0 00 00 42 D2 00 00 42 D4 00 00 42 D6 00 00 42 D8 00 00 42 DA 00 00 42 DC 00 00 42 DE 00 00 42 E0 00 00 42 E2 00 00 42 E4 00 00 42 E6 00 00 42 E8 00 00 42 EA 00 00 42 EC 00 00 42 EE 00 00 42 F0 00 00 42 F2 00 00 42 F4 00 00 42 F6 00 00 42 F8 00 00 42 FA 00 00 42 FC 00 00 42 FE 00 00 43 00 00 00 43 01 00 00 43 02 00 00 43 03 00 00 43 04 00 00 43 05 00 00 43 06 00 00 43 07 00 00 43 08 00 00 43 09 00 00 43 0A 00 00 43 0B 00 00 43 0C 00 00 43 0D 00 00 43 0E 00 00 43 0F 00 00 43 10 00 00 43 11 00 00 43 12 00 00 43 13 00 00 43 14 00 00 43 15 00 00 43 16 00 00 43 17 00 00 43 18 00 00 43 19 00 00 43 1A 00 00 43 1B 00 00 43 1C 00 00 43 1D 00 00 43 1E 00 00 43 1F 00 00 43 20 00 00 43 21 00 00 43 22 00 00 43 23 00 00 43 24 00 00 43 25 00 00 43 26 00 00 43 27 00 00 43 28 00 00 43 29 00 00 43 2A 00 00 43 2B 00 00 43 2C 00 00 43 2D 00 00 43 2E 00 00 43 2F 00 00 43 30 00 00 43 31 00 00 43 32 00 00 43 33 00 00 43 34 00 00 43 35 00 00 43 36 00 00 43 37 00 00 43 38 00 00 43 39 00 00 43 3A 00 00 43 3B 00 00 43 3C 00 00 43 3D 00 00 43 3E 00 00 43 3F 00 00 43 40 00 00 43 41 00 00 43 42 00 00 43 43 00 00 43 44 00 00 43 45 00 00 43 46 00 00 43 47 00 00 07 6B"

hex_string = "00003F80"

byte_array = bytes.fromhex(hex_string.replace(" ", ""))

num1 = int.from_bytes(byte_array[0:2])
num2 = int.from_bytes(byte_array[2:4])

logger.info(len(byte_array))

logger.info(byte_array)

logger.info("".join(format(byte, "02x") for byte in list(byte_array)))

logger.info(struct.unpack("!f", byte_array)[0])
decoder = BinaryPayloadDecoder.fromRegisters(
    [num1, num2],
    byteorder=Endian.Big,
    wordorder=Endian.Little,
)

logger.info(decoder.decode_32bit_float())

import tkinter as tk


class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.width = 50
        self.height = 30
        self.state = False  # False: Off, True: On

        self.create_oval(2, 2, self.width - 2, self.height - 2, fill="gray")
        self.thumb = self.create_oval(
            2, 2, self.width // 2, self.height - 2, fill="white"
        )
        self.bind("<Button-1>", self.toggle)

    def toggle(self, event):
        self.state = not self.state
        self.move(self.thumb, self.width // 2, 0) if self.state else self.move(
            self.thumb, -self.width // 2, 0
        )


def main():
    root = tk.Tk()
    root.title("Toggle Switch Example")

    toggle_switch = ToggleSwitch(root, width=50, height=30)
    toggle_switch.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
