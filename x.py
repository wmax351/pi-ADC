from smbus2 import SMBus
import struct
import time
from math import sqrt
from statistics import mean

Pmin=-1
Pmax=1
Q1=15
Q2=17
Q3=7
Q4=5
Q5=7
Q6=21
Tres=0.01
Pres=0.0001
air_dens=1.225 #kg/m3

def get_u16(arr):
    return struct.unpack('>H', bytearray(arr))[0]

def get_u32(arr):
    return struct.unpack('>I', bytearray([0] + arr))[0]

class MS5525DSO:
    def __init__(self, bus, bid,pcorr,tcorr):
        self.bus = bus
        self.bid = bid
        self.pcorr = pcorr
        self.tcorr = tcorr

        self.reset()
        consts = self.get_constants()
        self.C1 = consts[1]
        self.C2 = consts[2]
        self.C3 = consts[3]
        self.C4 = consts[4]
        self.C5 = consts[5]
        self.C6 = consts[6]

    def reset(self):
        print(f"Resetting {self.bid}...")
        self.bus.write_byte(self.bid, 0x1E)
        time.sleep(0.5)

    def get_constants(self):
        constants = [0]*8
        for i in range(8):
            byte = 0xA0 + (i*2)
            arr = self.bus.read_i2c_block_data(self.bid, byte, 2)
            print(f"0x{byte:x}=0x{arr}", get_u16(arr))
            constants[i] = get_u16(arr)
        return constants

    def get_temperature(self):
        self.bus.write_byte(self.bid, 0x58) # OSR=4096, 0x58 D2
        time.sleep(0.02)
        arr = self.bus.read_i2c_block_data(self.bid, 0x00, 3)
        d2 = get_u32(arr)
        t_ref = self.C5 * 2**Q5
        tempsens = self.C6/(2**Q6)
        dT = d2 - t_ref
        temp = 2000 + dT * tempsens + self.tcorr
        return (dT, temp)

    def get_pressure(self, dT=None):
        if dT is None:
            dT, temp = self.get_temperature()
        self.bus.write_byte(self.bid, 0x48) # OSR=4096, 0x48 D1
        time.sleep(0.02)
        arr = self.bus.read_i2c_block_data(self.bid, 0x00, 3)
        d1 = get_u32(arr)
        off_t1 = self.C2 * (2**Q2)
        tco = self.C4 / (2**Q4)
        off = off_t1 + tco * dT
        
        sens_t1 = self.C1 * (2**Q1)
        tcs = self.C3 / (2**Q3)
        sens = sens_t1 + tcs * dT

        pressure = ((d1 * sens / 2**21) - off) / (2**15) 
        return pressure

    def temp_and_pressure(self):
        dT, temp = self.get_temperature()
        pressure = self.get_pressure(dT)
        
        temp = int(temp) / 100.
#         print(f"Temp: {temp} degC")
        press = int((int(pressure) / 10000.)*6895.) + self.pcorr
#         print(f"Pressure: {press} Pascal")

        return temp, press

    def dump(self):
        print(f"C1: {self.C1}")
        print(f"C2: {self.C2}")
        print(f"C3: {self.C3}")
        print(f"C4: {self.C4}")
        print(f"C5: {self.C5}")
        print(f"C6: {self.C6}")


    
def calibrate_asi_aoa(cycles):
    with SMBus(1) as bus:
        
        print('calibrating')

        devASI = MS5525DSO(bus, 0x76, 0,0) 
        devASI.dump()
        # get constants 

        devAOA = MS5525DSO(bus, 0x77, 0,0) 
        devAOA.dump()
        
        asiPreslist = []
        asiTemplist = []
        aoaPreslist = []
        aoaTemplist = []
        
        for i in range(cycles):
            
            asi_temp,asi_pres=devASI.temp_and_pressure()
            
            aoa_temp,aoa_pres=devAOA.temp_and_pressure()
            
            asiPreslist.append(asi_pres)
            asiTemplist.append(asi_temp)
            aoaPreslist.append(aoa_pres)
            aoaTemplist.append(aoa_temp)
        
        
        asi_pres_avg = mean(asiPreslist)
        asi_temp_avg = mean(asiTemplist)
        aoa_pres_avg = mean(aoaPreslist)
        aoa_temp_avg = mean(aoaTemplist)
        
        
        print('count',len(asiPreslist))
        print('mean asi pres', asi_pres_avg)
        print('mean asi temp', asi_temp_avg)
        print('mean aoa pres', aoa_pres_avg)
        print('mean aoa temp', aoa_temp_avg)
        
        asi_pres_corr = -asi_pres_avg
        aoa_pres_corr = -aoa_pres_avg
        aoa_temp_corr = (asi_temp_avg - aoa_temp_avg)
        asi_temp_corr = 0
        
        return (asi_pres_corr, asi_temp_corr, aoa_pres_corr, aoa_temp_corr)
 
# get calibration for zero 
asi_pres_corr,asi_temp_corr,aoa_pres_corr,aoa_temp_corr = calibrate_asi_aoa(100) 

 
 
with SMBus(1) as bus:

    devASI = MS5525DSO(bus, 0x76, asi_pres_corr, asi_temp_corr)
#     devASI.dump()
    # get constants 

    devAOA = MS5525DSO(bus, 0x77, aoa_pres_corr, aoa_temp_corr) 
#     devAOA.dump()
    
    while True:
        # can consider using deque routines here
        asi_temp,asi_pres=devASI.temp_and_pressure()
        IAS=sqrt(2*abs(asi_pres)/air_dens)*1.944
        
        
        print('ASI Press', round(asi_pres,0), 'Pa', round(IAS,0),"kts IAS")
                
        aoa_temp,aoa_pres=devAOA.temp_and_pressure()
        # Can try different formulas
        AOA_ratio = asi_pres/(2* asi_pres - aoa_pres)
        
        print("AOA Pres", round(aoa_pres,0), 'Pa', 'AOA Ratio=', round(AOA_ratio,2))
        time.sleep(.25)
        
    #while True:
    #    dT, temp = devASI.get_temperature()
    #    print("ASI Temp (dT, temp):", dT, temp)
    #    print("ASI Pressure:", devASI.get_pressure(dT))
    #    dT, temp = devAOA.get_temperature()
    #    print("AOA Temp (dT, temp):", dT, temp)
    #    print("AOA Pressure:", devAOA.get_pressure(dT))
    #    time.sleep(1)

    #while True:
    #    print('-'*20)
    #    # get adc values
    #    bus.write_byte(DEV, 0x40) # OSR=256, D1
    #    time.sleep(0.1)
    #    press = bus.read_i2c_block_data(DEV, 0x00, 3)
    #    print(f"pressure={press}")

    #    time.sleep(0.1)

    #    bus.write_byte(DEV, 0x50) # OSR=256, D2
    #    time.sleep(0.1)
    #    temp = bus.read_i2c_block_data(DEV, 0x00, 3)
    #    print(f"temperature={temp}")

    #    time.sleep(0.3)

