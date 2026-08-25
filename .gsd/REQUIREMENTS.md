# REQUIREMENTS.md — AI Task Scheduler DataCollector

## Functional & Technical Requirements

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **REQ-01** | Portable single-file Windows `.exe` running without admin elevation or dependencies | SPEC §2.1 | Pending |
| **REQ-02** | First-run Privacy Disclaimer & Consent modal before any logging starts | SPEC §2.4 | Pending |
| **REQ-03** | Kinetic telemetry collector: mouse movement speed, click counts, aggregate keystroke frequency (no raw characters) | SPEC §2.2 | Pending |
| **REQ-04** | Window & Layout telemetry: foreground process, window title, window rect, screen coverage percentage | SPEC §2.2 | Pending |
| **REQ-05** | System state telemetry: idle detector (`GetLastInputInfo`) and audio playback active indicator | SPEC §2.2 | Pending |
| **REQ-06** | Heuristic rule-based auto-classifier for baseline cognitive states (Focus, Reading, Media, Gaming, Idle) | SPEC §2.3 | Pending |
| **REQ-07** | Smart Active-Learning notification popup for low-confidence intervals and task transitions | SPEC §2.3 | Pending |
| **REQ-08** | Clean modern desktop UI with real-time telemetry stats, current classification, and recording toggle | SPEC §2 | Pending |
| **REQ-09** | Interactive visual retrospective timeline to review, edit, and assign custom domain/subject tags (e.g. Specialist Math) | SPEC §2.3 | Pending |
| **REQ-10** | Local SQLite persistent storage with WAL mode for high-throughput, crash-resilient logging | SPEC §2.5 | Pending |
| **REQ-11** | Deduplicated incremental export engine (CSV, JSONL, Parquet) with state tracking | SPEC §2.5 | Pending |
| **REQ-12** | Root project README & documentation covering master roadmap and DataCollector usage | SPEC §1 | Pending |
