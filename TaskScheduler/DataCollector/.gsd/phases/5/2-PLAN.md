---
phase: 5
plan: 2
wave: 2
depends_on:
  - 5.1
---

# Plan 5.2: Standalone Application Entry Point & Portable Packaging

## Objective
Implement the main executable entry point, wire all components together, compile/bundle the portable standalone `.exe` into `TaskScheduler/DataCollector/dist/`, and run end-to-end integration tests.

## Context
- .gsd/phases/5/1-PLAN.md
- TaskScheduler/DataCollector/src/main.py
- TaskScheduler/DataCollector/build.sh

## Tasks

<task type="auto">
  <name>Build main application entry point and portable packaging pipeline</name>
  <files>
    TaskScheduler/DataCollector/src/main.py
    TaskScheduler/DataCollector/build.sh
  </files>
  <action>
    Create main.py supporting interactive dashboard, simulation mode, and CLI export subcommands.
    Update build.sh to package and verify the standalone binary in TaskScheduler/DataCollector/dist/DataCollector.exe with zero runtime prerequisites.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); import main; print('Main entry point valid!')" && /workspace/TaskScheduler/DataCollector/build.sh</verify>
  <done>main.py imports cleanly, build.sh executes, and standalone binary is produced in dist/.</done>
</task>

<task type="auto">
  <name>Create automated export and end-to-end integration test suite</name>
  <files>
    TaskScheduler/DataCollector/tests/test_exporter.py
    TaskScheduler/DataCollector/tests/test_e2e.py
  </files>
  <action>
    Implement tests for:
    1. Incremental JSONL and CSV exports, content hash validation, and deduplication guarantees.
    2. End-to-end full application lifecycle (Consent -> Sampling -> Heuristic -> Timeline Edit -> Export).
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_*.py"</verify>
  <done>All export and end-to-end tests pass with 100% success rate.</done>
</task>

## Success Criteria
- [ ] Portable standalone application entry point and binary ready in `dist/`.
- [ ] All end-to-end tests passing.
