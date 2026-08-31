---
phase: 6
plan: 2
wave: 2
depends_on: [1]
---

# Plan 6.2: Desktop GUI Transformation, System Tray Daemon, Autostart & Autosave

## Objective
Transform DataCollector into a polished Windows desktop GUI application with modern CustomTkinter visuals, interactive menus (Start/Stop collector, Export, Preferences), background daemon execution with a Windows System Tray icon (`pystray`), crash-safe SQLite WAL autosaving, and post-consent Windows Registry autostart.

## Context
- .gsd/SPEC.md
- .gsd/DECISIONS.md
- TaskScheduler/DataCollector/src/engine.py
- TaskScheduler/DataCollector/src/db_manager.py
- TaskScheduler/DataCollector/src/ui/dashboard.py
- TaskScheduler/DataCollector/src/ui/disclaimer.py

## Tasks

<task type="auto">
  <name>Build the Desktop GUI application with CustomTkinter and modern menus</name>
  <files>
    TaskScheduler/DataCollector/src/ui/app.py
    TaskScheduler/DataCollector/src/ui/views/dashboard_view.py
    TaskScheduler/DataCollector/src/ui/views/export_view.py
    TaskScheduler/DataCollector/src/ui/views/disclaimer_view.py
    TaskScheduler/DataCollector/src/ui/views/prompt_modal.py
  </files>
  <action>
    1. Implement modern desktop UI using `customtkinter` (with graceful fallback to standard `tkinter`):
       - Dark/Light modern theme styling with cohesive accent colors.
       - Navigation sidebar with tabs: Live Dashboard, Timeline Visualizer, Dataset Exporter, Settings/Status.
    2. Build `DashboardView`: Live telemetry indicators (active app, multi-state badges, keystroke/mouse gauges, audio state, total records).
    3. Build `ExportView`: GUI controls to trigger incremental/full exports (JSONL, CSV, Parquet), choose target directory, and view hash manifests.
    4. Build `DisclaimerView`: First-run consent GUI screen presenting Terms & Privacy details with Agree/Disagree actions.
    5. Build `PromptModal`: Non-blocking popup window for active learning prompts asking the user to confirm/select activity when confidence is low or a major state transition occurs.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from ui.app import create_app; print('GUI app module successfully imported and validated!')"</verify>
  <done>Desktop GUI application initializes with all interactive views and modal dialogs ready for runtime execution.</done>
</task>

<task type="auto">
  <name>Implement System Tray daemon, SQLite WAL autosaving, and Windows autostart</name>
  <files>
    TaskScheduler/DataCollector/src/ui/tray.py
    TaskScheduler/DataCollector/src/autostart.py
    TaskScheduler/DataCollector/src/db_manager.py
    TaskScheduler/DataCollector/src/engine.py
  </files>
  <action>
    1. Configure crash-safe SQLite autosaving in `db_manager.py`:
       - Enable WAL mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`).
       - Ensure every recorded sample is committed immediately with transaction integrity.
    2. Implement `tray.py` (`TrayManager`):
       - Uses `pystray` to host a Windows System Tray icon with dynamic menu items: Show Dashboard, Pause/Resume Telemetry, Quick Export, Exit.
       - Connect window close (`WM_DELETE_WINDOW`) to hide window to system tray while background collection thread continues running uninterrupted.
    3. Implement `autostart.py`:
       - Provides Windows Registry integration (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run\DataCollector`) and startup folder fallback.
       - Only configures autostart after the user grants consent in `DisclaimerManager`.
       - Provides helper methods to check and toggle autostart status.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from autostart import AutostartManager; from ui.tray import TrayManager; asm = AutostartManager(); print('Autostart & Tray managers initialized!')"</verify>
  <done>Background telemetry logging runs continuously after window closing, database autosaves with WAL crash resistance, and autostart registration is managed safely.</done>
</task>

## Success Criteria
- [ ] Desktop GUI launches with modern aesthetic styling and sidebar navigation.
- [ ] Closing the GUI window minimizes to the system tray without terminating telemetry collection.
- [ ] SQLite database configured with WAL mode ensuring crash-safe persistence.
- [ ] Autostart registration only activated following user consent.
