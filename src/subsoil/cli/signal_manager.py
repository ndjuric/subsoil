#!/usr/bin/env python

import signal
import sys
from subsoil.logger.logger_setup import LoggerSetup

class SignalManager:
    def __init__(self) -> None:
        self.logger = LoggerSetup.get_logger("SignalHandler")
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _handle_sigint(self, sig, frame) -> None:
        self.logger.info("User pressed Ctrl-C. Exiting cleanly.")
        print("⛔ User pressed Ctrl-C. Exiting.")
        sys.exit(0)
