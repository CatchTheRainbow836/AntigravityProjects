---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Project Directory Structure & Toolchain Architecture Setup

## Objective
Establish the `TaskScheduler/DataCollector/` environment, define the telemetry data schemas, data contracts, and cross-platform build/validation pipelines needed for a standalone, portable Windows application.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/ROADMAP.md
- README.md

## Tasks

<task type="auto">
  <name>Scaffold DataCollector project structure and toolchain configuration</name>
  <files>
    TaskScheduler/DataCollector/package.json
    TaskScheduler/DataCollector/Cargo.toml
    TaskScheduler/DataCollector/build.sh
    TaskScheduler/DataCollector/README.md
  </files>
  <action>
    Create project manifest and build configuration files under TaskScheduler/DataCollector/.
    Set up build scripts supporting standalone portable bundling.
    Avoid external runtime dependencies; ensure configuration targets zero-admin portable distribution.
  </action>
  <verify>test -f /workspace/TaskScheduler/DataCollector/Cargo.toml && test -f /workspace/TaskScheduler/DataCollector/build.sh</verify>
  <done>All project manifest and build scripts exist with valid configuration syntax.</done>
</task>

<task type="auto">
  <name>Define Telemetry Data Schemas and Storage Contracts</name>
  <files>
    TaskScheduler/DataCollector/src/schema.json
    TaskScheduler/DataCollector/src/types.ts
    TaskScheduler/DataCollector/src/db_schema.sql
  </files>
  <action>
    Specify formal schemas and SQL tables for:
    1. Time-slice telemetry stream (timestamp, app_name, sanitized window_title, screen_ratio, keystroke_rate, mouse_velocity, click_count, audio_active, idle_secs).
    2. Behavior segments (start_time, end_time, cognitive_state, domain_label, confidence, source).
    3. Export metadata and deduplication log.
    Ensure strict typing and field definitions ready for both runtime recording and ML ingestion.
  </action>
  <verify>python3 -c "import json, sqlite3; json.load(open('/workspace/TaskScheduler/DataCollector/src/schema.json')); conn = sqlite3.connect(':memory:'); conn.executescript(open('/workspace/TaskScheduler/DataCollector/src/db_schema.sql').read()); print('Schema valid!')"</verify>
  <done>SQL schema executes cleanly in SQLite and JSON schema parses with full field coverage.</done>
</task>

## Success Criteria
- [ ] Directory structure in `TaskScheduler/DataCollector/` is complete.
- [ ] Telemetry schemas and SQLite database tables are formally defined and verified.
