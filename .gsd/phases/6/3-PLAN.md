---
phase: 6
plan: 3
wave: 2
depends_on: [1]
---

# Plan 6.3: Dynamic Interactive Activity Timeline & Retrospective Editor

## Objective
Build a dynamic visual timeline view featuring colored horizontal activity bars that stretch across time intervals (e.g., Coding from 1pm–2pm), supporting zoom/pan navigation, multi-state visual indicators, tooltip inspections, and a click-to-edit interface for retrospective labeling.

## Context
- .gsd/SPEC.md
- .gsd/DECISIONS.md
- TaskScheduler/DataCollector/src/ui/timeline.py
- TaskScheduler/DataCollector/src/db_manager.py

## Tasks

<task type="auto">
  <name>Build dynamic interactive timeline visualizer widget</name>
  <files>
    TaskScheduler/DataCollector/src/ui/components/timeline_canvas.py
    TaskScheduler/DataCollector/src/ui/views/timeline_view.py
    TaskScheduler/DataCollector/src/ui/timeline.py
  </files>
  <action>
    1. Implement `TimelineCanvas` widget:
       - Renders continuous horizontal colored bars representing recorded time intervals and classified activities (e.g. Coding: Cyan, Specialist Math: Purple, Physics: Blue, Idle: Slate, Media/Music: Orange).
       - Visual time axis with hour/minute ticks and dynamic scaling (1h, 4h, 12h, 24h zoom presets and horizontal pan).
       - Supports stacked or layered visualization when multiple concurrent states are active (e.g. Coding bar with subtle underlying Music accent).
    2. Add interactive hover and inspection:
       - Displays popup tooltip with start/end time, duration, detected app/title, confidence score (%), and finalized status (0 or 1).
    3. Add click-to-edit retrospective tagging:
       - Clicking any time block allows the user to reassign or correct the activity label, saving user-verified ground-truth back to the database.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from ui.components.timeline_canvas import TimelineCanvas; from ui.timeline import TimelinePresenter; print('Timeline canvas and presenter loaded successfully!')"</verify>
  <done>Timeline canvas renders time-stretching visual bars, allows zoom/pan, and supports retrospective tag editing.</done>
</task>

<task type="auto">
  <name>Integrate timeline with live database telemetry and write timeline tests</name>
  <files>
    TaskScheduler/DataCollector/tests/test_timeline_visualization.py
  </files>
  <action>
    1. Connect timeline view to live database queries with auto-refresh on new telemetry samples.
    2. Implement test suite `test_timeline_visualization.py`:
       - Verify interval aggregation logic (collapsing contiguous samples into time blocks).
       - Verify multi-state duration calculations.
       - Verify manual tag override persistence in SQLite.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_timeline_visualization.py" -v</verify>
  <done>Timeline interval calculations, multi-state segmentations, and retrospective database edits verified by automated tests.</done>
</task>

## Success Criteria
- [ ] Horizontal bars accurately represent activity duration across the time axis.
- [ ] Multi-state and confidence values are clearly represented visually.
- [ ] Retrospective editing updates database records without data loss.
