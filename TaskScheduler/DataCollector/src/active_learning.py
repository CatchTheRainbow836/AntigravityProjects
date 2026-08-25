"""
Active Learning and Smart Prompt Trigger Manager for DataCollector.
Manages state transition detection, low-confidence prompt triggers, and retroactive ground-truth label application.
"""

import time
from typing import Dict, Any, List, Optional
from db_manager import DatabaseManager

class ActiveLearningManager:
    def __init__(
        self,
        db: DatabaseManager,
        confidence_threshold: float = 0.60,
        prompt_interval_seconds: float = 300.0 # 5 minutes default
    ):
        self.db = db
        self.confidence_threshold = confidence_threshold
        self.prompt_interval_seconds = prompt_interval_seconds

        self._last_prompt_time = 0.0
        self._last_app_name: Optional[str] = None
        self._last_cognitive_state: Optional[str] = None
        self._unclassified_count = 0

    def evaluate_prompt_trigger(self, latest_record: Dict[str, Any]) -> bool:
        """
        Determines whether a user prompt popup should be shown based on:
        1. Confidence below threshold (< 0.60)
        2. Significant state/app transition occurred
        3. Elapsed time since last prompt exceeds configured interval
        """
        now = time.time()
        confidence = latest_record.get("confidence", 0.0)
        app_name = latest_record.get("app_name", "")
        cognitive_state = latest_record.get("cognitive_state", "UNCLASSIFIED")

        # Check if confidence is low
        is_low_confidence = (confidence < self.confidence_threshold) or (cognitive_state == "UNCLASSIFIED")

        # Check for context transition
        is_transition = False
        if self._last_app_name and app_name != self._last_app_name:
            is_transition = True

        self._last_app_name = app_name
        self._last_cognitive_state = cognitive_state

        if is_low_confidence:
            self._unclassified_count += 1
        else:
            self._unclassified_count = 0

        # Don't spam: check minimum prompt interval
        time_since_last = now - self._last_prompt_time
        if is_low_confidence:
            if self._last_prompt_time == 0.0 or time_since_last >= self.prompt_interval_seconds:
                self._last_prompt_time = now
                return True

        return False

    def apply_user_label(
        self,
        domain_label: str,
        cognitive_state: Optional[str] = None,
        lookback_minutes: int = 15,
        source: str = "ACTIVE_PROMPT"
    ) -> int:
        """
        Applies a user-confirmed ground truth label to recent unclassified or low-confidence records.
        """
        records = self.db.get_unexported_records()
        if not records:
            return 0

        updated_ids = []
        for r in records[-lookback_minutes * 12:]: # Assuming ~12 5-second slices per minute
            if r["label_source"] in ("HEURISTIC_RULE", "UNCLASSIFIED") or r["confidence"] < 0.7:
                updated_ids.append(r["id"])

        if not updated_ids:
            return 0

        placeholders = ",".join("?" for _ in updated_ids)
        params = [domain_label, 1.0, source]
        query = f"""
        UPDATE telemetry_records
        SET domain_label = ?, confidence = ?, label_source = ?
        """
        if cognitive_state:
            query += f", cognitive_state = ?"
            params.append(cognitive_state)

        query += f" WHERE id IN ({placeholders})"
        params.extend(updated_ids)

        with self.db._lock:
            self.db.conn.execute(query, params)
            self.db.conn.commit()

        return len(updated_ids)

    def add_user_preset(self, preset_name: str, color_hex: str = "#3B82F6", keywords: List[str] = None):
        import json
        keywords_json = json.dumps(keywords if keywords is not None else [preset_name.lower()])
        query = """
        INSERT OR REPLACE INTO user_presets (preset_name, color_hex, default_keywords)
        VALUES (?, ?, ?)
        """
        with self.db._lock:
            self.db.conn.execute(query, (preset_name, color_hex, keywords_json))
            self.db.conn.commit()
