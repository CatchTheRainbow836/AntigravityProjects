"""
Unit tests for Telemetry Schema validation and structure integrity.
"""

import unittest
import json
import os

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "schema.json")

class TestTelemetrySchema(unittest.TestCase):
    def setUp(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def test_schema_title_and_type(self):
        self.assertEqual(self.schema.get("title"), "TelemetryRecord")
        self.assertEqual(self.schema.get("type"), "object")

    def test_required_fields_present(self):
        required = self.schema.get("required", [])
        expected_fields = [
            "timestamp",
            "app_name",
            "window_title_sanitized",
            "screen_area_pct",
            "keystrokes_per_min",
            "mouse_velocity_avg",
            "clicks_count",
            "scroll_delta",
            "is_audio_playing",
            "system_idle_seconds",
            "cognitive_state",
            "domain_label",
            "confidence",
            "label_source"
        ]
        for field in expected_fields:
            self.assertIn(field, required, f"Field '{field}' must be in required schema list")

    def test_cognitive_state_enum_values(self):
        cognitive_prop = self.schema["properties"]["cognitive_state"]
        enums = cognitive_prop.get("enum", [])
        self.assertIn("DEEP_FOCUS_WRITING", enums)
        self.assertIn("ACTIVE_CODING", enums)
        self.assertIn("RESEARCH_READING", enums)
        self.assertIn("MEDIA_CONSUMPTION", enums)
        self.assertIn("IDLE_AWAY", enums)
        self.assertIn("UNCLASSIFIED", enums)

if __name__ == "__main__":
    unittest.main()
