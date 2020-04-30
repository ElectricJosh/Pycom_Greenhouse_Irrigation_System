import pycom
import os
from machine import SD
from machine import Timer
from machine import SPI
from machine import Pin
from machine import I2C
from _LCD import LCDBackend
from _RTC import RTCBackend

#from network import Bluetooth

# Initialise LED
pycom.heartbeat(False)
pycom.rgbled(0x0000ff)  # blue

# Pin and Com definitions
_SPI_Ref = SPI(0, mode=SPI.MASTER, baudrate=100000, polarity=0, phase=0, firstbit=SPI.MSB) # baud rate was 100000
_I2C_Ref = I2C(0, I2C.MASTER, baudrate=10000, pins=('P21','P20')) # SDA, SCL
_LCD_CS_Ref = Pin('P9', mode=Pin.OUT)
_Solenoid = Pin('P19', mode=Pin.OUT)

# Calling Constructors
_LCDScreen = LCDBackend(_SPI_Ref, _LCD_CS_Ref)
_Clock = RTCBackend(_I2C_Ref)
_BT_UART = UART(1, baudrate=9600, pins=('P7','P6')) # TX, RX

#_Clock.SetTime(0, 31, 15, 6, 25, 4, 20) # s,m,h,dow,d,m,y

# SD stuff
#sd = SD()
#os.mount(sd, '/sd')
#RootDir = "/sd/Greenhouse_Logs"
#try:  # there is no check directory member of uos module...
#    os.mkdir(RootDir)
#except:
#    print("Directory Exists")

#LCD Screen
def UpdateLCD(LineOne,LineTwo):
    _LCDScreen.ClearScreen()
    _LCDScreen.WriteLine1(LineOne)
    _LCDScreen.WriteLine2(str(LineTwo))

#Get Timestamp from RTC
def TimeStampString(): # returns a string of the time
    _TimeStamp = ""
    _TimeStamp += str(_Clock.ReadHour())
    _TimeStamp += ":"
    _TimeStamp += str(_Clock.ReadMinute())
    _TimeStamp += ":"
    _TimeStamp += str(_Clock.ReadSecond())
    return _TimeStamp

def DateStampString(): # returns a string of the time
    _TimeStamp = ""
    _TimeStamp += str(_Clock.ReadDate())
    _TimeStamp += ":"
    _TimeStamp += str(_Clock.ReadMonth())
    _TimeStamp += ":"
    _TimeStamp += str(_Clock.ReadYear())
    return _TimeStamp

#pycom.rgbled(0x0000ff)  # blue

Irrigation_Delay_Sec_On = 30 # watering time in seconds
Irrigation_Delay_Sec_Off = 43200 # wait time in seconds
Irrigation_Delay_Count = 0 # functions need to count down, not up
Solenoid_Status = False

# BLUETOOTH

#BLE_Obj = Bluetooth()
#BLE_Obj.set_advertisement(name='Greenhouse', service_uuid=b'1234567890123456')
#BLE_Obj.advertise(True) # Works perfectly, now to define the GATT service

#srv1 = BLE_Obj.service(uuid=b'1234567890123456', isprimary=True) # Pycom makes GATT super easy
#chr1 = srv1.characteristic(uuid=b'ab34567890123456', value=5)


# MAIN LOOP
while True:   
    # Solenoid State Machine
    if(Solenoid_Status == False): # off status 
        if(Irrigation_Delay_Count == 0):
            Solenoid_Status = True
            Irrigation_Delay_Count = Irrigation_Delay_Sec_On
        else:
            Irrigation_Delay_Count = Irrigation_Delay_Count - 1
    else:
        if(Irrigation_Delay_Count == 0):
            Solenoid_Status = False
            Irrigation_Delay_Count = Irrigation_Delay_Sec_Off
        else:
            Irrigation_Delay_Count = Irrigation_Delay_Count - 1

    # Status Control
    LCD_Status_String = ""
    if(Solenoid_Status == False): # off status 
        pycom.rgbled(0xff0000)  # red
        _Solenoid(True) # hardware buffer inverts logic
        LCD_Status_String = "(off)"
    else:
        pycom.rgbled(0x00ff00)  # green
        _Solenoid(False) # hardware buffer inverts logic
        LCD_Status_String = "(on)"

    # LCD Updater    
    Delay_Count_Hours, Remain = divmod(Irrigation_Delay_Count, 3600) # divide seconds into hours 60*60
    Delay_Count_Mins, Remain = divmod(Remain, 60) # devide remaining seconds into minutes
    UpdateLCD(TimeStampString()  + " " + LCD_Status_String, "Count: " + str(Delay_Count_Hours) + ":" + str(Delay_Count_Mins) + ":" + str(Remain))
    Timer.sleep_us(1000000) # One Second Delay



# TODO 

# https://docs.pycom.io/firmwareapi/pycom/machine/spi/
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/

# Everything is implemented for this article, I just need to have a play with the BLE functions for the next step
# The two references that will be required to setup a GATT server are here
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/gattsservice/
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/gattscharacteristic/
# The service is that actual advertisement and the characteristic is the data
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/#class-network-bluetooth-id-0
# See here for bluetooth object constructor
