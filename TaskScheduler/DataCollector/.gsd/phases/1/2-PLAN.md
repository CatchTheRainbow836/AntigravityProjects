---
phase: 1
plan: 2
wave: 2
depends_on:
  - 1.1
---

# Plan 1.2: Foundation Data Contracts, Mock Simulation Harness & Validation Tests

## Objective
Implement core schema validation utilities, synthetic telemetry generator/simulator for cross-platform testing, and automated test suite to ensure the data format meets all AI training requirements.

## Context
- .gsd/phases/1/1-PLAN.md
- TaskScheduler/DataCollector/src/schema.json
- TaskScheduler/DataCollector/src/db_schema.sql

## Tasks

<task type="auto">
  <name>Build synthetic telemetry generator and SQLite storage harness</name>
  <files>
    TaskScheduler/DataCollector/src/simulator.py
    TaskScheduler/DataCollector/src/db_manager.py
  </files>
  <action>
    Create a robust database manager and synthetic telemetry generator that simulates realistic user sessions (e.g. typing an essay in Word, researching on Chrome, idle periods, switching to math tools).
    Ensure the database manager handles insertions, index querying, transaction batches, and WAL mode safely.
  </action>
  <verify>python3 -c "from TaskScheduler.DataCollector.src.db_manager import DatabaseManager; from TaskScheduler.DataCollector.src.simulator import generate_sample_session; db = DatabaseManager(':memory:'); data = generate_sample_session(10); db.insert_batch(data); assert db.count_records() == 10; print('Harness verified!')"</verify>
  <done>Synthetic telemetry generates realistic records and DatabaseManager successfully inserts and queries them without errors.</done>
</task>

<task type="auto">
  <name>Create automated schema & dataset validation test suite</name>
  <files>
    TaskScheduler/DataCollector/tests/test_schema.py
    TaskScheduler/DataCollector/tests/test_storage.py
  </files>
  <action>
    Implement comprehensive unit and integration tests verifying:
    1. Telemetry records strictly adhere to the defined schema.
    2. Extreme and edge cases (empty window titles, sudden disconnects, high-frequency burst clicks, null audio states).
    3. Proper deduplication and indexing performance.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_*.py"</verify>
  <done>All unit and integration tests pass with 100% success rate.</done>
</task>

## Success Criteria
- [ ] Database manager and telemetry simulator operational.
- [ ] Test suite verifies schema integrity, edge cases, and SQLite storage reliability.
