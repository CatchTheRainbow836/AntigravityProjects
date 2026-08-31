"""
Live Telemetry Dashboard View.
Displays real-time sensor metrics, multi-state activity indicators, confidence percentages, and session controls.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable

class DashboardView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_toggle_recording: Callable[[], None],
        on_trigger_sample: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.on_toggle_recording = on_toggle_recording
        self.on_trigger_sample = on_trigger_sample

        self._build_ui()

    def _build_ui(self):
        self.configure(fg_color="transparent")

        # Top Bar: Status Banner & Controls
        top_card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12)
        top_card.pack(fill="x", pady=(0, 16), padx=8)

        self.status_indicator = ctk.CTkLabel(
            top_card,
            text="● RECORDING ACTIVE (5s Interval)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#10B981"
        )
        self.status_indicator.pack(side="left", padx=20, pady=16)

        self.toggle_btn = ctk.CTkButton(
            top_card,
            text="Pause Telemetry",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="#FFFFFF",
            width=140,
            height=34,
            command=self.on_toggle_recording
        )
        self.toggle_btn.pack(side="right", padx=20, pady=16)

        # Middle Grid: Telemetry Metrics Cards
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 16), padx=8)
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Active App & Window
        card1 = ctk.CTkFrame(grid_frame, fg_color="#1E293B", corner_radius=10)
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        ctk.CTkLabel(card1, text="ACTIVE APPLICATION", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=16, pady=(14, 4))
        self.app_label = ctk.CTkLabel(card1, text="Visual Studio Code", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC")
        self.app_label.pack(anchor="w", padx=16, pady=(0, 2))
        self.title_label = ctk.CTkLabel(card1, text="classifier.py - DataCollector", font=ctk.CTkFont(size=12), text_color="#64748B")
        self.title_label.pack(anchor="w", padx=16, pady=(0, 14))

        # Card 2: Primary State & Confidence
        card2 = ctk.CTkFrame(grid_frame, fg_color="#1E293B", corner_radius=10)
        card2.grid(row=0, column=1, sticky="nsew", padx=4, pady=0)
        ctk.CTkLabel(card2, text="CLASSIFIED STATE & CONFIDENCE", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=16, pady=(14, 4))
        self.state_label = ctk.CTkLabel(card2, text="Coding (Finalized: 1)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#38BDF8")
        self.state_label.pack(anchor="w", padx=16, pady=(0, 2))
        self.conf_bar = ctk.CTkProgressBar(card2, height=8, fg_color="#334155", progress_color="#38BDF8")
        self.conf_bar.pack(fill="x", padx=16, pady=(4, 6))
        self.conf_bar.set(0.95)
        self.conf_text = ctk.CTkLabel(card2, text="Confidence: 95% (Threshold >= 75%)", font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.conf_text.pack(anchor="w", padx=16, pady=(0, 10))

        # Card 3: Interaction Kinetics & Audio
        card3 = ctk.CTkFrame(grid_frame, fg_color="#1E293B", corner_radius=10)
        card3.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=0)
        ctk.CTkLabel(card3, text="INTERACTION KINETICS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=16, pady=(14, 4))
        self.kinetics_label = ctk.CTkLabel(card3, text="Keys: 120/min | Mouse: 85 px/s", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC")
        self.kinetics_label.pack(anchor="w", padx=16, pady=(0, 2))
        self.audio_badge = ctk.CTkLabel(card3, text="Audio: Active 🔊 | Idle: 0s", font=ctk.CTkFont(size=12), text_color="#A855F7")
        self.audio_badge.pack(anchor="w", padx=16, pady=(0, 14))

        # Bottom Card: Concurrent Multi-States
        multi_card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12)
        multi_card.pack(fill="both", expand=True, pady=0, padx=8)

        ctk.CTkLabel(
            multi_card,
            text="CONCURRENT MULTI-STATE RECOGNITION (MULTI-SCREEN & AUDIO CONTEXT)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(16, 8))

        self.multi_states_container = ctk.CTkFrame(multi_card, fg_color="transparent")
        self.multi_states_container.pack(fill="x", padx=20, pady=(0, 16))

        # Initial badge labels
        self.state_badges = {}
        for state_name in ["Coding", "Research", "Music", "Communication", "Writing", "Mathematics", "Physics", "Gaming"]:
            badge = ctk.CTkLabel(
                self.multi_states_container,
                text=f"{state_name}: Active (1)",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#334155",
                text_color="#94A3B8",
                corner_radius=6,
                padx=10,
                pady=6
            )
            badge.pack(side="left", padx=4, pady=4)
            self.state_badges[state_name] = badge

    def update_telemetry(self, state: Dict[str, Any]):
        app = state.get("current_app", "Idle")
        title = state.get("window_title", "")
        self.app_label.configure(text=app[:30])
        self.title_label.configure(text=title[:45] if title else "Active Window")

        cog_state = state.get("current_cognitive_state", "UNCLASSIFIED")
        conf = float(state.get("confidence", 0.0))
        finalized = int(state.get("finalized_value", 1 if conf >= 0.75 else 0))

        self.state_label.configure(text=f"{cog_state} (Finalized: {finalized})")
        self.conf_bar.set(min(1.0, max(0.0, conf)))
        self.conf_text.configure(text=f"Confidence: {int(conf * 100)}% (Threshold >= 75%)")

        kpm = state.get("keystrokes_per_min", 0.0)
        mouse = state.get("mouse_velocity", 0.0)
        self.kinetics_label.configure(text=f"Keys: {int(kpm)}/min | Mouse: {int(mouse)} px/s")

        audio = "Active 🔊" if state.get("is_audio_playing", False) else "Silent 🔇"
        idle = state.get("system_idle_seconds", 0.0)
        self.audio_badge.configure(text=f"Audio: {audio} | Idle: {int(idle)}s")

        # Update multi-state badges
        active_states = state.get("active_states", {})
        for name, badge in self.state_badges.items():
            is_active = active_states.get(name, 0) == 1
            if is_active:
                badge.configure(
                    fg_color="#065F46" if name in ["Coding", "Writing", "Mathematics", "Physics"] else "#4C1D95",
                    text_color="#6EE7B7" if name in ["Coding", "Writing", "Mathematics", "Physics"] else "#C4B5FD",
                    text=f"{name}: Active (1)"
                )
            else:
                badge.configure(
                    fg_color="#1E293B",
                    text_color="#475569",
                    text=f"{name}: Inactive (0)"
                )
