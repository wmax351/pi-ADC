#!/usr/bin/env python

from smbus import SMBus
import time

def main():
    '''
    Main program function
    '''
    
     i2cbus = SMBus(1)  # Create a new I2C bus
     
     # U4 I2c=0x76, U5 I2C=0x77
     
     


if __name__ == "__main__":
    main()