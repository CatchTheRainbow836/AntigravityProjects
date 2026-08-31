"""
Active Learning Pop-up Modal Dialog.
Prompts the user to confirm or reassign their current activity during low-confidence intervals
or significant context transitions.
"""

import customtkinter as ctk
from typing import Callable, List, Optional

class PromptModal(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        detected_app: str,
        predicted_state: str,
        predicted_domain: str,
        confidence: float,
        on_submit_label: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.detected_app = detected_app
        self.predicted_state = predicted_state
        self.predicted_domain = predicted_domain
        self.confidence = confidence
        self.on_submit_label = on_submit_label

        self.title("Activity Check — AI Task Scheduler")
        self.geometry("460x360")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0F172A")

        self._build_ui()

    def _build_ui(self):
        # Heading
        header = ctk.CTkLabel(
            self,
            text="What activity are you working on?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F8FAFC"
        )
        header.pack(anchor="w", padx=24, pady=(20, 4))

        sub = ctk.CTkLabel(
            self,
            text=f"App: {self.detected_app[:35]} (Estimated: {self.predicted_state} • {int(self.confidence*100)}% conf)",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        )
        sub.pack(anchor="w", padx=24, pady=(0, 16))

        # Quick preset buttons
        presets_label = ctk.CTkLabel(self, text="Quick Select Subject Preset:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        presets_label.pack(anchor="w", padx=24, pady=(0, 6))

        btn_grid = ctk.CTkFrame(self, fg_color="transparent")
        btn_grid.pack(fill="x", padx=24, pady=(0, 14))
        btn_grid.grid_columnconfigure((0, 1), weight=1)

        presets = [
            ("Coding / Dev", "Coding", "Software Development"),
            ("Specialist Math", "Writing", "Specialist Mathematics"),
            ("Physics Study", "Writing", "Physics"),
            ("Research / Reading", "Research", "General Research"),
        ]

        for idx, (label_text, cog_state, dom_label) in enumerate(presets):
            row = idx // 2
            col = idx % 2
            btn = ctk.CTkButton(
                btn_grid,
                text=label_text,
                font=ctk.CTkFont(size=12),
                fg_color="#1E293B",
                hover_color="#334155",
                text_color="#E2E8F0",
                height=32,
                command=lambda cs=cog_state, dl=dom_label: self._confirm(cs, dl)
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        # Custom text input option
        custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        custom_frame.pack(fill="x", padx=24, pady=(6, 20))

        self.custom_input = ctk.CTkEntry(
            custom_frame,
            placeholder_text="Or type custom activity...",
            fg_color="#1E293B",
            text_color="#F8FAFC",
            height=34
        )
        self.custom_input.pack(side="left", fill="x", expand=True, padx=(0, 8))

        submit_btn = ctk.CTkButton(
            custom_frame,
            text="Save",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=70,
            height=34,
            command=self._submit_custom
        )
        submit_btn.pack(side="right")

    def _confirm(self, cog_state: str, dom_label: str):
        self.on_submit_label(dom_label, cog_state)
        self.destroy()

    def _submit_custom(self):
        custom_text = self.custom_input.get().strip()
        if custom_text:
            self.on_submit_label(custom_text, "USER_CUSTOM")
        else:
            self.on_submit_label(self.predicted_domain, self.predicted_state)
        self.destroy()
