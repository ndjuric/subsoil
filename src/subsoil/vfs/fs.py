#!/usr/bin/env python
import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

class FS:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[3]
        self.env_file = self.project_root / ".env"
        load_dotenv(self.env_file)
        self.storage_folder = self.project_root / "storage"
        self.logs_folder = self.storage_folder / "logs"
        self.main_log_file = self.logs_folder / "subsoil.log"
        self.sensor_device_details_json = self.storage_folder / "sensor_device_details.json"
        self.backup_folder = self.storage_folder / "backups"
        

        self.log_max_size_mb = int(os.getenv("LOG_MAX_SIZE_MB", 1))
        self.log_max_backup_count = int(os.getenv("LOG_MAX_BACKUP_COUNT", 5))

        self.ensure_directories()

    def ensure_directories(self):
        self.storage_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        self.backup_folder.mkdir(parents=True, exist_ok=True)

    def env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)

    def backup_existing_config(self) -> None:
        """Creates a versioned backup of the current sensor_device_details.json."""
        if not self.sensor_device_details_json.exists():
            return

        from datetime import datetime

        date_part = datetime.now().strftime("%Y%m%d")
        base_name = f"sensor_device_details_{date_part}"
        counter = 1

        while True:
            candidate_name = f"{base_name}_{counter:03d}.json"
            candidate_path = self.backup_folder / candidate_name
            if not candidate_path.exists():
                break
            counter += 1

        candidate_path.write_text(self.sensor_device_details_json.read_text())

