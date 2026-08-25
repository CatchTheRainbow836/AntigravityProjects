"""
Retrospective Timeline Manager for DataCollector.
Groups granular time-slice records into continuous behavior blocks, renders timeline data models, and allows retroactive label edits.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from db_manager import DatabaseManager

class RetrospectiveTimeline:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_timeline_blocks(self, limit_hours: float = 24.0) -> List[Dict[str, Any]]:
        """
        Fetches recent telemetry records and merges consecutive records with matching
        app/cognitive/domain labels into continuous visual blocks.
        """
        records = self.db.get_unexported_records()
        if not records:
            return []

        blocks = []
        current_block: Optional[Dict[str, Any]] = None

        for r in records:
            app = r["app_name"]
            state = r["cognitive_state"]
            domain = r["domain_label"]
            timestamp = r["timestamp"]
            record_id = r["id"]

            if current_block is None:
                current_block = {
                    "id": len(blocks) + 1,
                    "start_time": timestamp,
                    "end_time": timestamp,
                    "app_name": app,
                    "cognitive_state": state,
                    "domain_label": domain,
                    "confidence_avg": r["confidence"],
                    "record_ids": [record_id],
                    "sample_count": 1,
                    "duration_seconds": r["duration_seconds"]
                }
            else:
                # Same activity segment if app and cognitive state match
                same_activity = (
                    current_block["app_name"] == app and
                    current_block["cognitive_state"] == state and
                    current_block["domain_label"] == domain
                )

                if same_activity:
                    current_block["end_time"] = timestamp
                    current_block["record_ids"].append(record_id)
                    current_block["sample_count"] += 1
                    current_block["duration_seconds"] += r["duration_seconds"]
                    current_block["confidence_avg"] = round(
                        (current_block["confidence_avg"] * (current_block["sample_count"] - 1) + r["confidence"]) / current_block["sample_count"],
                        2
                    )
                else:
                    current_block["duration_minutes"] = round(current_block["duration_seconds"] / 60.0, 1)
                    blocks.append(current_block)
                    current_block = {
                        "id": len(blocks) + 1,
                        "start_time": timestamp,
                        "end_time": timestamp,
                        "app_name": app,
                        "cognitive_state": state,
                        "domain_label": domain,
                        "confidence_avg": r["confidence"],
                        "record_ids": [record_id],
                        "sample_count": 1,
                        "duration_seconds": r["duration_seconds"]
                    }

        if current_block:
            current_block["duration_minutes"] = round(current_block["duration_seconds"] / 60.0, 1)
            blocks.append(current_block)

        return blocks

    def update_block_label(
        self,
        record_ids: List[int],
        new_domain_label: str,
        new_cognitive_state: Optional[str] = None
    ) -> int:
        if not record_ids:
            return 0

        placeholders = ",".join("?" for _ in record_ids)
        params = [new_domain_label, 1.0, "RETROSPECTIVE_EDIT"]
        query = f"""
        UPDATE telemetry_records
        SET domain_label = ?, confidence = ?, label_source = ?
        """
        if new_cognitive_state:
            query += f", cognitive_state = ?"
            params.append(new_cognitive_state)

        query += f" WHERE id IN ({placeholders})"
        params.extend(record_ids)

        with self.db._lock:
            self.db.conn.execute(query, params)
            self.db.conn.commit()

        return len(record_ids)
