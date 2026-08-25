# ROADMAP.md — AI Task Scheduler: DataCollector

> **Milestone**: v1.0 — DataCollector Standalone Executable & Telemetry Pipeline
> **Current Phase**: Phase 1 (Foundation & Architecture)

---

## Must-Haves (from SPEC)
- [ ] Standalone zero-dependency executable (`TaskScheduler/DataCollector/dist/DataCollector.exe`)
- [ ] Privacy & Disclaimer First-Run Screen
- [ ] Non-Admin Win32 Telemetry Engine (Keyboard/Mouse aggregates, Window title/geometry, Audio states, Idle)
- [ ] Rule-Based Auto-Classification & Smart Prompting / Retrospective Timeline
- [ ] Incremental Deduplicated Local Dataset Export (JSONL / CSV / Parquet)
- [ ] Comprehensive Project Documentation & README

---

## Phases

### Phase 1: Foundation & Project Setup
**Status**: ⬜ Not Started  
**Objective**: Establish `TaskScheduler/DataCollector/` directory structure, build toolchains (Rust / Win32 backend & modern UI), and master `README.md`.  
**Requirements**: REQ-01, REQ-12

### Phase 2: Core Win32 Telemetry & Storage Engine
**Status**: ⬜ Not Started  
**Objective**: Implement non-admin native Win32 collectors (mouse/keyboard rates, window geometry, audio state, idle) and high-performance local SQLite storage with schema versioning.  
**Requirements**: REQ-03, REQ-04, REQ-05, REQ-10

### Phase 3: Rule-Based Classifier & Active Learning System
**Status**: ⬜ Not Started  
**Objective**: Build the heuristic classification pipeline, state transition detector, smart popup trigger, and user feedback ingestion loop.  
**Requirements**: REQ-06, REQ-07

### Phase 4: Desktop UI, Disclaimer & Retrospective Timeline
**Status**: ⬜ Not Started  
**Objective**: Create a sleek, modern UI featuring first-run privacy consent, real-time activity dashboard, task tag presets (e.g., Specialist Math, Physics), and retrospective timeline editor.  
**Requirements**: REQ-02, REQ-08, REQ-09

### Phase 5: Incremental Export Engine & Standalone Packaging
**Status**: ⬜ Not Started  
**Objective**: Implement deduplicated local file export (JSONL, CSV, Parquet), standalone compilation pipeline into `TaskScheduler/DataCollector/dist/`, and end-to-end verification.  
**Requirements**: REQ-01, REQ-11
