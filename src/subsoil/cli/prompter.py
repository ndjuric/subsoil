#!/usr/bin/env python

from subsoil.cli.constants import ModbusConstants
from typing import Tuple


class SensorInputPrompter:
    @staticmethod
    def ask_slave_address() -> int:
        while True:
            user = input("Enter slave address (1–247) [default 1]: ") or "1"
            try:
                val = int(user)
                if ModbusConstants.is_valid_slave_address(val):
                    return val
            except ValueError:
                pass
            print("❌ Invalid address.")

    @staticmethod
    def ask_baudrate() -> int:
        while True:
            user = input(f"Enter baudrate {ModbusConstants.VALID_BAUDRATES} [default 9600]: ") or "9600"
            try:
                val = int(user)
                if ModbusConstants.is_valid_baudrate(val):
                    return val
            except ValueError:
                pass
            print("❌ Invalid baudrate.")

    @staticmethod
    def ask_timeout() -> float:
        while True:
            user = input("Enter timeout (seconds) [default 1.0]: ") or "1.0"
            try:
                val = float(user)
                if 0.05 <= val <= 10.0:
                    return val
            except ValueError:
                pass
            print("❌ Invalid timeout.")

    @classmethod
    def interactive_config(cls) -> Tuple[int, int, float]:
        """Prompt user for slave address, baudrate, and timeout."""
        slave = cls.ask_slave_address()
        baud = cls.ask_baudrate()
        timeout = cls.ask_timeout()
        return slave, baud, timeout

    @classmethod
    def default_config(cls) -> Tuple[int, int, float]:
        """Return hardcoded safe defaults."""
        return 1, 9600, 1.0
