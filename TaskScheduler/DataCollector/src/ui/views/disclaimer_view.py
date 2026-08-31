"""
First-Run Disclaimer & Privacy Consent View.
"""

import customtkinter as ctk
from typing import Callable

class DisclaimerView(ctk.CTkFrame):
    def __init__(self, master, on_agree: Callable[[], None], on_decline: Callable[[], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_agree = on_agree
        self.on_decline = on_decline

        self._build_ui()

    def _build_ui(self):
        self.configure(fg_color="#0F172A", corner_radius=12)

        # Header Title
        title = ctk.CTkLabel(
            self,
            text="Privacy Policy & Telemetry Consent",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(pady=(24, 12), padx=24, anchor="w")

        subtitle = ctk.CTkLabel(
            self,
            text="AI Task Scheduler — Local Behavior Data Collector",
            font=ctk.CTkFont(size=14),
            text_color="#94A3B8"
        )
        subtitle.pack(pady=(0, 16), padx=24, anchor="w")

        # Scrollable terms textbox
        textbox = ctk.CTkTextbox(
            self,
            height=260,
            font=ctk.CTkFont(size=13),
            fg_color="#1E293B",
            text_color="#E2E8F0",
            corner_radius=8
        )
        textbox.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        disclaimer_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "   DATA PRIVACY & LOCAL RECORDING COMMITMENT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "1. PRIVACY & SECURITY FIRST:\n"
            "   • All recorded telemetry data is stored STRICTLY LOCALLY on your computer.\n"
            "   • No raw keystroke content or passwords are ever captured or logged.\n"
            "   • No audio recordings or video screen streams are ever captured.\n\n"
            "2. WHAT METRICS ARE COLLECTED:\n"
            "   • Interaction kinetics: Aggregate keystroke rates (keys/min), mouse velocities, click frequencies.\n"
            "   • Window context: Active application name, sanitized window titles (emails/tokens redacted), and screen bounds.\n"
            "   • System states: Idle duration, active audio output state (presence of playback/recording).\n\n"
            "3. AUTONOMOUS TASK SCHEDULING PURPOSE:\n"
            "   • This data is used solely to classify cognitive work blocks (e.g. Coding, Math, Physics, Writing)\n"
            "     for training your personalized AI homework and task scheduler.\n"
            "   • You maintain 100% control to pause, inspect, retrospective edit, or export your dataset at any time.\n\n"
            "By clicking 'Agree & Grant Consent', you confirm that you understand and agree to local behavior data collection."
        )
        textbox.insert("0.0", disclaimer_text)
        textbox.configure(state="disabled")

        # Button row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 24))

        agree_btn = ctk.CTkButton(
            btn_frame,
            text="Agree & Grant Consent",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            height=40,
            command=self.on_agree
        )
        agree_btn.pack(side="right", padx=(12, 0))

        decline_btn = ctk.CTkButton(
            btn_frame,
            text="Decline & Exit",
            font=ctk.CTkFont(size=14),
            fg_color="#475569",
            hover_color="#334155",
            text_color="#E2E8F0",
            height=40,
            command=self.on_decline
        )
        decline_btn.pack(side="right")
