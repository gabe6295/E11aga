import adafruit_bme680
import time
import board
import csv
import serial
from adafruit_pm25.uart import PM25_UART

# --- User Input & Logic ---
timemax = int(input("How long would you like to run? "))
timerun = 0 
timep = 2

# --- BME680 Setup --- 
i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
bme680.sea_level_pressure = 1013.25

# --- PM2.5 Setup --- 
# Using Raspberry Pi hardware serial port
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
pm25 = PM25_UART(uart, None)

print("Found PM2.5 sensor, reading data...")

# Open CSV for writing *before* the loop
with open('rpA1.csv', 'w', newline='') as file:
    csvwriter = csv.writer(file, delimiter=',')
    # Optional: Add a header row so you know what the columns are
    csvwriter.writerow(["Timestamp", "Temp", "Gas", "Humidity", "Pressure", "PM25_Env"])

    while timerun < timemax:
        try:
            # 1. Read Particle Data FIRST so aqdata exists for printing
            aqdata = pm25.read()
            
            # 2. Print PM2.5 Data (Your original format)
            print("\nConcentration Units (standard)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % 
                  (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"]))
            
            print("Concentration Units (environmental)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % 
                  (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"]))
            
            # 3. Print BME680 Data
            print("---------------------------------------")
            print("Temperature: %0.1f C" % bme680.temperature)
            print("Gas: %d ohm" % bme680.gas)
            print("Humidity: %0.1f %%" % bme680.relative_humidity)
            print("Pressure: %0.3f hPa" % bme680.pressure)
            
            t_now = time.time()
            s_now = time.strftime("%A, %B %d, %Y %I:%M:%S %p", time.localtime(t_now))
            print(s_now)

            # 4. Save to CSV inside the loop so you don't lose data
            # Writing: Timestamp, Temp, Gas, Humidity, Pressure, PM2.5
            csvwriter.writerow([t_now, bme680.temperature, bme680.gas, 
                                bme680.relative_humidity, bme680.pressure, aqdata["pm25 env"]])
            
            # Force write to disk
            file.flush()

        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue

        time.sleep(timep)
        timerun += timep

print("Run complete.")
