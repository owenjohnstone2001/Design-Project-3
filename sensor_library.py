import busio
import board
import smbus
import time
from math import pow

class Gas_Sensor(object):
    DEFAULT_I2C_ADDR = 0x04

    ADDR_IS_SET = 0  # if this is the first time to run, if 1126, set
    ADDR_FACTORY_ADC_NH3 = 2
    ADDR_FACTORY_ADC_CO = 4
    ADDR_FACTORY_ADC_NO2 = 6

    ADDR_USER_ADC_HN3 = 8
    ADDR_USER_ADC_CO = 10
    ADDR_USER_ADC_NO2 = 12
    ADDR_IF_CALI = 14  # IF USER HAD CALI

    ADDR_I2C_ADDRESS = 20

    CH_VALUE_NH3 = 1
    CH_VALUE_CO = 2
    CH_VALUE_NO2 = 3

    CMD_ADC_RES0 = 1  # NH3
    CMD_ADC_RES1 = 2  # CO
    CMD_ADC_RES2 = 3  # NO2
    CMD_ADC_RESALL = 4  # ALL CHANNEL
    CMD_CHANGE_I2C = 5  # CHANGE I2C
    CMD_READ_EEPROM = 6  # READ EEPROM VALUE, RETURN UNSIGNED INT
    CMD_SET_R0_ADC = 7  # SET R0 ADC VALUE
    CMD_GET_R0_ADC = 8  # GET R0 ADC VALUE
    CMD_GET_R0_ADC_FACTORY = 9  # GET FACTORY R0 ADC VALUE
    CMD_CONTROL_LED = 10
    CMD_CONTROL_PWR = 11

    CO = 0
    NO2 = 1
    NH3 = 2
    C3H8 = 3
    C4H10 = 4
    CH4 = 5
    H2 = 6
    C2H5OH = 7

    adcValueR0_NH3_Buf = 0
    adcValueR0_C0_Buf = 0
    adcValueR0_NO2_Buf = 0

    def __init__(self, addr=DEFAULT_I2C_ADDR):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.addr = addr
        self.version = self.get_version()

    def cmd(self, cmd, nbytes=2):
        self.i2c.writeto(self.addr, bytes(cmd))
        dta = 0
        buf = bytearray(nbytes)
        raw = self.i2c.readfrom_into(self.addr, buf)
        for byte in buf:
            dta = dta * 256 + int(byte)
        if cmd == self.CH_VALUE_NH3:
            if dta > 0:
                self.adcValueR0_NH3_Buf = dta
            else:
                dta = self.adcValueR0_NH3_Buf
        elif cmd == self.CH_VALUE_CO:
            if dta > 0:
                self.adcValueR0_CO_Buf = dta
            else:
                dta = self.adcValueR0_CO_Buf
        elif cmd == self.CH_VALUE_NO2:
            if dta > 0:
                self.adcValueR0_NO2_Buf = dta
            else:
                dta = self.adcValueR0_NO2_Buf
        return dta

    def get_version(self):
        if self.cmd([self.CMD_READ_EEPROM, self.ADDR_IS_SET]) == 1126:
            return 2
        else:
            print("version currently not supported")
            from sys import exit
            exit(1)

    def CO_gas(self): # Carbon Monoxide gas, in ppm (parts per million)
        A0_1 = self.cmd([6, self.ADDR_USER_ADC_CO])
        An_1 = self.cmd([self.CH_VALUE_CO])
        ratio1 = An_1 / A0_1 * (1023.0 - A0_1) / (1023.0 - An_1)
        c = pow(ratio1, -1.179) * 4.385
        return c

    def NO2_gas(self): # Nitrogen Dioxide gas, in ppm
        A0_2 = self.cmd([6, self.ADDR_USER_ADC_NO2])
        An_2 = self.cmd([self.CH_VALUE_NO2])
        ratio2 = An_2 / A0_2 * (1023.0 - A0_2) / (1023.0 - An_2)
        c = pow(ratio2, 1.007) / 6.855
        return c

    def H2_gas(self): # Hydrogen, in ppm
        A0_1 = self.cmd([6, self.ADDR_USER_ADC_CO])
        An_1 = self.cmd([self.CH_VALUE_CO])
        ratio1 = An_1 / A0_1 * (1023.0 - A0_1) / (1023.0 - An_1)
        c = pow(ratio1, -1.8) * 0.73
        return c

    def ammonia(self): # Ammonia (NH3), in ppm
        A0_0 = self.cmd([6, self.ADDR_USER_ADC_HN3])
        An_0 = self.cmd([self.CH_VALUE_NH3])
        ratio0 = An_0 / A0_0 * (1023.0 - A0_0) / (1023.0 - An_0)
        c = pow(ratio0, -1.67) / 1.47
        return c

    def propane(self): # Propane (C3H8), in ppm
        A0_0 = self.cmd([6, self.ADDR_USER_ADC_HN3])
        An_0 = self.cmd([self.CH_VALUE_NH3])
        ratio0 = An_0 / A0_0 * (1023.0 - A0_0) / (1023.0 - An_0)
        c = pow(ratio0, -2.518) * 570.164
        return c

    def butane(self): # Butane (C4H10), in ppm
        A0_0 = self.cmd([6, self.ADDR_USER_ADC_HN3])
        An_0 = self.cmd([self.CH_VALUE_NH3])
        ratio0 = An_0 / A0_0 * (1023.0 - A0_0) / (1023.0 - An_0)
        c = pow(ratio0, -2.138) * 398.107
        return c

    def methane(self): # Methane (CH4), in ppm
        A0_1 = self.cmd([6, self.ADDR_USER_ADC_CO])
        An_1 = self.cmd([self.CH_VALUE_CO])
        ratio1 = An_1 / A0_1 * (1023.0 - A0_1) / (1023.0 - An_1)
        c = pow(ratio1, -4.363) * 630.957
        return c

    def ethanol(self): # Ethanol (C2H5OH), in ppm
        A0_1 = self.cmd([6, self.ADDR_USER_ADC_CO])
        An_1 = self.cmd([self.CH_VALUE_CO])
        ratio1 = An_1 / A0_1 * (1023.0 - A0_1) / (1023.0 - An_1)
        c = pow(ratio1, -1.552) * 1.622
        return c
