---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: First-Run Privacy Disclaimer & Consent Screen

## Objective
Implement the mandatory first-run privacy consent screen that informs the user about telemetry collection boundaries (aggregate kinetics only, no raw keylogging) and manages consent state persistence.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- TaskScheduler/DataCollector/src/types.ts

## Tasks

<task type="auto">
  <name>Build DisclaimerManager and consent persistence</name>
  <files>
    TaskScheduler/DataCollector/src/ui/disclaimer.py
    TaskScheduler/DataCollector/src/ui/__init__.py
  </files>
  <action>
    Create DisclaimerManager:
    1. Formulates the privacy disclosure text detailing exact telemetry metrics captured vs strictly excluded.
    2. Checks whether consent has been granted (stored in local config file or SQLite table).
    3. Handles accept/decline flows and prevents any recording until consent is confirmed.
  </action>
  <verify>python3 -c "import sys, tempfile, os; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from ui.disclaimer import DisclaimerManager; tf = tempfile.NamedTemporaryFile(delete=False); tf.close(); dm = DisclaimerManager(tf.name); assert not dm.has_consented(); dm.grant_consent(); assert dm.has_consented(); os.remove(tf.name); print('Disclaimer verified!')"</verify>
  <done>DisclaimerManager manages consent status and persists accepted state across sessions.</done>
</task>

## Success Criteria
- [ ] First-run disclaimer properly disclosures telemetry boundaries and blocks recording until user acceptance.
