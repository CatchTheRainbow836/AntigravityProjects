"""
Dynamic Interactive Timeline Canvas Widget.
Renders continuous colored horizontal activity bars across time intervals,
supporting zoom levels, multi-state layering, and interactive click-to-edit.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Callable

STATE_COLORS = {
    "Coding": "#06B6D4",        # Cyan
    "ACTIVE_CODING": "#06B6D4",
    "Writing": "#3B82F6",       # Blue
    "DEEP_FOCUS_WRITING": "#3B82F6",
    "Research": "#8B5CF6",      # Purple
    "RESEARCH_READING": "#8B5CF6",
    "Mathematics": "#EC4899",   # Pink
    "Specialist Mathematics": "#EC4899",
    "Mathematical Methods": "#F43F5E",
    "Physics": "#6366F1",       # Indigo
    "Music": "#F59E0B",         # Amber
    "MEDIA_CONSUMPTION": "#F59E0B",
    "Communication": "#10B981", # Green
    "Gaming": "#EF4444",        # Red
    "HIGH_INTERACTION_GAMING": "#EF4444",
    "Idle": "#475569",          # Slate
    "IDLE_AWAY": "#475569",
    "UNCLASSIFIED": "#334155"   # Dark slate
}

class TimelineCanvas(tk.Canvas):
    def __init__(
        self,
        master,
        on_block_clicked: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ):
        kwargs.setdefault("bg", "#0F172A")
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)

        self.on_block_clicked = on_block_clicked
        self.segments: List[Dict[str, Any]] = []
        self.zoom_hours = 4.0 # default zoom span: 4 hours
        self.reference_time = datetime.now(timezone.utc)

        self._tooltip = None
        self._block_hitboxes = []

        self.bind("<Configure>", self._on_resize)
        self.bind("<Motion>", self._on_hover)
        self.bind("<Button-1>", self._on_click)

    def set_zoom(self, hours: float):
        self.zoom_hours = hours
        self.redraw()

    def set_data(self, records: List[Dict[str, Any]]):
        """Aggregate telemetry records into contiguous behavior blocks."""
        if not records:
            self.segments = []
            self.redraw()
            return

        # Sort chronological
        sorted_recs = sorted(records, key=lambda r: r.get("timestamp", ""))
        self.segments = self._aggregate_to_segments(sorted_recs)
        if sorted_recs:
            try:
                self.reference_time = datetime.fromisoformat(sorted_recs[-1]["timestamp"].replace("Z", "+00:00"))
            except Exception:
                self.reference_time = datetime.now(timezone.utc)
        self.redraw()

    def _aggregate_to_segments(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        segments = []
        if not records:
            return segments

        current_seg = None

        for r in records:
            try:
                t = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            except Exception:
                continue

            state = r.get("cognitive_state", "UNCLASSIFIED")
            domain = r.get("domain_label", "Unlabeled")
            conf = float(r.get("confidence", 0.0))
            finalized = int(r.get("finalized_value", 1 if conf >= 0.75 else 0))
            app = r.get("app_name", "")
            rec_id = r.get("id", 0)

            if current_seg is None:
                current_seg = {
                    "start": t,
                    "end": t + timedelta(seconds=5),
                    "state": state,
                    "domain": domain,
                    "confidence": conf,
                    "finalized_value": finalized,
                    "app": app,
                    "ids": [rec_id]
                }
            else:
                # Merge if same state/domain within 15 seconds
                time_gap = (t - current_seg["end"]).total_seconds()
                if current_seg["state"] == state and current_seg["domain"] == domain and time_gap <= 15:
                    current_seg["end"] = t + timedelta(seconds=5)
                    current_seg["ids"].append(rec_id)
                    current_seg["confidence"] = (current_seg["confidence"] + conf) / 2.0
                else:
                    segments.append(current_seg)
                    current_seg = {
                        "start": t,
                        "end": t + timedelta(seconds=5),
                        "state": state,
                        "domain": domain,
                        "confidence": conf,
                        "finalized_value": finalized,
                        "app": app,
                        "ids": [rec_id]
                    }

        if current_seg:
            segments.append(current_seg)

        return segments

    def _on_resize(self, event):
        self.redraw()

    def redraw(self):
        self.delete("all")
        self._block_hitboxes = []

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 50 or height < 50:
            return

        margin_left = 60
        margin_right = 30
        track_y = 60
        track_height = 48

        # Draw Time Axis Background Track
        track_width = width - margin_left - margin_right
        self.create_rectangle(
            margin_left, track_y, margin_left + track_width, track_y + track_height,
            fill="#1E293B", outline="#334155", width=1
        )

        # Time range window
        end_time = self.reference_time
        start_time = end_time - timedelta(hours=self.zoom_hours)
        total_seconds = max(1.0, (end_time - start_time).total_seconds())

        # Draw Time Labels & Ticks
        num_ticks = 6
        for i in range(num_ticks + 1):
            tick_ratio = i / num_ticks
            tick_x = margin_left + (tick_ratio * track_width)
            tick_time = start_time + timedelta(seconds=tick_ratio * total_seconds)
            time_str = tick_time.strftime("%H:%M")

            self.create_line(tick_x, track_y + track_height, tick_x, track_y + track_height + 8, fill="#64748B")
            self.create_text(tick_x, track_y + track_height + 18, text=time_str, fill="#94A3B8", font=("Helvetica", 9))

        # Render Activity Bars
        for seg in self.segments:
            seg_start = seg["start"]
            seg_end = seg["end"]

            # Filter out segments outside view window
            if seg_end < start_time or seg_start > end_time:
                continue

            visible_start = max(start_time, seg_start)
            visible_end = min(end_time, seg_end)

            start_ratio = (visible_start - start_time).total_seconds() / total_seconds
            end_ratio = (visible_end - start_time).total_seconds() / total_seconds

            x1 = margin_left + (start_ratio * track_width)
            x2 = max(x1 + 4, margin_left + (end_ratio * track_width)) # Min width 4px

            color = STATE_COLORS.get(seg["domain"], STATE_COLORS.get(seg["state"], "#38BDF8"))

            # Draw block
            block_id = self.create_rectangle(
                x1, track_y + 4, x2, track_y + track_height - 4,
                fill=color, outline="#0F172A", width=1
            )

            # Draw label inside block if wide enough
            if (x2 - x1) > 55:
                label = seg["domain"] if seg["domain"] != "Unlabeled" else seg["state"]
                self.create_text(
                    (x1 + x2) / 2, track_y + (track_height / 2),
                    text=label[:14], fill="#FFFFFF", font=("Helvetica", 9, "bold")
                )

            # Store hitbox for tooltips & clicks
            self._block_hitboxes.append({
                "bbox": (x1, track_y + 4, x2, track_y + track_height - 4),
                "segment": seg
            })

    def _on_hover(self, event):
        hit = None
        for item in self._block_hitboxes:
            x1, y1, x2, y2 = item["bbox"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                hit = item["segment"]
                break

        if hit:
            dur = int((hit["end"] - hit["start"]).total_seconds() / 60)
            time_str = f"{hit['start'].strftime('%H:%M')} - {hit['end'].strftime('%H:%M')} ({dur} min)"
            conf_str = f"{int(hit['confidence'] * 100)}% (Finalized: {hit['finalized_value']})"
            tooltip_text = f"Activity: {hit['domain']} | {hit['state']}\nDuration: {time_str}\nApp: {hit['app']}\nConfidence: {conf_str}\n[Click block to edit label]"

            self.delete("tooltip")
            # Draw sleek floating tooltip
            tx = min(self.winfo_width() - 200, max(20, event.x))
            ty = 130
            self.create_rectangle(tx - 6, ty - 6, tx + 240, ty + 70, fill="#1E293B", outline="#475569", tags="tooltip")
            self.create_text(tx + 8, ty + 30, text=tooltip_text, fill="#E2E8F0", font=("Helvetica", 9), anchor="w", tags="tooltip")
        else:
            self.delete("tooltip")

    def _on_click(self, event):
        for item in self._block_hitboxes:
            x1, y1, x2, y2 = item["bbox"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if self.on_block_clicked:
                    self.on_block_clicked(item["segment"])
                break
