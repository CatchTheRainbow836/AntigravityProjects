"""
Privacy Disclaimer and Consent Manager for DataCollector.
Presents transparent terms regarding telemetry metrics and prevents data recording until user grants explicit consent.
"""

import json
import os
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.datacollector_consent.json")

DISCLAIMER_TEXT = """
═════════════════════════════════════════════════════════════════════
          AI TASK SCHEDULER: DATA COLLECTOR — PRIVACY NOTICE
═════════════════════════════════════════════════════════════════════

This application is designed to record behavioral telemetry to train an
autonomous AI task and homework scheduler.

WHAT IS COLLECTED:
✓ Aggregate typing frequency (keystrokes per minute & burst cadence)
✓ Mouse velocity (pixels/sec), click counts, and scroll activity
✓ Foreground application executable name (e.g. WINWORD.EXE, Code.exe)
✓ Sanitized window title (emails and authentication tokens redacted)
✓ Screen area ratio occupied by active windows
✓ System idle duration & binary audio output state

WHAT IS STRICTLY NEVER COLLECTED:
✗ Raw keystrokes (passwords, messages, and typed text are NEVER logged)
✗ Screen recordings or screenshots
✗ Audio/microphone recordings or speech
✗ Personal files or file contents

DATA STORAGE:
All data is stored STRICTLY LOCALLY on your computer in an encrypted/local
SQLite database. Nothing is sent over the internet or uploaded to any cloud.

By clicking 'I Agree', you consent to local telemetry recording.
═════════════════════════════════════════════════════════════════════
"""

class DisclaimerManager:
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH, storage_path: Optional[str] = None):
        self.config_path = storage_path if storage_path is not None else config_path

    def get_disclaimer_text(self) -> str:
        return DISCLAIMER_TEXT.strip()

    def has_consented(self) -> bool:
        if not os.path.exists(self.config_path):
            return False
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("consent_granted", False) is True
        except Exception:
            return False

    def grant_consent(self) -> bool:
        try:
            data = {
                "consent_granted": True,
                "version": "1.0",
                "timestamp": json.loads(json.dumps(os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0))
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def revoke_consent(self) -> bool:
        try:
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            return True
        except Exception:
            return False
