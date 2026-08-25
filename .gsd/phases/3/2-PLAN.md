---
phase: 3
plan: 2
wave: 2
depends_on:
  - 3.1
---

# Plan 3.2: Active Learning & Smart Prompt Trigger Manager

## Objective
Implement state transition monitoring, smart low-confidence prompt triggers, and retroactive user label application to support human-in-the-loop active learning.

## Context
- .gsd/phases/3/1-PLAN.md
- TaskScheduler/DataCollector/src/db_manager.py
- TaskScheduler/DataCollector/src/classifier.py

## Tasks

<task type="auto">
  <name>Build ActiveLearningManager and feedback loop</name>
  <files>
    TaskScheduler/DataCollector/src/active_learning.py
  </files>
  <action>
    Create ActiveLearningManager:
    1. Tracks consecutive low-confidence intervals and detects state transitions (e.g. app change or return from idle).
    2. Determines when to trigger prompt (e.g. after low confidence or periodically every 5 minutes if unclassified).
    3. Ingests user input to update past unclassified slices in SQLite and updates user preset mappings.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from active_learning import ActiveLearningManager; from db_manager import DatabaseManager; db = DatabaseManager(':memory:'); alm = ActiveLearningManager(db); rec = {'id': 1, 'app_name': 'Unknown.exe', 'window_title_sanitized': 'Unknown', 'confidence': 0.2}; should_prompt = alm.evaluate_prompt_trigger(rec); assert should_prompt is True; print('Active learning manager verified!')"</verify>
  <done>ActiveLearningManager identifies prompt triggers and applies user labels cleanly to SQLite records.</done>
</task>

<task type="auto">
  <name>Create automated test suite for classification and active learning</name>
  <files>
    TaskScheduler/DataCollector/tests/test_classifier.py
    TaskScheduler/DataCollector/tests/test_active_learning.py
  </files>
  <action>
    Implement unit tests validating:
    1. Heuristic classification of all cognitive states (Writing, Coding, Reading, Media, Gaming, Idle).
    2. Domain keyword matching across math, physics, chemistry, coding.
    3. Active learning prompt triggering intervals and retroactive SQLite label updates.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_*.py"</verify>
  <done>All classifier and active learning tests pass with 100% success rate.</done>
</task>

## Success Criteria
- [ ] Active learning manager evaluates triggers and applies corrections to SQLite.
- [ ] Full automated test suite passes.
