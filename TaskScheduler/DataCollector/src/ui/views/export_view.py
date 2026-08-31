"""
Dataset Export View.
Provides UI controls to trigger incremental/full dataset exports in JSONL/CSV/Parquet formats.
"""

import customtkinter as ctk
import os
from typing import Callable, Dict, Any, List

class ExportView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_export: Callable[[str], Dict[str, Any]],
        get_export_stats: Callable[[], Dict[str, Any]],
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.on_export = on_export
        self.get_export_stats = get_export_stats

        self._build_ui()

    def _build_ui(self):
        self.configure(fg_color="transparent")

        # Top Export Controls Card
        card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12)
        card.pack(fill="x", pady=(0, 16), padx=8)

        title = ctk.CTkLabel(
            card,
            text="Incremental Dataset Exporter",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(anchor="w", padx=20, pady=(16, 4))

        desc = ctk.CTkLabel(
            card,
            text="Export locally recorded multi-signal telemetry into clean ML-ready formats (JSONL, CSV) with cryptographic deduplication.",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        desc.pack(anchor="w", padx=20, pady=(0, 16))

        # Format picker & action
        controls_frame = ctk.CTkFrame(card, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(controls_frame, text="Format:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#E2E8F0").pack(side="left", padx=(0, 10))
        self.format_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["jsonl", "csv"],
            fg_color="#334155",
            button_color="#475569",
            text_color="#FFFFFF"
        )
        self.format_menu.pack(side="left", padx=(0, 20))

        self.export_btn = ctk.CTkButton(
            controls_frame,
            text="Export New Records Now",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._handle_export
        )
        self.export_btn.pack(side="left")

        self.status_msg = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#10B981"
        )
        self.status_msg.pack(anchor="w", padx=20, pady=(0, 16))

        # Bottom Results Log
        log_card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12)
        log_card.pack(fill="both", expand=True, padx=8, pady=0)

        ctk.CTkLabel(
            log_card,
            text="EXPORT LOG & MANIFEST",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(16, 8))

        self.log_textbox = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="monospace", size=12),
            fg_color="#0F172A",
            text_color="#CBD5E1",
            corner_radius=8
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Refresh initial stats
        stats = self.get_export_stats()
        self.log_textbox.insert("end", f"Total records in local SQLite: {stats.get('total_records', 0)}\n")
        self.log_textbox.insert("end", f"Unexported records awaiting export: {stats.get('unexported_records', 0)}\n")

    def _handle_export(self):
        fmt = self.format_menu.get()
        res = self.on_export(fmt)
        if res.get("record_count", 0) > 0:
            msg = f"✓ Exported {res['record_count']} records to {res['file_path']} (SHA256: {res['content_hash'][:12]}...)"
            self.status_msg.configure(text=msg, text_color="#10B981")
            self.log_textbox.insert("end", f"\n[EXPORT SUCCESS] {res['exported_at']}\n")
            self.log_textbox.insert("end", f"  File: {res['file_path']}\n")
            self.log_textbox.insert("end", f"  Records: {res['record_count']} | Hash: {res['content_hash']}\n")
        else:
            self.status_msg.configure(text=res.get("message", "No new records to export."), text_color="#F59E0B")
            self.log_textbox.insert("end", f"\n[EXPORT] {res.get('message', 'No new records to export.')}\n")
