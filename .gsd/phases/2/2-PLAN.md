---
phase: 2
plan: 2
wave: 2
depends_on:
  - 2.1
---

# Plan 2.2: Telemetry Aggregator Engine & Storage Pipeline Integration

## Objective
Combine all sensor streams into synchronized 5-second aggregation windows, validate against schema, and pipeline data directly into local SQLite storage with background worker thread management.

## Context
- .gsd/phases/2/1-PLAN.md
- TaskScheduler/DataCollector/src/db_manager.py
- TaskScheduler/DataCollector/src/schema.json

## Tasks

<task type="auto">
  <name>Build TelemetryAggregator and background recording loop</name>
  <files>
    TaskScheduler/DataCollector/src/engine.py
  </files>
  <action>
    Create TelemetryEngine that orchestrates all collectors, slices time into configurable 5-second windows, validates each record against schema, and writes directly to DatabaseManager.
    Support start(), pause(), stop(), and get_current_stats() for UI binding.
  </action>
  <verify>python3 -c "import sys, time; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from engine import TelemetryEngine; from db_manager import DatabaseManager; db = DatabaseManager(':memory:'); engine = TelemetryEngine(db=db, sample_interval=0.5); engine.start(); time.sleep(1.2); engine.stop(); assert db.count_records() >= 2; print('Engine verified!')"</verify>
  <done>TelemetryEngine aggregates all collector outputs and successfully flushes records to SQLite database.</done>
</task>

<task type="auto">
  <name>Create automated sensor and aggregation test suite</name>
  <files>
    TaskScheduler/DataCollector/tests/test_collectors.py
    TaskScheduler/DataCollector/tests/test_engine.py
  </files>
  <action>
    Implement unit and integration tests verifying sensor sampling rate, idle calculations, window sanitization logic, and engine recording lifecycle.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_*.py"</verify>
  <done>All collector and engine tests pass with 100% success rate.</done>
</task>

## Success Criteria
- [ ] Telemetry engine running continuously with background SQLite storage.
- [ ] Full automated test suite passing.
