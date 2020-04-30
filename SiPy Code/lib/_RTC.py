from machine import I2C

class RTCBackend:

    # Slave Address
    DS1307_ADDRESS = 0x68
    # Register Address
    SecondsAddress = 0x00
    MinutesAddress = 0x01
    HoursAddress = 0x02
    DaysAddress = 0x03
    DateAddress = 0x04
    MonthAddress = 0x05
    YearAddress = 0x06
    ControlAddress = 0x07

    RTC_Comm = 0

    def __init__(self, I2C_Instance):
        self.RTC_Comm = I2C_Instance

    def SetTime(self, Sec, Mins, Hours, Days, Date, Month, Year):
        self.WriteSecond(Sec)
        self.WriteMinute(Mins)
        self.WriteHour(Hours)
        self.WriteDay(Days)
        self.WriteDate(Date)
        self.WriteMonth(Month)
        self.WriteYear(Year)

    # Read Subroutines

    def ReadSecond(self): 
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.SecondsAddress, 1)
        Temp = I2CBuffer[0]
        Temp = Temp & 0x7F # Mask
        Units = Temp & 0x0F
        Tens = ((Temp & 0x70)>>4) * 10
        Temp = Units + Tens
        return Temp

    def ReadMinute(self):
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.MinutesAddress, 1)
        Temp = I2CBuffer[0]
        Temp = Temp & 0x7F # Mask
        Units = Temp & 0x0F
        Tens = ((Temp & 0x70)>>4) * 10
        Temp = Units + Tens
        return Temp

    def ReadHour(self):
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.HoursAddress, 1)
        Temp = I2CBuffer[0]
        Temp = Temp & 0x3F # Mask
        Units = Temp & 0x0F
        Tens = ((Temp & 0x30)>>4) * 10
        Temp = Units + Tens
        return Temp

    def ReadDay(self):
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.DaysAddress, 1)
        Temp = I2CBuffer[0]
        Temp = Temp & 0x07 # Mask
        return Temp

    def ReadDate(self):
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.DateAddress, 1)
        Temp = I2CBuffer[0]
        Temp = Temp & 0x3F # Mask
        Units = Temp & 0x0F
        Tens = ((Temp & 0x30)>>4) * 10
        Temp = Units + Tens
        return Temp

    def ReadMonth(self):
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.MonthAddress, 1)
        Temp = I2CBuffer[0]
        Temp = Temp & 0x1F # Mask
        Units = Temp & 0x0F
        Tens = ((Temp & 0x10)>>4) * 10
        Temp = Units + Tens
        return Temp

    def ReadYear(self):
        I2CBuffer = self.RTC_Comm.readfrom_mem(self.DS1307_ADDRESS, self.YearAddress, 1)
        Temp = I2CBuffer[0]
        Units = Temp & 0x0F
        Tens = ((Temp & 0xF0)>>4) * 10
        Temp = Units + Tens
        return Temp

    # Write Subroutines

    def WriteSecond(self, Secs):
        Tens = Secs // 10 # floored division
        Units = Secs % 10 # remainder
        Units &= 0x0F
        Tens &= 0x07
        Tens = Tens<<4
        Final = Tens|Units
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.SecondsAddress, Final)

    def WriteMinute(self, Mins):
        Tens = Mins // 10 # floored division
        Units = Mins % 10 # remainder
        Units &= 0x0F
        Tens &= 0x07
        Tens = Tens<<4
        Final = Tens|Units
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.MinutesAddress, Final)

    def WriteHour(self, Hours):
        Tens = Hours // 10 # floored division
        Units = Hours % 10 # remainder
        Units &= 0x0F
        Tens &= 0x03
        Tens = Tens<<4
        Final = Tens|Units
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.HoursAddress, Final)

    def WriteDay(self, Days):
        Days &= 0x07
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.DaysAddress, Days)

    def WriteDate(self, Date):
        Tens = Date // 10 # floored division
        Units = Date % 10 # remainder
        Units &= 0x0F
        Tens &= 0x03
        Tens = Tens<<4
        Final = Tens|Units
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.DateAddress, Final)

    def WriteMonth(self, Month):
        Tens = Month // 10 # floored division
        Units = Month % 10 # remainder
        Units &= 0x0F
        Tens &= 0x01
        Tens = Tens<<4
        Final = Tens|Units
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.MonthAddress, Final)

    def WriteYear(self, Year):
        Tens = Year // 10 # floored division
        Units = Year % 10 # remainder
        Units &= 0x0F
        Tens &= 0x0F
        Tens = Tens<<4
        Final = Tens|Units
        self.RTC_Comm.writeto_mem(self.DS1307_ADDRESS, self.YearAddress, Final)