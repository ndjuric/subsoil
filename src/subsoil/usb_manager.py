from typing import List, Tuple
import pyudev
from subsoil.logger.logger_setup import LoggerSetup


class USBManager:
    def __init__(self) -> None:
        self.logger = LoggerSetup.get_logger(self.__class__.__name__)
        self.context = pyudev.Context()

    def list_candidate_usb_devices(self) -> List[Tuple[str, str]]:
        candidates = []
        for device in self.context.list_devices(subsystem='tty'):
            if 'ID_VENDOR' in device and 'ID_MODEL' in device:
                name = f"{device.get('ID_VENDOR')} {device.get('ID_MODEL')}"
                devnode = device.device_node
                if any(x in name.lower() for x in ['keyboard', 'mouse', 'hub']):
                    continue
                candidates.append((devnode, name))
        self.logger.debug(f"Candidate USB devices: {candidates}")
        return candidates


    def select_usb_device(self) -> str:
        devices = self.list_candidate_usb_devices()
        if not devices:
            print("No likely USB serial devices found.")
            self.logger.warning("No USB serial candidates found.")
            raise RuntimeError("No USB serial devices detected.")

        print("USB devices likely to be sensors:")
        for idx, (devnode, name) in enumerate(devices):
            print(f"{idx + 1}: {devnode} — {name}")

        while True:
            try:
                choice = int(input(f"Select device [1–{len(devices)}]: "))
                if 1 <= choice <= len(devices):
                    selected = devices[choice - 1][0]
                    self.logger.info(f"User selected USB device: {selected}")
                    return selected
                print(f"Invalid selection. Please enter a number between 1 and {len(devices)}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

