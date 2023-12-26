DEVICES = {
    "<name>": {
        "address": 0,
    },
    "<name2>": {
        "address": 1,
    },
}

import minimalmodbus

MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 9600
MODBUS_BYTESIZE = 8
MODBUS_STOPBITS = 1
MODBUS_PARITY = minimalmodbus.serial.PARITY_NONE
MODBUS_TIMEOUT = 1

# Read value from device to presented value fraction
MODBUS_FRAQ = 10.0
