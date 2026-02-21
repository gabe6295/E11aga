import adafruit_bme680
import time
import board
import csv
import serial
import sys
from adafruit_pm25.uart import PM25_UART

arguments = sys.argv
data_path = './' + arguments[1]
timemax = int(arguments[2])
file = open(data_path,'w', newline = None)

timerun = 0 
timep = 2

#BME680
i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
bme680.sea_level_pressure = 1013.25

# PM2.5 setup
# (UART)
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
pm25 = PM25_UART(uart, None)

print("Found PM2.5 sensor, reading data...")

# Open CSV
with file as file:
    csvwriter = csv.writer(file, delimiter=',')
    # header row
    csvwriter.writerow(["Timestamp", "Temp", "Gas", "Humidity", "Pressure", "PM25_Env"])

    while timerun < timemax:
        try:
            # Read Particle Data FIRST
            aqdata = pm25.read()
            
            # Print PM2.5
            print("\nConcentration Units (standard)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % 
                  (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"]))
            
            print("Concentration Units (environmental)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % 
                  (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"]))
            
            # Print BME680
            print("---------------------------------------")
            print("Temperature: %0.1f C" % bme680.temperature)
            print("Gas: %d ohm" % bme680.gas)
            print("Humidity: %0.1f %%" % bme680.relative_humidity)
            print("Pressure: %0.3f hPa" % bme680.pressure)
            
            t_now = time.time()
            s_now = time.strftime("%A, %B %d, %Y %I:%M:%S %p", time.localtime(t_now))
            print(s_now)

            # Save to CSV !!inside the loop!!
            #
            csvwriter.writerow([t_now, bme680.temperature, bme680.gas, 
                                bme680.relative_humidity, bme680.pressure, aqdata["pm25 env"]])
            file.flush() #DO NOT REMOVE THIS IT FORCE WRITES TO PRESERVE THE DATA

        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue

        time.sleep(timep)
        timerun += timep
print("Run complete.")
#comment
