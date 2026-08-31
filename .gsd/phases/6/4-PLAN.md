---
phase: 6
plan: 4
wave: 3
depends_on: [2, 3]
---

# Plan 6.4: Windows Cross-Compilation Pipeline & Project File Consolidation

## Objective
Establish automated Windows executable compilation via GitHub Actions and cross-compile scripts, update `.gitignore` and distribution workflows (using GitHub Releases for binary distribution to keep the repo clean), consolidate project files into `TaskScheduler/DataCollector/`, and perform full end-to-end verification.

## Context
- .gsd/SPEC.md
- .gsd/DECISIONS.md
- TaskScheduler/DataCollector/build.sh
- TaskScheduler/DataCollector/DataCollector.spec
- TaskScheduler/DataCollector/src/main.py

## Tasks

<task type="auto">
  <name>Configure Windows automated compilation pipeline and file consolidation</name>
  <files>
    .github/workflows/build-windows.yml
    TaskScheduler/DataCollector/build.bat
    TaskScheduler/DataCollector/build.ps1
    TaskScheduler/DataCollector/build_windows.sh
    TaskScheduler/DataCollector/DataCollector.spec
    .gitignore
  </files>
  <action>
    1. Create `.github/workflows/build-windows.yml`:
       - Triggers on tag release (`v*`) or manual dispatch.
       - Runs on `windows-latest`, installs Python 3.12 and dependencies (customtkinter, pystray, pyinstaller, etc.).
       - Compiles `DataCollector.exe` via PyInstaller with icon and embedded resources.
       - Uploads `DataCollector.exe` as a release / prerelease asset and build artifact.
    2. Add `build.bat` and `build.ps1` for one-click native Windows local compilation.
    3. Update `build_windows.sh` and `build.sh` for Linux/Wine environments.
    4. Update `.gitignore`: Ensure `dist/` and `*.exe` are ignored from git commit tree to prevent repository bloating, while preserving clean source tracking.
    5. Consolidate DataCollector-specific planning files and assets inside `TaskScheduler/DataCollector/` while maintaining workspace compatibility.
  </action>
  <verify>test -f .github/workflows/build-windows.yml && test -f TaskScheduler/DataCollector/build.bat && test -f TaskScheduler/DataCollector/build.ps1 && python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); print('Build configs and scripts verified!')"</verify>
  <done>Automated CI/CD Windows packaging workflow, local Windows build scripts, and clean gitignore configured.</done>
</task>

<task type="auto">
  <name>Wire unified main entrypoint and execute end-to-end test suite</name>
  <files>
    TaskScheduler/DataCollector/src/main.py
    TaskScheduler/DataCollector/tests/test_e2e_gui_lifecycle.py
  </files>
  <action>
    1. Update `src/main.py`:
       - Default to launching the Desktop GUI with background tray daemon.
       - Support CLI flags for headless/automated runs: `--cli`, `--simulate`, `--export`, `--status`.
       - Connect first-run disclaimer verification before engine start.
    2. Create and run `test_e2e_gui_lifecycle.py`:
       - Verify full app startup flow, multi-state telemetry capture, crash-safe database storage, confidence thresholding, export triggering, and clean shutdown.
  </action>
  <verify>python3 -m unittest discover -s /workspace/TaskScheduler/DataCollector/tests -p "test_*.py" -v</verify>
  <done>All unit and end-to-end integration tests across telemetry, multi-state classification, GUI presenter, and packaging scripts pass with 0 failures.</done>
</task>

## Success Criteria
- [ ] Automated Windows CI/CD release workflow configured for `DataCollector.exe`.
- [ ] Unified `main.py` entrypoint supports both GUI and CLI operation modes.
- [ ] Full automated test suite passes with 100% test success.
