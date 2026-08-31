# SPEC.md — AI Task Scheduler: Behavior Telemetry & Data Collector

> **Status**: `FINALIZED`
> **Milestone**: v1.0 — DataCollector Executable & Telemetry Pipeline

---

## 1. Vision & Master Goal

Build a privacy-preserving, zero-setup, standalone Windows executable application (`DataCollector.exe`) that runs with standard user privileges to continuously capture device telemetry (aggregate interaction kinetics, window/screen geometry, application context, audio activity states) and auto-classify user behavior. 

This data collector forms the empirical dataset generation foundation for training custom ML models that power the subsequent **Autonomous AI Task & Homework Scheduler**.

---

## 2. Core Goals & Objectives

1. **Non-Elevated Standalone Execution**:
   - Runs as a portable single `.exe` on Windows without requiring admin rights, installer wizards, or runtime pre-requisites (.NET / Python installations).
2. **Rich Multi-Signal Telemetry**:
   - **Kinetics**: Keystrokes per minute, cadence variation, mouse velocity, clicks, scroll rates (NO raw keystroke logging).
   - **Window & Layout**: Active window title (sanitized), process name, window bounds, screen area ratio, multi-window split ratio.
   - **System States**: System idle duration (`GetLastInputInfo`), audio playback/capture active state (`IAudioSessionManager2`).
3. **Hybrid Heuristic Classifier & Active Learning**:
   - Built-in deterministic rules for common cognitive states (Deep Focus, Passive Reading, Media/Video, Gaming, Idle).
   - Smart, non-intrusive prompt triggers (on major context transitions / low-confidence intervals) to prompt user ground-truth labels.
   - Retrospective timeline editor allowing users to review, tag, and correct past time blocks.
4. **First-Run Privacy & Disclaimer Screen**:
   - Clear disclosure upon initial launch explaining exactly what metrics are captured and confirming that raw keys/passwords/audio streams are never recorded.
5. **Local-Only, Deduplicated Data Export Engine**:
   - Secure local storage (SQLite).
   - Incremental, deduplicated export to clean CSV, JSONL, and Parquet formats formatted for ML pipelines (PyTorch, Scikit-learn, Pandas).

---

## 3. Non-Goals (Out of Scope for Phase 1)

- Building the schedule generation engine / calendar optimizer (reserved for Milestone 2: `TaskScheduler`).
- Cloud syncing or telemetry transmission over the network (all data stays strictly local on the user's machine).
- Keylogging or raw keystroke sequence capture (strictly disallowed for privacy and AV safety).
- Audio/video screen recording (only binary audio activity state and window bounding rectangles are captured).

---

## 4. Target Users & Constraints

- **Users**: High school / university students and knowledge workers with diverse workflows (math, physics, essay writing, coding, casual browsing).
- **Environment**: Windows 10/11 (64-bit), standard user privileges (no UAC / Administrator prompt).
- **Performance Budget**: `<1%` CPU utilization, `<40MB` RAM footprint, startup time `<1` second.

---

## 5. Success Criteria & Verification

- [ ] Single executable file launches cleanly on standard non-admin Windows account.
- [ ] First-run privacy modal appears, requiring acknowledgment before recording begins.
- [ ] Telemetry engine accurately captures window titles, screen ratios, mouse velocity, keystroke rates, and audio playback state without dropping samples.
- [ ] Active learning prompt triggers seamlessly without interrupting fullscreen games or critical tasks.
- [ ] Retrospective timeline view accurately shows recent activity blocks and allows 1-click reassignment.
- [ ] Incremental export produces valid, deduplicated JSONL/CSV/Parquet files ready for direct loading in Python.
