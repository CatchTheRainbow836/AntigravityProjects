"""
Main Desktop Application Window for DataCollector.
Transforms DataCollector into a sleek Windows GUI application featuring sidebar navigation,
dynamic timeline visualizer, live telemetry meters, incremental dataset exporter, and system tray daemon.
"""

import sys
import os
import threading
import customtkinter as ctk
from typing import Optional

# Setup appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from db_manager import DatabaseManager
from classifier import HeuristicClassifier
from engine import TelemetryEngine
from exporter import DatasetExporter
from autostart import AutostartManager
from ui.disclaimer import DisclaimerManager
from ui.tray import TrayManager
from ui.views.disclaimer_view import DisclaimerView
from ui.views.dashboard_view import DashboardView
from ui.views.timeline_view import TimelineView
from ui.views.export_view import ExportView
from ui.views.prompt_modal import PromptModal

class DataCollectorApp(ctk.CTk):
    def __init__(self, db_path: str = "datacollector.db"):
        super().__init__()

        self.db_path = db_path
        self.title("AI Task Scheduler — Behavior Data Collector")
        self.geometry("1020x680")
        self.minsize(880, 580)
        self.configure(fg_color="#0F172A")

        # Core Backend Services
        self.db = DatabaseManager(self.db_path)
        self.classifier = HeuristicClassifier()
        self.engine = TelemetryEngine(db=self.db, classifier_fn=self.classifier.classify)
        self.exporter = DatasetExporter(self.db)
        self.disclaimer_mgr = DisclaimerManager()
        self.autostart_mgr = AutostartManager()

        # System Tray Integration
        self.tray = TrayManager(
            on_show_window=self._restore_from_tray,
            on_toggle_recording=self._toggle_recording,
            on_export=lambda: self.exporter.export_incremental(fmt="jsonl"),
            on_exit=self._clean_exit
        )
        self.tray.start()

        # Protocol hook: closing window minimizes to system tray instead of terminating
        self.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

        self._build_ui()

        # Auto-refresh loop for live telemetry
        self._refresh_telemetry_loop()

    def _build_ui(self):
        # If user hasn't consented yet, show DisclaimerView modal/first-screen
        if not self.disclaimer_mgr.has_consented():
            self._show_disclaimer_screen()
            return

        self._show_main_screen()

    def _show_disclaimer_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.disclaimer_view = DisclaimerView(
            self,
            on_agree=self._handle_consent_granted,
            on_decline=self._handle_consent_declined
        )
        self.disclaimer_view.pack(fill="both", expand=True, padx=40, pady=40)

    def _handle_consent_granted(self):
        self.disclaimer_mgr.grant_consent()
        self.autostart_mgr.enable_autostart()
        self.engine.start()
        self._show_main_screen()

    def _handle_consent_declined(self):
        self.tray.stop()
        self.destroy()
        sys.exit(0)

    def _show_main_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Start telemetry engine if not running
        if not self.engine.is_running:
            self.engine.start()

        # Main Layout Container (Sidebar + Content View)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Frame
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1E293B")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)

        logo_label = ctk.CTkLabel(
            sidebar,
            text="AI DATA COLLECTOR",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#38BDF8"
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="w")

        # Navigation Buttons
        self.nav_buttons = {}
        tabs = [
            ("dashboard", "⚡ Live Dashboard"),
            ("timeline", "📊 Activity Timeline"),
            ("exporter", "💾 Dataset Exporter"),
        ]

        for idx, (key, text) in enumerate(tabs, start=1):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                fg_color="#334155" if key == "dashboard" else "transparent",
                hover_color="#334155",
                text_color="#F8FAFC",
                height=40,
                command=lambda k=key: self._select_tab(k)
            )
            btn.grid(row=idx, column=0, padx=12, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        # Bottom System Info
        sys_info = ctk.CTkLabel(
            sidebar,
            text="v2.0 Standalone\nBackground Logging Active",
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
            justify="left"
        )
        sys_info.grid(row=6, column=0, padx=20, pady=20, sticky="sw")

        # 2. Content Area
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

        # Initialize Views
        self.views = {
            "dashboard": DashboardView(
                self.content_container,
                on_toggle_recording=self._toggle_recording,
                on_trigger_sample=self._trigger_sample
            ),
            "timeline": TimelineView(
                self.content_container,
                get_records_fn=lambda: self.db.get_recent_records(120),
                on_update_record_fn=self.db.update_record_label
            ),
            "exporter": ExportView(
                self.content_container,
                on_export=lambda fmt: self.exporter.export_incremental(fmt=fmt),
                get_export_stats=lambda: {
                    "total_records": self.db.count_records(),
                    "unexported_records": len(self.db.get_unexported_records())
                }
            )
        }

        self._select_tab("dashboard")

    def _select_tab(self, tab_key: str):
        for key, btn in self.nav_buttons.items():
            if key == tab_key:
                btn.configure(fg_color="#334155")
            else:
                btn.configure(fg_color="transparent")

        for key, view in self.views.items():
            if key == tab_key:
                view.pack(fill="both", expand=True)
                if key == "timeline":
                    view.refresh_data()
            else:
                view.pack_forget()

    def _toggle_recording(self):
        if self.engine.is_paused:
            self.engine.resume()
            self.tray.set_recording_state(True)
            self.views["dashboard"].toggle_btn.configure(text="Pause Telemetry", fg_color="#F59E0B", hover_color="#D97706")
            self.views["dashboard"].status_indicator.configure(text="● RECORDING ACTIVE (5s Interval)", text_color="#10B981")
        else:
            self.engine.pause()
            self.tray.set_recording_state(False)
            self.views["dashboard"].toggle_btn.configure(text="Resume Telemetry", fg_color="#10B981", hover_color="#059669")
            self.views["dashboard"].status_indicator.configure(text="❚❚ TELEMETRY PAUSED", text_color="#F59E0B")

    def _trigger_sample(self):
        pass

    def _refresh_telemetry_loop(self):
        if hasattr(self, "views") and "dashboard" in self.views:
            stats = self.engine.get_current_stats()
            latest = stats.get("latest_record")
            if latest:
                state_dict = {
                    "current_app": latest.get("app_name", "Idle"),
                    "window_title": latest.get("window_title_sanitized", ""),
                    "current_cognitive_state": latest.get("cognitive_state", "UNCLASSIFIED"),
                    "current_domain": latest.get("domain_label", "Unlabeled"),
                    "confidence": latest.get("confidence", 0.0),
                    "finalized_value": latest.get("finalized_value", 0),
                    "active_states": latest.get("active_states", {}),
                    "keystrokes_per_min": latest.get("keystrokes_per_min", 0.0),
                    "mouse_velocity": latest.get("mouse_velocity_avg", 0.0),
                    "is_audio_playing": latest.get("is_audio_playing", False),
                    "system_idle_seconds": latest.get("system_idle_seconds", 0.0)
                }
                self.views["dashboard"].update_telemetry(state_dict)

        # Repeat every 2500ms
        self.after(2500, self._refresh_telemetry_loop)

    def _minimize_to_tray(self):
        self.withdraw()

    def _restore_from_tray(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _clean_exit(self):
        self.engine.stop()
        self.tray.stop()
        self.db.close()
        self.destroy()
        sys.exit(0)

def create_app(db_path: str = "datacollector.db") -> DataCollectorApp:
    return DataCollectorApp(db_path=db_path)
