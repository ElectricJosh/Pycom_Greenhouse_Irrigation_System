import pycom
import os
from machine import SD
from machine import Timer
from machine import SPI
from machine import Pin
from machine import I2C
from _LCD import LCDBackend
from _RTC import RTCBackend

from network import Bluetooth

# Timing variables
Irrigation_Delay_Sec_On = 30 # watering time in seconds
Irrigation_Delay_Sec_Off = 43200 # wait time in seconds
Irrigation_Delay_Count = 0 # functions need to count down, not up
Solenoid_Status = False

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
sd = SD()
os.mount(sd, '/sd')
RootDir = '/sd/Greenhouse_Meta'
FileName = RootDir + '/config.txt'

try: 
    os.mkdir(RootDir) # make directory if it does not exist
except:
    print("Directory Exists")

f = open(FileName, 'a') # generate file if it does not exist using write mode
f.close()

f = open(FileName, 'r') # open in read mode
config_timings = f.read()
f.close()
if(config_timings != ''):
    # load saved values otherwise use default values
    print('loading saved values')
    delimit = config_timings.split('_') # split string with delimiter
    Irrigation_Delay_Sec_On = int(delimit[0])
    Irrigation_Delay_Sec_Off = int(delimit[1])

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

# BLUETOOTH
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/gattsservice/
# https://docs.pycom.io/firmwareapi/pycom/network/bluetooth/gattscharacteristic/

# https://play.google.com/store/apps/details?id=com.macdom.ble.blescanner&hl=en_GB
# Uses the "BLE scanner" app on Android
# write using the text option
def Delay_On_BLE_Callback(BLE_Type, Char_Value):
    print("on delay write event")
    
    global Irrigation_Delay_Sec_On
    Irrigation_Delay_Sec_On = int(chr1.value()) # watering time in seconds
    global Irrigation_Delay_Count
    Irrigation_Delay_Count = 0
    global Solenoid_Status
    Solenoid_Status = True

    f = open(FileName, 'w') # overwrite data    
    f.write(str(Irrigation_Delay_Sec_On))
    f.write('_')
    f.write(str(Irrigation_Delay_Sec_Off))
    f.close()

def Delay_Off_BLE_Callback(BLE_Type, Char_Value):
    print("off delay write event")

    global Irrigation_Delay_Sec_Off
    Irrigation_Delay_Sec_Off = int(chr2.value()) # watering time in seconds
    global Irrigation_Delay_Count
    Irrigation_Delay_Count = 0
    global Solenoid_Status
    Solenoid_Status = True

    f = open(FileName, 'w') # overwrite data
    f.write(str(Irrigation_Delay_Sec_On) + "_" + str(Irrigation_Delay_Sec_Off))
    f.close()

# Setup BLE advertisement
BLE_Obj = Bluetooth()
BLE_Obj.set_advertisement(name='Greenhouse', service_uuid=b'1234567890123456')
BLE_Obj.advertise(True)

#define BLE GATT servcies and charateristics
srv1 = BLE_Obj.service(uuid= 0x100, isprimary=True) # define two services because Pycom does not support multiple characteristics
srv2 = BLE_Obj.service(uuid= 0x200, isprimary=True) # frontend code and documentation is incomplete
chr1 = srv1.characteristic(uuid= 0x101, value= Irrigation_Delay_Sec_On)
chr2 = srv2.characteristic(uuid= 0x201, value= Irrigation_Delay_Sec_Off)

# Define callbacks for BLE events
chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=Delay_On_BLE_Callback)
chr2.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=Delay_Off_BLE_Callback)



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