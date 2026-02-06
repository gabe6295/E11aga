import adafruit_bme680
import time
import board
import numpy as np

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
quit
