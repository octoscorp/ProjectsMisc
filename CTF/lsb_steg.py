"""
Basic LSB steg tool for CTFs.

Author: G Hampton
Date: 21/03/2025

TODO: Extract conversion functionality into its own class

"""
from PIL import Image
from base64 import b64encode


class LSB_Steganographer():
    def __init__(self):
        print("=== LSB Steganography tool ===")
        img = Image.open(input('Image:  '))
        self.pixels = img.load()

        file_size = input('Size (ROWxCOL):  ')
        self.rows, self.cols = file_size.split('x')

        step = input("Step size [1]:  ")
        self.step = int(step) if step != "" else 1
        channels = input("Channels to inspect [3]:  ")
        self.channels = int(channels) if channels != "" else 3

        print("-" * 15)

        self.binary = ""
        self.hex = ""
        self.ascii = ""

    def read_lsb(self):
        # TODO: rework this so step size can wrap around row ends
        print("Processing image, this may take a while")
        self.bit_array = ""
        for row in range(int(self.rows)):
            for col in range(0, int(self.cols), self.step):
                for i in range(self.channels):
                    byte_val = format((self.pixels[row, col][i]), "b")
                    self.bit_array += str(byte_val)[-1]
        print("Processing complete\n")

    def show_binary(self):
        print("--- In binary:")
        self.binary = ""
        counter = 0
        while counter < len(self.bit_array):
            self.binary += self.bit_array[counter]
            counter += 1
        print(f"{self.binary}")
        # Additional format:
        for i in range(len(self.binary)):
            spacer = ''
            if i % 8 == 7:
                spacer = ' '
            print(self.binary[i], end=spacer)
        print("\n")

    def _get_next_byte(self, start):
        """Returned in string format of course"""
        byte = ""
        bits = 8
        if start + bits > len(self.bit_array):
            print("\nLast byte ran out of bits. Zero-padding from MSB gives:  ", end="")
            bits = len(self.bit_array) - start
            for i in range(8-bits):
                byte += "0"
        for i in range(bits):
            byte += self.bit_array[start + i]
        return byte

    def show_hex(self):
        print("--- In hex:")
        self.hex = ""
        counter = 0
        while counter < len(self.bit_array):
            byte = self._get_next_byte(counter)
            self.hex += format(int(byte, 2), 'x')
            counter += 8
        print(f"{self.hex}\n")

    def show_ascii(self):
        print("--- In ASCII:")
        self.ascii = ""
        counter = 0
        while counter < len(self.bit_array):
            byte = self._get_next_byte(counter)
            self.ascii += chr(int(byte, 2))
            counter += 8
        print(f"{self.ascii}\n")

    def show_base64(self):
        print("--- In base64:")
        self.base_64 = b64encode(self.binary.encode())
        print(f"{self.base_64}\n")

    def show_all(self):
        self.show_binary()
        self.show_hex()
        self.show_ascii()
        self.show_base64()


if __name__ == "__main__":
    steg = LSB_Steganographer()
    steg.read_lsb()
    steg.show_all()
