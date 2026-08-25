# AI Task Scheduler & Behavior Recognizer

An intelligent, routine-aware Windows productivity system that models user behavior to automate task and homework scheduling, estimate completion durations, and provide adaptive schedule adherence checks.

---

## 🌟 Project Architecture & Phasing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGE 1: BEHAVIOR DATA COLLECTOR                   │
│  • Privacy-first kinetic & context telemetry (Win32, Non-Admin)             │
│  • Real-time heuristic classification & smart human-in-the-loop labeling    │
│  • Local SQLite database & deduplicated dataset export (Parquet/JSONL/CSV)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Empirical Datasets)
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGE 2: BEHAVIOR RECOGNITION AI                   │
│  • ML Models trained on user kinetics + semantic document cues              │
│  • Cognitive state detection (Deep Work, Research, Passive Media, Idle)     │
│  • Fine-grained domain/subject classification (e.g. Specialist Math)         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Task & Duration Estimates)
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGE 3: AUTONOMOUS AI TASK SCHEDULER              │
│  • Schedule synthesis tailored to real daily habits & energy curves         │
│  • Dynamic schedule re-adjustment and milestone check-ins                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

- [`TaskScheduler/`](file:///workspace/TaskScheduler): Root directory for all task scheduler modules.
  - [`DataCollector/`](file:///workspace/TaskScheduler/DataCollector):
    - `src/`: Native telemetry engine, heuristic classifier, and desktop UI.
    - `assets/`: Icons, disclaimer assets, and interface styles.
    - `dist/`: Standalone `.exe` binary distribution.
    - `exports/`: Local deduplicated dataset exports.
- [`.gsd/`](file:///workspace/.gsd): Project specifications, requirements, architecture decisions, and roadmap.

---

## 🔒 Privacy & Non-Admin Architecture

1. **Zero Elevation Required**: Operates completely under standard user privileges on Windows 10/11.
2. **No Raw Keystrokes**: Strictly records aggregate metrics (typing cadence, keystrokes per minute, mouse velocity). Passwords and confidential text are never logged.
3. **Local Only**: All data is saved directly on your machine in local SQLite and exported files; nothing is sent across the internet.
4. **Transparent Consent**: Initial startup displays a clear terms of data collection disclaimer before recording commences.

---

## 🚀 Getting Started

The DataCollector is packaged as a portable single-file executable (`DataCollector.exe`) located in `TaskScheduler/DataCollector/dist/`. No installation or runtime dependencies are required.
