---
phase: 5
plan: 1
wave: 1
---

# Plan 5.1: Incremental Deduplicated Dataset Exporter

## Objective
Implement local-only incremental dataset export utilities supporting JSONL, CSV, and tabular dumps with cryptographic hash integrity and SQLite export tracking to prevent duplicate records.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- TaskScheduler/DataCollector/src/db_manager.py
- TaskScheduler/DataCollector/src/types.ts

## Tasks

<task type="auto">
  <name>Build DatasetExporter with deduplication tracking</name>
  <files>
    TaskScheduler/DataCollector/src/exporter.py
  </files>
  <action>
    Create DatasetExporter:
    1. Queries only unexported records (`is_exported = 0`) from SQLite.
    2. Writes local files in JSONL and CSV formats to TaskScheduler/DataCollector/exports/.
    3. Calculates SHA256 content hash and logs the batch to `export_history`.
    4. Marks exported records (`is_exported = 1`) atomically.
    5. Supports exporting all records or incremental new records since last export.
  </action>
  <verify>python3 -c "import sys, tempfile, os; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from exporter import DatasetExporter; from db_manager import DatabaseManager; from simulator import generate_sample_session; tf = tempfile.NamedTemporaryFile(suffix='.db', delete=False); tf.close(); db = DatabaseManager(tf.name); db.insert_batch(generate_sample_session(10)); exp_dir = tempfile.mkdtemp(); exp = DatasetExporter(db, export_dir=exp_dir); m1 = exp.export_incremental(fmt='jsonl'); assert m1['record_count'] == 10; m2 = exp.export_incremental(fmt='jsonl'); assert m2['record_count'] == 0; os.remove(tf.name); print('Exporter verified!')"</verify>
  <done>DatasetExporter exports clean JSONL/CSV records and ensures subsequent incremental runs output 0 duplicate records.</done>
</task>

## Success Criteria
- [ ] Local-only dataset export functional across CSV and JSONL formats.
- [ ] Deduplication tracking strictly verified.
