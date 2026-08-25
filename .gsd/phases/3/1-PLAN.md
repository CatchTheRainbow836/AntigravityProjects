---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: Rule-Based Heuristic Classifier

## Objective
Implement a multi-layer heuristic classification engine that computes baseline cognitive state (Layer 1), domain/subject classification (Layer 2), and confidence scores from multi-modal telemetry signals.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- TaskScheduler/DataCollector/src/types.ts

## Tasks

<task type="auto">
  <name>Build HeuristicClassifier with two-layer signal evaluation</name>
  <files>
    TaskScheduler/DataCollector/src/classifier.py
  </files>
  <action>
    Implement HeuristicClassifier:
    1. Layer 1 (Cognitive State): Idle (>60s idle), Focus Writing (Word/Docs + high typing rate), Active Coding (IDE + typing/clicking), Media Consumption (Browser + Audio + low input), Research Reading (Browser/PDF + scrolling + low typing), High Interaction Gaming (Fullscreen + high mouse velocity/clicks).
    2. Layer 2 (Domain Label): Keyword token matching on sanitized window title (e.g. "Specialist Mathematics", "Vectors", "Calculus", "Physics", "Thermodynamics", "Coding").
    3. Confidence Score: Weighted multi-signal convergence score.
  </action>
  <verify>python3 -c "import sys; sys.path.insert(0, '/workspace/TaskScheduler/DataCollector/src'); from classifier import HeuristicClassifier; c = HeuristicClassifier(); res = c.classify({'app_name': 'WINWORD.EXE', 'window_title_sanitized': 'Physics Lab.docx', 'keystrokes_per_min': 150.0, 'mouse_velocity_avg': 50.0, 'clicks_count': 2, 'scroll_delta': 0, 'is_audio_playing': False, 'system_idle_seconds': 0.0, 'is_fullscreen': False}); assert res['cognitive_state'] == 'DEEP_FOCUS_WRITING'; assert res['domain_label'] == 'Physics'; assert res['confidence'] > 0.8; print('Classifier verified!')"</verify>
  <done>Classifier accurately assigns cognitive state, domain label, and confidence score across standard test vectors.</done>
</task>

## Success Criteria
- [ ] Multi-signal heuristic rules accurately classify writing, coding, media, reading, gaming, and idle.
- [ ] Domain keywords extract subject labels from window titles.
