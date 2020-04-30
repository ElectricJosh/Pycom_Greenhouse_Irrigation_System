from _LCD_MCP23S17 import MCP23S17Backend
from machine import Timer

# clock is on bit 0
# RS is on bit 1

class LCDBackend:

    MCP23S17Ref = 0

    def __init__(self, LCD_SPI_Object, LCD_SPI_CS):
        self.MCP23S17Ref = MCP23S17Backend(LCD_SPI_Object, LCD_SPI_CS)
        Timer.sleep_us(50000)
        self.InitFunctionSet()
        Timer.sleep_us(4500)
        self.InitFunctionSet()
        Timer.sleep_us(200)
        self.InitFunctionSet()
        # now set the properties you want
        self.FunctionSet()
        self.DisplayOnOff()
        self.ClearScreen()
        self.EntryModeSet()

    # INITIALISING FUNCTIONS

    def InitFunctionSet(self): # D7 -> 00110000 <- D0 (0x30)
        self.MCP23S17Ref.WritePortA(0x30)
        self.ClockIn(0)

    def FunctionSet(self): # D7 -> 00111000 <- D0 (0x38)
        self.MCP23S17Ref.WritePortA(0x38)
        self.ClockIn(0)

    def DisplayOnOff(self): # D7 -> 00001100 <- D0 (0x0C) No cursor, no blink, display on
        self.MCP23S17Ref.WritePortA(0x0C) # no cursor blink
        #self.MCP23S17Ref.WritePortA(0x0F) # cursor blink
        self.ClockIn(0)

    def ClearScreen(self): # D7 -> 00000001 <- D0 (0x01)
        self.MCP23S17Ref.WritePortA(0x01)
        self.ClockIn(0)
        Timer.sleep_us(2000)

    def EntryModeSet(self): # D7 -> 00000110 <- D0 (0x06)
        self.MCP23S17Ref.WritePortA(0x06)
        self.ClockIn(0)

    def ClockIn(self, RS_State): # RS_State is either 1 or 0
        RS_State = RS_State << 1 # RS is on bit 1
        ClkOff = 0x00 # clock is on bit 0
        ClkOn = 0x01
        self.MCP23S17Ref.WritePortB(ClkOff | RS_State)
        Timer.sleep_us(1)
        self.MCP23S17Ref.WritePortB(ClkOn | RS_State)
        Timer.sleep_us(1)
        self.MCP23S17Ref.WritePortB(ClkOff | RS_State)
        Timer.sleep_us(100)

    def WriteLine1(self, TextString): # parse 's' as an argument
        self.MCP23S17Ref.WritePortA(0x80)
        self.ClockIn(0)

        b = bytearray(TextString, 'utf-8') # does str.encode as part of the function

        for x in range(0, len(b)): # writes a char at a time
            self.MCP23S17Ref.WritePortA(b[x])
            self.ClockIn(1)

    def WriteLine2(self, TextString): # parse 's' as an argument
        self.MCP23S17Ref.WritePortA(0xC0)
        self.ClockIn(0)

        b = bytearray(TextString, 'utf-8') # does str.encode as part of the function

        for x in range(0, len(b)): # writes a char at a time
            self.MCP23S17Ref.WritePortA(b[x])
            self.ClockIn(1)