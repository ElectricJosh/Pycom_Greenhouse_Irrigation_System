from machine import SPI
from machine import Pin

class MCP23S17Backend:

    ChipAddress = 0x40

    SPI_Comm = 0
    SPI_CS = 0

    IODIRA = 0x00
    IODIRB = 0x01
    IPOLA = 0x02
    IPOLB = 0x03
    GPINTENA = 0x04
    GPINTENB = 0x05
    DEFVALA = 0x06
    DEFVALB = 0x07
    INTCONA = 0x08
    INTCONB = 0x09
    IOCONA = 0x0A
    IOCONB = 0x0B
    GPPUA = 0x0C
    GPPUB = 0x0D
    GPIOA = 0x12
    GPIOB = 0x13

    def __init__(self, MCP23S17_SPI_Object, MCP23S17_CS_Object):
        self.SPI_Comm = MCP23S17_SPI_Object
        self.SPI_CS = MCP23S17_CS_Object
        self.SPI_CS(True) # Chip disabled, active low

        self.Write(self.IOCONA, 0x28)

        self.Write(self.IODIRA, 0x00)
        self.Write(self.IODIRB, 0x00)

        self.Write(self.IPOLA, 0x00)
        self.Write(self.IPOLB, 0x00)

        self.Write(self.GPINTENA, 0x00)
        self.Write(self.GPINTENB, 0x00)

        self.Write(self.DEFVALA, 0x00)
        self.Write(self.DEFVALB, 0x00)

        self.Write(self.INTCONA, 0x00)
        self.Write(self.INTCONB, 0x00)

        self.Write(self.GPPUA, 0x00)
        self.Write(self.GPPUB, 0x00)

        # Initialise Outputs

        self.Write(self.GPIOA, 0x00)
        self.Write(self.GPIOB, 0x00)

    def Write(self, Reg, Data):
        self.SPI_CS(False) # Active Low
        self.SPI_Comm.write(bytes([self.ChipAddress, Reg, Data]))
        self.SPI_CS(True)

    def Read(self, Reg):
        self.SPI_CS(True)
        self.SPI_CS(False) # Active Low
        read_buf = bytearray(3)
        ReadAddress = (self.ChipAddress + 0x01) # the read address has a read bit that needs to be enabled
        self.SPI_Comm.write_readinto(bytes([ReadAddress, Reg, 0xFF]), read_buf) # Redundant data is needed to clock out the register
        self.SPI_CS(True)
        return read_buf[2]

    def WritePortA(self, value):
        value = self.BitOrderPatch(value)
        self.Write(self.GPIOA, value)

    def WritePortB(self, value):
        self.Write(self.GPIOB, value)

    def ReadPortB(self):
        return self.Read(self.GPIOB)

    def ReadPortA(self):
        return self.BitOrderPatch(self.Read(self.GPIOA))


    def BitOrderPatch(self, value):
        temp = 0
        temp |= ((0x01 & value)<<7)
        temp |= ((0x02 & value)<<5)
        temp |= ((0x04 & value)<<3)
        temp |= ((0x08 & value)<<1)
        temp |= ((0x10 & value)>>1)
        temp |= ((0x20 & value)>>3)
        temp |= ((0x40 & value)>>5)
        temp |= ((0x80 & value)>>7)
        temp &= 0xFF
        return temp