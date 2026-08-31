"""
Synthetic Telemetry Generator / Simulator for DataCollector.
Generates realistic multi-signal telemetry streams for testing and ML validation.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

SCENARIOS = [
    {
        "app_name": "WINWORD.EXE",
        "window_title_sanitized": "Document1 - Physics Lab Report Draft - Word",
        "screen_area_pct": 100.0,
        "is_fullscreen": False,
        "keystrokes_range": (120, 280),
        "mouse_velocity_range": (20, 150),
        "clicks_range": (1, 8),
        "audio_playing": False,
        "idle_secs": 0.0,
        "cognitive_state": "DEEP_FOCUS_WRITING",
        "domain_label": "Physics",
        "confidence": 0.94,
    },
    {
        "app_name": "OneNote.exe",
        "window_title_sanitized": "OneNote - Specialist Mathematics - Unit 3 Vectors",
        "screen_area_pct": 80.0,
        "is_fullscreen": False,
        "keystrokes_range": (30, 90),
        "mouse_velocity_range": (100, 450),
        "clicks_range": (5, 20),
        "audio_playing": False,
        "idle_secs": 0.0,
        "cognitive_state": "DEEP_FOCUS_WRITING",
        "domain_label": "Specialist Mathematics",
        "confidence": 0.96,
    },
    {
        "app_name": "Code.exe",
        "window_title_sanitized": "main.py - AI Task Scheduler - Visual Studio Code",
        "screen_area_pct": 100.0,
        "is_fullscreen": True,
        "keystrokes_range": (150, 350),
        "mouse_velocity_range": (50, 300),
        "clicks_range": (4, 15),
        "audio_playing": True,
        "idle_secs": 0.0,
        "cognitive_state": "ACTIVE_CODING",
        "domain_label": "Software Development",
        "confidence": 0.98,
    },
    {
        "app_name": "chrome.exe",
        "window_title_sanitized": "MIT OpenCourseWare - Vector Calculus Lecture - YouTube - Google Chrome",
        "screen_area_pct": 100.0,
        "is_fullscreen": False,
        "keystrokes_range": (0, 10),
        "mouse_velocity_range": (0, 30),
        "clicks_range": (0, 2),
        "audio_playing": True,
        "idle_secs": 12.0,
        "cognitive_state": "MEDIA_CONSUMPTION",
        "domain_label": "Mathematical Methods",
        "confidence": 0.89,
    },
    {
        "app_name": "LockApp.exe",
        "window_title_sanitized": "Windows Default Lock Screen",
        "screen_area_pct": 100.0,
        "is_fullscreen": True,
        "keystrokes_range": (0, 0),
        "mouse_velocity_range": (0, 0),
        "clicks_range": (0, 0),
        "audio_playing": False,
        "idle_secs": 320.0,
        "cognitive_state": "IDLE_AWAY",
        "domain_label": "Idle",
        "confidence": 1.0,
    }
]

def generate_sample_session(num_samples: int = 20, start_time: datetime = None) -> List[Dict[str, Any]]:
    if start_time is None:
        start_time = datetime.now(timezone.utc) - timedelta(seconds=num_samples * 5)

    samples = []
    current_time = start_time
    current_scenario = random.choice(SCENARIOS)

    for i in range(num_samples):
        # 15% chance to transition scenario
        if random.random() < 0.15:
            current_scenario = random.choice(SCENARIOS)

        keystrokes = random.uniform(*current_scenario["keystrokes_range"])
        mouse_vel = random.uniform(*current_scenario["mouse_velocity_range"])
        clicks = random.randint(*current_scenario["clicks_range"])

        record = {
            "timestamp": current_time.isoformat(),
            "duration_seconds": 5.0,
            "app_name": current_scenario["app_name"],
            "window_title_sanitized": current_scenario["window_title_sanitized"],
            "screen_area_pct": current_scenario["screen_area_pct"],
            "is_fullscreen": current_scenario["is_fullscreen"],
            "keystrokes_per_min": round(keystrokes, 1),
            "typing_burst_rate": round(random.uniform(0.1, 2.5), 2),
            "mouse_velocity_avg": round(mouse_vel, 1),
            "clicks_count": clicks,
            "scroll_delta": random.randint(0, 500) if mouse_vel > 20 else 0,
            "is_audio_playing": current_scenario["audio_playing"],
            "is_audio_recording": False,
            "system_idle_seconds": current_scenario["idle_secs"],
            "cognitive_state": current_scenario["cognitive_state"],
            "domain_label": current_scenario["domain_label"],
            "confidence": current_scenario["confidence"],
            "confidence_score": current_scenario["confidence"],
            "finalized_value": 1 if current_scenario["confidence"] >= 0.75 else 0,
            "active_states": {current_scenario["cognitive_state"]: 1},
            "label_source": "HEURISTIC_RULE" if random.random() > 0.3 else "USER_CONFIRMED",
            "is_exported": False
        }
        samples.append(record)
        current_time += timedelta(seconds=5)

    return samples
