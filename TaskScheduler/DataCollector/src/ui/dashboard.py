"""
Dashboard Presenter for DataCollector.
Coordinates live telemetry feeds, status cards, active prompt dialogs, and timeline rendering for the desktop application.
"""

from typing import Dict, Any, List, Optional
from engine import TelemetryEngine
from db_manager import DatabaseManager
from active_learning import ActiveLearningManager
from .disclaimer import DisclaimerManager
from .timeline import RetrospectiveTimeline

class DashboardPresenter:
    def __init__(
        self,
        engine: TelemetryEngine,
        db: DatabaseManager,
        disclaimer_mgr: Optional[DisclaimerManager] = None
    ):
        self.engine = engine
        self.db = db
        self.disclaimer = disclaimer_mgr if disclaimer_mgr is not None else DisclaimerManager()
        self.timeline = RetrospectiveTimeline(db)
        self.active_learning = ActiveLearningManager(db)

    def can_start_recording(self) -> bool:
        return self.disclaimer.has_consented()

    def start_recording(self) -> bool:
        if not self.can_start_recording():
            return False
        self.engine.start()
        return True

    def pause_recording(self):
        self.engine.pause()

    def resume_recording(self):
        self.engine.resume()

    def stop_recording(self):
        self.engine.stop()

    def get_dashboard_state(self) -> Dict[str, Any]:
        stats = self.engine.get_current_stats()
        latest = stats.get("latest_record") or {}

        # Check for active learning prompt
        prompt_required = False
        if latest:
            prompt_required = self.active_learning.evaluate_prompt_trigger(latest)

        return {
            "has_consented": self.disclaimer.has_consented(),
            "is_recording": stats.get("is_running", False),
            "is_paused": stats.get("is_paused", False),
            "total_records_collected": stats.get("total_records", 0),
            "total_db_records": self.db.count_records(),
            "current_app": latest.get("app_name", "Idle / System"),
            "current_title": latest.get("window_title_sanitized", "No active window"),
            "current_cognitive_state": latest.get("cognitive_state", "UNCLASSIFIED"),
            "current_domain": latest.get("domain_label", "Unlabeled"),
            "confidence": latest.get("confidence", 0.0),
            "keystrokes_per_min": latest.get("keystrokes_per_min", 0.0),
            "mouse_velocity_avg": latest.get("mouse_velocity_avg", 0.0),
            "is_audio_playing": latest.get("is_audio_playing", False),
            "system_idle_seconds": latest.get("system_idle_seconds", 0.0),
            "prompt_dialog_active": prompt_required,
            "recent_timeline_blocks": self.timeline.get_timeline_blocks()
        }

    def respond_to_prompt(self, domain_label: str, cognitive_state: Optional[str] = None) -> int:
        return self.active_learning.apply_user_label(
            domain_label=domain_label,
            cognitive_state=cognitive_state,
            source="ACTIVE_PROMPT"
        )
