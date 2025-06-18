#!/usr/bin/env python

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from subsoil.logger.logger_setup import LoggerSetup


@dataclass
class SensorConnectionConfig:
    port: str
    slave_address: int = 1
    baudrate: int = 9600
    timeout: float = 1.0

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def from_file(cls, path: Path) -> Optional["SensorConnectionConfig"]:
        logger = LoggerSetup.get_logger(cls.__name__)
        try:
            data = json.loads(path.read_text())
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to load sensor config: {e}")
            return None
