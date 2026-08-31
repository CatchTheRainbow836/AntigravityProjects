"""
Unit and Lifecycle Tests for GUI Components, Autostart, and Tray Daemon.
"""

import unittest
import tempfile
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from autostart import AutostartManager
from ui.tray import TrayManager
from ui.disclaimer import DisclaimerManager
from db_manager import DatabaseManager

class TestGUILifecycle(unittest.TestCase):
    def test_autostart_manager(self):
        asm = AutostartManager(executable_path="/test/path/DataCollector.exe")
        self.assertTrue(asm.enable_autostart())
        self.assertTrue(asm.disable_autostart())

    def test_tray_manager_lifecycle(self):
        toggled = []
        tray = TrayManager(
            on_show_window=lambda: None,
            on_toggle_recording=lambda: toggled.append(True),
            on_export=lambda: None,
            on_exit=lambda: None
        )
        tray.set_recording_state(True)
        self.assertTrue(tray._is_recording)
        tray.set_recording_state(False)
        self.assertFalse(tray._is_recording)

    def test_disclaimer_consent_lifecycle(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temp_file.close()
        try:
            mgr = DisclaimerManager(storage_path=temp_file.name)
            self.assertFalse(mgr.has_consented())
            mgr.grant_consent()
            self.assertTrue(mgr.has_consented())
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

if __name__ == "__main__":
    unittest.main()
