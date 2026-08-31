# ROADMAP.md — AI Task Scheduler: DataCollector

> **Milestone**: v1.0 — DataCollector Standalone Executable & Telemetry Pipeline ✅ COMPLETE
> **Current Phase**: All phases shipped — pending future TaskScheduler integration

---

## Must-Haves (from SPEC)
- [x] Project Scaffolding & Foundational Data Contracts (Phase 1)
- [x] Non-Admin Win32 Telemetry Engine (Keyboard/Mouse aggregates, Window title/geometry, Audio states, Idle) (Phase 2)
- [x] Rule-Based Auto-Classification & Smart Prompting / Retrospective Timeline (Phase 3)
- [x] Desktop UI & Privacy Disclaimer First-Run Screen (Phase 4)
- [x] Incremental Deduplicated Local Dataset Export & Standalone Packaging (Phase 5)

---

## Phases

### Phase 1: Foundation & Project Setup
**Status**: ✅ Complete  
**Objective**: Establish `TaskScheduler/DataCollector/` directory structure, build toolchains (Rust / Win32 backend & modern UI), and master README.md.  
**Requirements**: REQ-01, REQ-12

### Phase 2: Core Win32 Telemetry & Storage Engine
**Status**: ✅ Complete  
**Objective**: Implement non-admin native Win32 collectors (mouse/keyboard rates, window geometry, audio state, idle) and high-performance local SQLite storage with schema versioning.  
**Requirements**: REQ-03, REQ-04, REQ-05, REQ-10

### Phase 3: Rule-Based Classifier & Active Learning System
**Status**: ✅ Complete  
**Objective**: Build the heuristic classification pipeline, state transition detector, smart popup trigger, and user feedback ingestion loop.  
**Requirements**: REQ-06, REQ-07

### Phase 4: Desktop UI, Disclaimer & Retrospective Timeline
**Status**: ✅ Complete  
**Objective**: Create a sleek, modern UI featuring first-run privacy consent, real-time activity dashboard, task tag presets (e.g., Specialist Math, Physics), and retrospective timeline editor.  
**Requirements**: REQ-02, REQ-08, REQ-09

### Phase 5: Incremental Export Engine & Standalone Packaging
**Status**: ✅ Complete  
**Objective**: Implement deduplicated local file export (JSONL, CSV, Parquet), standalone compilation pipeline into `TaskScheduler/DataCollector/dist/`, and end-to-end verification.  
**Requirements**: REQ-01, REQ-11

---

### Phase 6: Recompile and Improve UI
**Status**: ✅ Complete  
**Objective**: Transform DataCollector into a polished Windows GUI application with dynamic timeline visualization, multi-state activity classification (with 0/1 finalization at >=75% confidence and multi-monitor/audio context), background thread execution with system tray & autostart, crash-safe autosave, and a robust Windows cross-compilation / release pipeline.  
**Depends on**: Phase 5

**Tasks**:
- [x] Plan 6.1: Multi-State Activity Classification & Confidence Thresholding Engine
- [x] Plan 6.2: Desktop GUI Transformation, System Tray Daemon, Autostart & Autosave
- [x] Plan 6.3: Dynamic Interactive Activity Timeline & Retrospective Editor
- [x] Plan 6.4: Windows Cross-Compilation Pipeline & Project File Consolidation

**Verification**:
- Automated test suite (42/42 tests passing), CI workflow `.github/workflows/build-windows.yml`, native scripts (`build.bat`, `build.ps1`), verified end-to-end.


