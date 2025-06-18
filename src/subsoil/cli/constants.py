#!/usr/bin/env python

class ModbusConstants:
    VALID_BAUDRATES = [9600, 4800, 19200, 2400, 38400]
    VALID_SLAVE_ADDRESSES = range(1, 248)

    @classmethod
    def is_valid_baudrate(cls, value: int) -> bool:
        return value in cls.VALID_BAUDRATES

    @classmethod
    def is_valid_slave_address(cls, value: int) -> bool:
        return value in cls.VALID_SLAVE_ADDRESSES
