"""
Timeline Visualizer & Retrospective Editor View.
Integrates the dynamic canvas with zoom presets, duration breakdowns, and retrospective tag reassignment.
"""

import customtkinter as ctk
from datetime import datetime, timezone
from typing import Callable, List, Dict, Any

from ui.components.timeline_canvas import TimelineCanvas

class TimelineView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        get_records_fn: Callable[[], List[Dict[str, Any]]],
        on_update_record_fn: Callable[[int, str, str], None],
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.get_records_fn = get_records_fn
        self.on_update_record_fn = on_update_record_fn

        self._build_ui()

    def _build_ui(self):
        self.configure(fg_color="transparent")

        # Top Control Card
        control_card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12)
        control_card.pack(fill="x", pady=(0, 14), padx=8)

        title = ctk.CTkLabel(
            control_card,
            text="Dynamic Activity Timeline Visualizer",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(side="left", padx=20, pady=16)

        # Zoom Segmented Buttons
        zoom_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        zoom_frame.pack(side="right", padx=20, pady=16)

        ctk.CTkLabel(zoom_frame, text="Time Zoom:", font=ctk.CTkFont(size=12), text_color="#94A3B8").pack(side="left", padx=(0, 8))
        self.zoom_btn = ctk.CTkSegmentedButton(
            zoom_frame,
            values=["1h", "4h", "12h", "24h"],
            command=self._on_zoom_change
        )
        self.zoom_btn.pack(side="left", padx=(0, 12))
        self.zoom_btn.set("4h")

        refresh_btn = ctk.CTkButton(
            zoom_frame,
            text="↻ Refresh",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            width=80,
            command=self.refresh_data
        )
        refresh_btn.pack(side="left")

        # Middle Canvas Card
        canvas_card = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=12)
        canvas_card.pack(fill="both", expand=True, padx=8, pady=(0, 14))

        self.canvas = TimelineCanvas(canvas_card, on_block_clicked=self._on_block_clicked, height=220)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=12)

        # Bottom Retrospective Editor Card
        self.edit_card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12)
        self.edit_card.pack(fill="x", padx=8, pady=0)

        self.edit_title = ctk.CTkLabel(
            self.edit_card,
            text="RETROSPECTIVE TAG EDITOR (Click any timeline block above to edit)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94A3B8"
        )
        self.edit_title.pack(anchor="w", padx=20, pady=(12, 6))

        self.edit_controls = ctk.CTkFrame(self.edit_card, fg_color="transparent")
        self.edit_controls.pack(fill="x", padx=20, pady=(0, 14))

        self.selected_info = ctk.CTkLabel(
            self.edit_controls,
            text="No block selected.",
            font=ctk.CTkFont(size=13),
            text_color="#CBD5E1"
        )
        self.selected_info.pack(side="left", padx=(0, 16))

        self.tag_menu = ctk.CTkOptionMenu(
            self.edit_controls,
            values=["Software Development", "Specialist Mathematics", "Mathematical Methods", "Physics", "Chemistry", "English & Humanities", "Gaming", "Idle"],
            fg_color="#334155",
            button_color="#475569",
            text_color="#FFFFFF"
        )
        self.tag_menu.pack(side="left", padx=(0, 10))

        self.apply_btn = ctk.CTkButton(
            self.edit_controls,
            text="Apply Label",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            width=100,
            command=self._apply_tag
        )
        self.apply_btn.pack(side="left")

        self.active_segment = None

    def _on_zoom_change(self, value):
        hours = {"1h": 1.0, "4h": 4.0, "12h": 12.0, "24h": 24.0}.get(value, 4.0)
        self.canvas.set_zoom(hours)

    def refresh_data(self):
        records = self.get_records_fn()
        self.canvas.set_data(records)

    def _on_block_clicked(self, segment: Dict[str, Any]):
        self.active_segment = segment
        time_str = f"{segment['start'].strftime('%H:%M')} - {segment['end'].strftime('%H:%M')}"
        self.selected_info.configure(text=f"Selected: {segment['domain']} ({time_str})")
        if segment["domain"] in self.tag_menu.cget("values"):
            self.tag_menu.set(segment["domain"])

    def _apply_tag(self):
        if not self.active_segment:
            return
        new_tag = self.tag_menu.get()
        ids = self.active_segment.get("ids", [])
        for rec_id in ids:
            self.on_update_record_fn(rec_id, new_tag, self.active_segment.get("state", "Coding"))
        self.selected_info.configure(text=f"✓ Updated {len(ids)} records to '{new_tag}'")
        self.refresh_data()
