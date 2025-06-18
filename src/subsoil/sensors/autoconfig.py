#!/usr/bin/env python

import minimalmodbus
import serial
from typing import Optional, Tuple
from subsoil.logger.logger_setup import LoggerSetup

class AutoConfig:
    BAUD_RATES = [9600, 4800, 19200, 2400, 38400]
    SLAVE_ADDRESSES = range(1, 11)
    TIMEOUT = 0.2

    def __init__(self, port: str) -> None:
        self.logger = LoggerSetup.get_logger(self.__class__.__name__)
        self.port = port

    def scan(self) -> Optional[Tuple[int, int]]:
        print("🔍 Starting AutoConfig scan for Modbus sensor...")
        print(f"Port: {self.port}")
        print("Testing register 0 across common baud rates and slave addresses.\n")
        self.logger.info(f"AutoConfig started on port {self.port}")

        for baudrate in self.BAUD_RATES:
            for slave_addr in self.SLAVE_ADDRESSES:
                print(f"→ Trying baudrate={baudrate}, slave_address={slave_addr} ... ", end='', flush=True)
                try:
                    instrument = minimalmodbus.Instrument(self.port, slave_addr)
                    instrument.serial.baudrate = baudrate
                    instrument.serial.bytesize = 8
                    instrument.serial.parity = serial.PARITY_NONE
                    instrument.serial.stopbits = 1
                    instrument.serial.timeout = self.TIMEOUT
                    instrument.mode = minimalmodbus.MODE_RTU
                    instrument.clear_buffers_before_each_transaction = True

                    response = instrument.read_register(0, functioncode=3)
                    print("✅ Success!")
                    print("=" * 42)
                    print("  ✅  VALID CONFIGURATION FOUND")
                    print("=" * 42)
                    print(f"  Port: {self.port}")
                    print(f"  Baudrate: {baudrate}")
                    print(f"  Slave Address: {slave_addr}")
                    print(f"  Register[0] value: {response}")
                    print("=" * 42)
                    self.logger.info(f"AutoConfig success: baudrate={baudrate}, slave={slave_addr}, value={response}")
                    return slave_addr, baudrate

                except Exception as e:
                    print("❌", flush=True)
                    self.logger.debug(f"AutoConfig failed: baudrate={baudrate}, slave={slave_addr}, error={e}")

        print("⚠️ No working combination found. Please try manual configuration or check sensor wiring.")
        self.logger.warning("AutoConfig failed — no valid configuration found.")
        return None
