# Phase 6 Research: GUI Transformation, Multi-State Classification & Windows Compilation

## 1. Overview & Objectives
Phase 6 transforms the DataCollector from a CLI prototype into a production-grade, aesthetically pleasing Windows desktop application with background logging capabilities, crash-safe autosave, multi-state activity classification with >=75% confidence thresholding, dynamic visual timeline rendering, and automated Windows binary distribution.

---

## 2. Technical Findings & Architecture

### A. Windows Compilation & Packaging
- **Constraint**: PyInstaller on Linux produces Linux ELF binaries; producing a native Windows PE `.exe` requires a Windows host or Wine emulation.
- **Solution**:
  1. `.github/workflows/build-windows.yml`: Runs on `windows-latest` via GitHub Actions on tag/push, producing and uploading `DataCollector.exe` release artifacts automatically.
  2. `build_windows.sh`: Linux Wine cross-compilation helper.
  3. `build.bat` / `build.ps1`: Native Windows build scripts.
  4. PyInstaller `.spec` configuration with embedded assets (`schema.json`, `db_schema.sql`, GUI assets).

### B. GUI Framework: CustomTkinter
- **Advantages**: Built on top of Python's standard `tkinter` with modern dark/light mode widgets, high-DPI scaling, no browser dependency, small footprint (~20MB binary).
- **Architecture**:
  - `MainWindow`: Sidebar navigation (Dashboard, Timeline, Exporter, Settings/Status).
  - `TimelineCanvas`: Custom high-performance canvas rendering colored continuous activity blocks with time zooming and hover inspection.
  - `ActiveLearningModal`: Non-blocking pop-up dialog triggered on state transitions.
  - `DisclaimerView`: First-run consent screen.

### C. Background Execution & System Tray Daemon
- **Library**: `pystray` (works seamlessly on Windows with standard win32 tray hooks) combined with `threading.Thread(daemon=True)`.
- **Window Close Hook**: Intercept `WM_DELETE_WINDOW` / `protocol("WM_DELETE_WINDOW")` to hide window instead of exiting.
- **Autostart**: `winreg` writing `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\DataCollector` upon user consent.
- **Crash-Safe Autosave**: SQLite WAL mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`) with per-event transaction commits.

### D. Multi-State Classification & 75% Confidence Thresholding
- **Multi-Signal Input**:
  - Visible window enumeration (`EnumWindows`) across multiple monitors.
  - Active audio render sessions (WASAPI `IAudioSessionManager2`) for background media/calls.
  - Statistical input kinetics (keystroke & mouse velocities).
- **Classification Output**:
  - Multi-label dictionary / candidate tags (e.g. `Coding`, `Mathematics`, `Music`, `Communication`, `Idle`).
  - For each tag $k$, compute continuous confidence score $C_k \in [0.0, 1.0]$.
  - Store `confidence` (float) and `finalized_value` (integer: $1$ if $C_k \ge 0.75$ else $0$).
- **Database Schema**:
  - Updated `activity_records` schema storing primary state, multi-state JSON payload, confidence score, and binary finalized flag.

---

## 3. Risk Mitigation & Verification Strategy
- **Risk**: Headless Linux container cannot open GUI windows for automated tests.
  - **Mitigation**: Implement strict separation between UI presenters/models and canvas views; use headless testing modes (`xvfb` or mock UI loops) and direct unit testing of engine/presenter state machines.
- **Risk**: Antivirus false positives for background tray daemons.
  - **Mitigation**: Clean non-admin API usage, clear tray icon indicator, no raw keylogging.
