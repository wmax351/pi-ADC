from bmp388 import BMP388
import struct
import time
from math import sqrt
from statistics import mean

# # From fixgw plugin
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


# Create a bmp388 object to communicate with I2C.
bmp389 = BMP388()


while True:
    time.sleep(0.5)
    temperature,pressure,altitude = bmp389.get_temperature_and_pressure_and_altitude()
    print(' Temperature = %.1f Pressure = %.2f  Altitude =%.2f '%(temperature/100.0,pressure/100.0,altitude/100.0))
