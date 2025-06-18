#!/usr/bin/env python

import typer
import minimalmodbus
import serial
from typing import Optional

from subsoil.vfs.fs import FS
from subsoil.logger.logger_setup import LoggerSetup
from subsoil.usb_manager import USBManager
from subsoil.sensors.sensor_connection_config import SensorConnectionConfig
from subsoil.sensors.autoconfig import AutoConfig
from subsoil.cli.signal_manager import SignalManager
from subsoil.cli.prompter import SensorInputPrompter

SignalManager()

app = typer.Typer()
logger = LoggerSetup.get_logger("SubSoilCLI")
fs = FS()


class SoilSensor:
    def __init__(self, config: SensorConnectionConfig) -> None:
        self.logger = LoggerSetup.get_logger(self.__class__.__name__)
        self.instrument = minimalmodbus.Instrument(config.port, config.slave_address)
        self.instrument.serial.baudrate = config.baudrate
        self.instrument.serial.timeout = config.timeout
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.logger.info(f"Initialized SoilSensor on port {config.port}")

    def read_all(self) -> Optional[dict]:
        try:
            return {
                "temperature_c": self.instrument.read_register(0x00, 1, 4) / 10.0,
                "humidity_percent": self.instrument.read_register(0x01, 1, 4) / 10.0,
                "ec_us_cm": self.instrument.read_register(0x02, 0, 4),
                "ph": self.instrument.read_register(0x03, 2, 4) / 100.0,
                "nitrogen_mg_kg": self.instrument.read_register(0x04, 0, 4),
                "phosphorus_mg_kg": self.instrument.read_register(0x05, 0, 4),
                "potassium_mg_kg": self.instrument.read_register(0x06, 0, 4),
            }
        except Exception as e:
            self.logger.error(f"Failed to read from sensor: {e}")
            return None


@app.command()
def setup() -> None:
    """Run initial sensor setup and save connection info."""
    try:
        if fs.sensor_device_details_json.exists():
            old_config = SensorConnectionConfig.from_file(fs.sensor_device_details_json)
            if old_config:
                print("⚠️ Existing sensor configuration found:")
                print(old_config.to_json())
            else:
                print("⚠️ sensor_device_details.json exists but is invalid JSON.")

            confirm = input("Proceeding will overwrite the current config. Do you want to continue? [y/N]: ").strip().lower()
            if confirm != "y":
                print("❌ Setup cancelled.")
                return

            fs.backup_existing_config()

        usb = USBManager()
        port = usb.select_usb_device()

        print("🧪 Would you like to auto-detect sensor configuration?")
        print("We'll scan common baudrates and slave addresses.")
        auto = input("Run auto-config? [Y/n]: ").strip().lower() or "y"

        if auto == "y":
            result = AutoConfig(port).scan()
            if result:
                slave_address, baudrate = result
                timeout = 1.0
            else:
                print("⚠️ AutoConfig failed to detect valid config.")
                choice = input("Would you like to [M]anually enter values or [D]efault to basic values? [M/d]: ").strip().lower() or "d"
                if choice == "m":
                    slave_address, baudrate, timeout = SensorInputPrompter.interactive_config()
                else:
                    slave_address, baudrate, timeout = SensorInputPrompter.default_config()
        else:
            slave_address, baudrate, timeout = SensorInputPrompter.interactive_config()

        config = SensorConnectionConfig(
            port=port,
            slave_address=slave_address,
            baudrate=baudrate,
            timeout=timeout,
        )

        fs.sensor_device_details_json.write_text(config.to_json())
        logger.info("Sensor config saved to disk.")
        print("💾 Configuration saved.")

        sensor = SoilSensor(config)
        if sensor.read_all():
            print("✅ Sensor responded successfully.")
            logger.info("Sensor test passed.")
        else:
            print("⚠️ Sensor did not respond. Configuration still saved for manual retry.")
            logger.warning("Sensor test failed, but config saved.")

    except Exception as e:
        logger.exception(f"Setup failed: {e}")
        print("❌ Setup failed. See logs for more info.")


@app.command()
def read() -> None:
    """Read values from soil sensor."""
    config = SensorConnectionConfig.from_file(fs.sensor_device_details_json)
    if not config:
        print("⚠️ Config missing or invalid. Run 'subsoil setup'.")
        raise typer.Exit(1)
    try:
        sensor = SoilSensor(config)
        result = sensor.read_all()
        if result:
            for key, val in result.items():
                print(f"{key}: {val}")
        else:
            print("⚠️ No data from sensor.")
    except Exception as e:
        logger.exception(f"Read failed: {e}")
        print("❌ Error reading sensor. Check logs.")


def main() -> None:
    try:
        app()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print("❌ Fatal error. See logs.")


if __name__ == "__main__":
    main()
