---
phase: 6
plan: 1
wave: 1
---

# Plan 6.1: Multi-State Activity Classification & Confidence Thresholding Engine

## Objective
Upgrade the classification engine and SQLite database layer to support simultaneous multi-state activity detection (multi-window / multi-monitor + background audio sessions) with continuous confidence scores $[0.0, 1.0]$ and a separate finalized binary value ($1$ if confidence $\ge 0.75$, else $0$).

## Context
- .gsd/SPEC.md
- .gsd/DECISIONS.md
- TaskScheduler/DataCollector/src/classifier.py
- TaskScheduler/DataCollector/src/db_manager.py
- TaskScheduler/DataCollector/src/db_schema.sql
- TaskScheduler/DataCollector/src/collectors/window_collector.py
- TaskScheduler/DataCollector/src/collectors/system_collector.py

## Tasks

<task type="auto">
  <name>Refactor classifier and database schema for multi-state classification & 75% confidence thresholding</name>
  <files>
    TaskScheduler/DataCollector/src/db_schema.sql
    TaskScheduler/DataCollector/src/db_manager.py
    TaskScheduler/DataCollector/src/classifier.py
    TaskScheduler/DataCollector/src/collectors/window_collector.py
  </files>
  <action>
    1. Update `db_schema.sql` and `db_manager.py` schema version to v2:
       - Add `finalized_value INTEGER NOT NULL DEFAULT 0` (0 or 1 binary indicator).
       - Add `confidence_score REAL NOT NULL DEFAULT 0.0` (range 0.0 to 1.0).
       - Add `active_states_json TEXT` to store multi-state mapping (e.g. `{"Coding": 1, "Music": 1, "Communication": 0}`).
       - Support schema migration from v1 to v2 gracefully.
    2. Upgrade `window_collector.py` to capture visible background windows across multi-monitor setups in addition to the foreground window.
    3. Refactor `classifier.py` (`HeuristicClassifier`):
       - Implement multi-label state evaluation: determine candidate active states (e.g., Coding, Study/Math/Physics, Music/Media, Communication/Call, Gaming, Idle).
       - Calculate individual confidence scores $C \in [0.0, 1.0]$ for each detected state based on kinetic rates, foreground/background window titles, and audio state.
       - Enforce the 75% threshold rule: `finalized_value = 1 if confidence >= 0.75 else 0`.
       - Return structured payload containing `primary_state`, `confidence`, `finalized_value`, and `all_states`.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from classifier import HeuristicClassifier; c = HeuristicClassifier(); r1 = c.classify({'keystroke_rate': 2.5, 'mouse_velocity': 120, 'audio_active': True, 'foreground_window': {'title': 'main.py - VS Code', 'process': 'Code.exe'}, 'visible_windows': [{'title': 'Spotify Free', 'process': 'Spotify.exe'}]}); assert r1['finalized_value'] == 1, 'Expected finalized_value=1 for high confidence'; assert r1['confidence'] >= 0.75; assert 'Coding' in r1['active_states'] and 'Music' in r1['active_states']; print('Classifier multi-state and thresholding verified!')"</verify>
  <done>Classifier accurately evaluates concurrent states and sets finalized_value=1 when confidence >= 0.75, with schema storing confidence and finalized value separately.</done>
</task>

<task type="auto">
  <name>Implement comprehensive unit and integration tests for multi-state classification</name>
  <files>
    TaskScheduler/DataCollector/tests/test_multistate_classifier.py
  </files>
  <action>
    Create test suite covering:
    1. High confidence coding + background music -> finalized_value = 1, both states marked active.
    2. Ambiguous activity with confidence < 0.75 -> finalized_value = 0, confidence stored.
    3. Multi-screen context with active research + video stream.
    4. Database insertion and retrieval of v2 schema records including `confidence_score`, `finalized_value`, and `active_states_json`.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_multistate_classifier.py" -v</verify>
  <done>All multi-state classification and confidence threshold tests pass with 100% assertions satisfied.</done>
</task>

## Success Criteria
- [ ] Multi-state activity detection correctly identifies concurrent activities.
- [ ] Binary finalized value is strictly 1 when confidence >= 0.75, and 0 otherwise.
- [ ] Database schema records confidence score and finalized value in distinct columns.
