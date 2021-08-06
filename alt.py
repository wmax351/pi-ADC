from smbus2 import SMBus
import adafruit_bmp3xx
import struct
import time
import board
from math import sqrt
from statistics import mean

print(board.I2C())
# I2C setup
i2c = 1 #board.I2C()  # uses board.SCL and board.SDA
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)


bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2

while True:
    print(
        "Pressure: {:6.4f}  Temperature: {:5.2f}".format(bmp.pressure, bmp.temperature)
    )
    time.sleep(1)


# # From plugin
#         while True:
#             if self.getout:
#                 break
#             time.sleep(sleep_time)
#             self.count += 1
#             stdbaro = 29.92
#             currentbaro = self.parent.db_read("BARO")
#             init_alt = round((float(self.sensor.read_altitude())*3.28083989502))
#             self.alt = float((self.alt*self.smooted)+(1.0-self.smooted)*(init_alt))
#             altitude = ((float(currentbaro[0]) - stdbaro)*1000) + self.alt
#             self.parent.db_write("ALT", altitude)
#             time.sleep(sleep_time)
#             cat = float(self.sensor.read_temperature())
#             self.parent.db_write(self.tkey, cat)
#             time.sleep(sleep_time)
#             airpress = int(self.sensor.read_pressure())
#             self.parent.db_write(self.pkey, airpress)
#         self.running = False
