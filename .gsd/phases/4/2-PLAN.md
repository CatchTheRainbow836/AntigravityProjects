---
phase: 4
plan: 2
wave: 2
depends_on:
  - 4.1
---

# Plan 4.2: Modern Desktop Dashboard & Retrospective Timeline Editor

## Objective
Implement the UI presentation layer featuring live telemetry metrics, classification indicators, recording controls, interactive retrospective timeline editor, and active learning prompt dialog.

## Context
- .gsd/phases/4/1-PLAN.md
- TaskScheduler/DataCollector/src/engine.py
- TaskScheduler/DataCollector/src/active_learning.py

## Tasks

<task type="auto">
  <name>Build DashboardPresenter and RetrospectiveTimeline</name>
  <files>
    TaskScheduler/DataCollector/src/ui/dashboard.py
    TaskScheduler/DataCollector/src/ui/timeline.py
  </files>
  <action>
    Implement:
    1. DashboardPresenter: binds to TelemetryEngine, formats real-time metrics (KPM, velocity, app name, state badge, confidence).
    2. RetrospectiveTimeline: aggregates consecutive time-slice records into continuous behavior blocks, provides timeline view model, and handles click-to-edit label reassignment.
    3. Active learning popup dialog model for 1-click subject selection.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from ui.dashboard import DashboardPresenter; from ui.timeline import RetrospectiveTimeline; from db_manager import DatabaseManager; from simulator import generate_sample_session; db = DatabaseManager(':memory:'); db.insert_batch(generate_sample_session(20)); tl = RetrospectiveTimeline(db); blocks = tl.get_timeline_blocks(); assert len(blocks) > 0; print('Dashboard and timeline verified!')"</verify>
  <done>DashboardPresenter and RetrospectiveTimeline format telemetry data and allow timeline reassignment.</done>
</task>

<task type="auto">
  <name>Create automated test suite for UI and timeline presentation</name>
  <files>
    TaskScheduler/DataCollector/tests/test_ui.py
  </files>
  <action>
    Implement unit tests verifying:
    1. Disclaimer consent state management and blocking.
    2. Timeline continuous block grouping logic and duration calculations.
    3. Retrospective label updates reflected in timeline blocks.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_*.py"</verify>
  <done>All UI and timeline tests pass with 100% success rate.</done>
</task>

## Success Criteria
- [ ] Disclaimer manager, dashboard presenter, and retrospective timeline operational.
- [ ] Full test suite passes.
