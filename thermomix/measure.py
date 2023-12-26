import minimalmodbus
import serial

from thermomix.config import (MODBUS_BAUDRATE, MODBUS_BYTESIZE, MODBUS_FRAQ,
                              MODBUS_PARITY, MODBUS_PORT, MODBUS_STOPBITS,
                              MODBUS_TIMEOUT)


class MeasureException(Exception):
    pass


def get_measures(devices):
    try:
        return _get_measures(devices)
    except serial.serialutil.SerialException:
        raise MeasureException("MODBUS Connector not found in given port")
    except minimalmodbus.NoResponseError:
        raise MeasureException("One of devices did not respond")


def _get_measures(devices):
    instrument = minimalmodbus.Instrument(MODBUS_PORT,
                                          1,
                                          mode=minimalmodbus.MODE_RTU)

    instrument.serial.baudrate = MODBUS_BAUDRATE
    instrument.serial.bytesize = MODBUS_BYTESIZE
    instrument.serial.stopbits = MODBUS_STOPBITS
    instrument.serial.parity = MODBUS_PARITY
    instrument.serial.timeout = MODBUS_TIMEOUT

    instrument.close_port_after_each_call = True
    instrument.clear_buffers_before_each_transaction = True

    measures = {}

    for device, data in devices.items():
        measures[device] = {
            'value': instrument.read_register(data['address']) / MODBUS_FRAQ,
            'address': data['address'],
        }
    return measures
