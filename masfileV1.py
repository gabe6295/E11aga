import adafruit_bme680
import time
import board
import numpy as np
import csv
import time
import numpy as np
import busio
import serial
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
from adafruit_pm25.uart import PM25_UART




# ~~~~~~~~~~~~~~~~ begin ri.py bme data ~~~~~~~~~~~~~~~~ # 

n = 0
# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()   # uses board.SCL and board.SDA
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1013.25

l = []

while n<5:
    print("\nTemperature: %0.1f C" % bme680.temperature)
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.relative_humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)
    t = time.time()
    r = time.localtime(t)
    s = time.strftime("%A, %B %d, %Y %I:%M:%S %p", r)
    print(s)

    n+=1
    time.sleep(1)
    l.append([bme680.temperature])
    l.append([bme680.gas])
    l.append([bme680.relative_humidity])
    l.append([bme680.pressure])
    l.append([bme680.altitude])
    l.append([t])
    

np.savetxt('databme.csv',l,delimiter=",",fmt='%s')
# ~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~ # 


# ~~~~~~~~~~~~~~~~ begin rpA1.py ~~~~~~~~~~~~~~~~ # 

reset_pin = None
# If you have a GPIO, its not a bad idea to connect it to the RESET pin
# reset_pin = DigitalInOut(board.G0)
# reset_pin.direction = Direction.OUTPUT
# reset_pin.value = False


# For use with a computer running Windows:
# import serial
# uart = serial.Serial("COM30", baudrate=9600, timeout=1)

# For use with microcontroller board:
# (Connect the sensor TX pin to the board/computer RX pin)
# uart = busio.UART(board.TX, board.RX, baudrate=9600)

# For use with Raspberry Pi/Linux:
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)

# For use with USB-to-serial cable:
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.25)

# Connect to a PM2.5 sensor over UART
pm25 = PM25_UART(uart, reset_pin)

# Create library object, use 'slow' 100KHz frequency!
# i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
# Connect to a PM2.5 sensor over I2C
# pm25 = PM25_I2C(i2c, reset_pin)

print("Found PM2.5 sensor, reading data...")

timerun = 0 
timep = 2
timemax = int(input("How long would you like to run? "))
target_key = 'pm25 env'
pm25dict = pm25.read()
metastoredata = {key:value for key, value in pm25dict.items() if key == target_key}
meta = [time.time(),metastoredata]



while timerun<timemax:
    time.sleep(timep)
    
    
    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue

    print()
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    )
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    )
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    print("---------------------------------------")
    timestamp = time.time()
    timeread = time.strftime("%A, %B %d, %Y %I:%M:%S %p", time.localtime(timestamp))
    print(timeread)
    
    timerun += timep



file = open('rpA1.csv', 'w', newline= None)
csvwriter = csv.writer(file, delimiter=',')
    
csvwriter.writerow(meta) 
    
for i in range(0,timemax,timep):
    now = time.time()
    value = aqdata["pm25 env"]
    csvwriter.writerow([now,value]) #make into a list
    
file.close() #close file
quit()
#~~~~~~~~~~~ end ~~~~~~~~~#