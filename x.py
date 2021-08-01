from smbus2 import SMBus
import time

Sens_ASI = 0x76
Sens_AOA = 0x77

with SMBus(1) as bus:
    print("Resetting ASI...")
    bus.write_byte(Sens_ASI, 0x1E)
    time.sleep(0.5)
    print("Reading ASI...")
    # PROM read
    for i in range(0,16,2):
        byte = 0xA0 + i
        read = bus.read_i2c_block_data(Sens_ASI, byte, 2)
        print(f"ASI 0x{byte:x}=0x{read}")
        
    print("Resetting AOA...")
    bus.write_byte(Sens_AOA, 0x1E)
    time.sleep(0.5)
    print("Reading AOA...")
    # PROM read
    for i in range(0,16,2):
        byte = 0xA0 + i
        read = bus.read_i2c_block_data(Sens_AOA, byte, 2)
        print(f"AOA 0x{byte:x}=0x{read}")

    while True:
        print('-'*20)
        # get adc values
        bus.write_byte(Sens_ASI, 0x40) # OSR=256, D1
        time.sleep(0.1)
        press = bus.read_i2c_block_data(Sens_ASI, 0x00, 3)
        print(f"ASI pressure={press}")
        
        print('-'*20)
        # get adc values
        bus.write_byte(Sens_AOA, 0x40) # OSR=256, D1
        time.sleep(0.1)
        press = bus.read_i2c_block_data(Sens_AOA, 0x00, 3)
        print(f"AOA pressure={press}")
        time.sleep(0.1)

        #bus.write_byte(Sens_ASI, 0x50) # OSR=256, D2
        #time.sleep(0.1)
        #temp = bus.read_i2c_block_data(Sens_ASI, 0x00, 3)
        #print(f"temperature={temp}")

        time.sleep(0.3)
