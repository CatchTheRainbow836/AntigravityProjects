---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: Native Win32 Non-Admin Sensor Collectors

## Objective
Implement native Win32 sensor modules that capture aggregate keyboard/mouse kinetics, foreground window title/geometry, system idle time, and audio output state without requiring administrative elevation.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- TaskScheduler/DataCollector/src/types.ts
- TaskScheduler/DataCollector/src/schema.json

## Tasks

<task type="auto">
  <name>Build non-admin Win32 kinetic and window context collector</name>
  <files>
    TaskScheduler/DataCollector/src/collectors/kinetic_collector.py
    TaskScheduler/DataCollector/src/collectors/window_collector.py
    TaskScheduler/DataCollector/src/collectors/__init__.py
  </files>
  <action>
    Implement kinetic tracking (mouse speed, click count, aggregate keystroke rate) and window inspection (process name, sanitized title, bounds, screen area ratio).
    Include fallback / mock mechanisms so telemetry executes safely across both Windows native and cross-platform environments.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from collectors.kinetic_collector import KineticCollector; from collectors.window_collector import WindowCollector; k = KineticCollector(); w = WindowCollector(); k.start(); s = k.sample(); info = w.get_active_window_info(); assert 'mouse_velocity_avg' in s; assert 'app_name' in info; print('Collectors verified!')"</verify>
  <done>Kinetic and window collectors instantiate, sample data without errors, and return properly formatted feature dicts.</done>
</task>

<task type="auto">
  <name>Build system idle and audio state detector</name>
  <files>
    TaskScheduler/DataCollector/src/collectors/system_collector.py
  </files>
  <action>
    Implement non-admin system telemetry using GetLastInputInfo for idle seconds and Core Audio session enumerator for active sound playback detection.
    Ensure zero administrative privileges are required.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from collectors.system_collector import SystemCollector; sc = SystemCollector(); state = sc.get_system_state(); assert 'system_idle_seconds' in state; assert 'is_audio_playing' in state; print('System collector verified!')"</verify>
  <done>System collector returns idle duration and audio playback status reliably.</done>
</task>

## Success Criteria
- [ ] Kinetic, window geometry, idle, and audio state collectors fully functional and verified.
