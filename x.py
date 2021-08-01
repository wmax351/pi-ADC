from smbus2 import SMBus
import time

DEV = 0x76


with SMBus(1) as bus:
    print("Resetting...")
    bus.write_byte(DEV, 0x1E)
    time.sleep(0.5)
    print("Reading...")
    # PROM read
    for i in range(0,16,2):
        byte = 0xA0 + i
        read = bus.read_i2c_block_data(DEV, byte, 2)
        print(f"0x{byte:x}=0x{read}")

    while True:
        print('-'*20)
        # get adc values
        bus.write_byte(DEV, 0x40) # OSR=256, D1
        time.sleep(0.1)
        press = bus.read_i2c_block_data(DEV, 0x00, 3)
        print(f"pressure={press}")

        time.sleep(0.1)

        bus.write_byte(DEV, 0x50) # OSR=256, D2
        time.sleep(0.1)
        temp = bus.read_i2c_block_data(DEV, 0x00, 3)
        print(f"temperature={temp}")

        time.sleep(0.3)
