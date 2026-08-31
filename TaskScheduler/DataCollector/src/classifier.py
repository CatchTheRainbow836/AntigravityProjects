"""
Heuristic Classifier for DataCollector.
Provides deterministic multi-state classification:
- Multi-State & Concurrent Activity Detection (Coding, Writing, Research, Mathematics, Physics, Music/Media, Communication/Call, Gaming, Idle)
- Continuous Confidence Scoring for each active state (0.0 to 1.0)
- Finalized Binary Value: strictly 1 if confidence >= 0.75, else 0
"""

import re
from typing import Dict, Any, List, Tuple

DEFAULT_DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "Specialist Mathematics": [
        "specialist", "vector", "vectors", "calculus", "differential",
        "complex number", "matrices", "integration", "derivatives"
    ],
    "Mathematical Methods": [
        "methods", "probability", "statistics", "functions", "algebra",
        "logarithm", "exponential", "desmos", "casio", "ti-nspire"
    ],
    "General Mathematics": [
        "general math", "geometry", "trigonometry", "finance", "arithmetic", "percentage"
    ],
    "Physics": [
        "physics", "kinematics", "thermodynamics", "mechanics", "electromagnetism",
        "quantum", "optics", "forces", "momentum", "phet", "circuits"
    ],
    "Chemistry": [
        "chemistry", "titration", "organic", "moles", "periodic", "stoichiometry",
        "reactions", "acid", "base", "equilibrium"
    ],
    "Biology": [
        "biology", "genetics", "cellular", "photosynthesis", "ecology", "anatomy", "dna"
    ],
    "English & Humanities": [
        "essay", "literature", "history", "novel", "analysis", "thesis", "draft", "citation", "prose"
    ],
    "Software Development": [
        "python", "rust", "github", "compiler", "debug", "vscode", "visual studio code",
        "terminal", "algorithm", "function", "repository", "git", "stack overflow",
        ".py", ".rs", ".js", ".ts", ".cpp", ".cs", ".java"
    ]
}

IDE_APPS = {
    "code.exe", "devenv.exe", "pycharm64.exe", "idea64.exe", "clion64.exe",
    "windowsterminal.exe", "cmd.exe", "powershell.exe", "bash.exe"
}

WRITING_APPS = {
    "winword.exe", "onenote.exe", "notepad.exe", "notepad++.exe",
    "typora.exe", "obsidian.exe", "acrobat.exe", "acrord32.exe"
}

BROWSER_APPS = {
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"
}

MEDIA_APPS = {
    "spotify.exe", "vlc.exe", "wmplayer.exe", "music.ui.exe", "itunes.exe", "netflix.exe"
}

COMMUNICATION_APPS = {
    "discord.exe", "teams.exe", "zoom.exe", "slack.exe", "skype.exe", "telegram.exe", "whatsapp.exe"
}

CONFIDENCE_THRESHOLD = 0.75

class HeuristicClassifier:
    def __init__(self, custom_domain_keywords: Dict[str, List[str]] = None):
        self.domain_keywords = custom_domain_keywords if custom_domain_keywords is not None else DEFAULT_DOMAIN_KEYWORDS

    def extract_domain(self, window_title: str) -> Tuple[str, float]:
        if not window_title:
            return ("Unlabeled", 0.1)

        title_lower = window_title.lower()
        best_domain = "Unlabeled"
        max_matches = 0

        for domain, keywords in self.domain_keywords.items():
            matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', title_lower))
            if matches > max_matches:
                max_matches = matches
                best_domain = domain

        if max_matches >= 2:
            return (best_domain, 0.95)
        elif max_matches == 1:
            return (best_domain, 0.80)
        return ("Unlabeled", 0.20)

    def classify_cognitive_state(self, record: Dict[str, Any]) -> Tuple[str, float]:
        idle_secs = record.get("system_idle_seconds", 0.0)
        app_name = (record.get("app_name") or record.get("foreground_window", {}).get("process", "")).lower()
        title = (record.get("window_title_sanitized") or record.get("foreground_window", {}).get("title", "")).lower()
        kpm = record.get("keystrokes_per_min", record.get("keystroke_rate", 0.0) * 60 if "keystroke_rate" in record else 0.0)
        mouse_vel = record.get("mouse_velocity_avg", record.get("mouse_velocity", 0.0))
        clicks = record.get("clicks_count", 0)
        scroll = record.get("scroll_delta", 0)
        is_audio = bool(record.get("is_audio_playing", record.get("audio_active", False)))
        is_fullscreen = bool(record.get("is_fullscreen", False))

        # 1. Idle Detection
        if idle_secs >= 60.0:
            return ("IDLE_AWAY", 1.0)

        # 2. Gaming Detection
        if is_fullscreen and (mouse_vel > 250.0 or clicks > 12) and app_name not in IDE_APPS and app_name not in BROWSER_APPS:
            return ("HIGH_INTERACTION_GAMING", 0.90)

        # 3. Active Coding Detection
        if app_name in IDE_APPS or "vs code" in title or "visual studio" in title:
            if kpm > 20.0 or clicks > 2:
                return ("ACTIVE_CODING", 0.95)
            return ("ACTIVE_CODING", 0.80)

        # 4. Deep Focus Writing Detection
        if app_name in WRITING_APPS or "word" in title or "onenote" in title or "notion" in title:
            if kpm > 40.0:
                return ("DEEP_FOCUS_WRITING", 0.92)
            elif kpm > 10.0 or clicks > 3:
                return ("DEEP_FOCUS_WRITING", 0.85)
            return ("DEEP_FOCUS_WRITING", 0.70)

        # 5. Media Consumption
        if is_audio and kpm < 15.0 and mouse_vel < 40.0:
            return ("MEDIA_CONSUMPTION", 0.88)

        # 6. Research / Reading Detection
        if app_name in BROWSER_APPS:
            if scroll > 30 and kpm < 30.0:
                return ("RESEARCH_READING", 0.85)
            elif kpm > 50.0:
                return ("DEEP_FOCUS_WRITING", 0.75)
            elif clicks > 3:
                return ("RESEARCH_READING", 0.75)
            return ("RESEARCH_READING", 0.70)

        return ("UNCLASSIFIED", 0.30)

    def evaluate_multi_states(self, record: Dict[str, Any]) -> Dict[str, float]:
        states: Dict[str, float] = {}

        idle_secs = record.get("system_idle_seconds", 0.0)
        app_name = (record.get("app_name") or record.get("foreground_window", {}).get("process", "")).lower()
        title = (record.get("window_title_sanitized") or record.get("foreground_window", {}).get("title", "")).lower()
        kpm = record.get("keystrokes_per_min", record.get("keystroke_rate", 0.0) * 60 if "keystroke_rate" in record else 0.0)
        mouse_vel = record.get("mouse_velocity_avg", record.get("mouse_velocity", 0.0))
        clicks = record.get("clicks_count", 0)
        is_audio = bool(record.get("is_audio_playing", record.get("audio_active", False)))

        visible_windows = record.get("visible_windows", [])
        visible_apps = {w.get("process", "").lower() for w in visible_windows}
        visible_titles = " ".join([w.get("title", "").lower() for w in visible_windows])

        if idle_secs >= 60.0:
            states["Idle"] = 1.0
            return states

        # Coding
        if app_name in IDE_APPS or "vs code" in title or any(ide in visible_apps for ide in IDE_APPS):
            states["Coding"] = 0.95 if (kpm > 20 or clicks > 2 or app_name in IDE_APPS) else 0.80

        # Writing
        if app_name in WRITING_APPS or "word" in title or "onenote" in title:
            states["Writing"] = 0.90 if kpm > 10 else 0.75

        # Research
        if app_name in BROWSER_APPS or any(b in visible_apps for b in BROWSER_APPS):
            states["Research"] = 0.85

        # Music
        if is_audio or app_name in MEDIA_APPS or any(m in visible_apps for m in MEDIA_APPS) or "spotify" in visible_titles:
            states["Music"] = 0.90 if is_audio else 0.75

        # Communication
        if app_name in COMMUNICATION_APPS or any(c in visible_apps for c in COMMUNICATION_APPS):
            states["Communication"] = 0.88

        # Domain specifics
        dom, dom_conf = self.extract_domain(title + " " + visible_titles)
        if dom != "Unlabeled":
            states[dom] = dom_conf

        return states

    def classify(self, record: Dict[str, Any]) -> Dict[str, Any]:
        cog_state, cog_conf = self.classify_cognitive_state(record)
        title = (record.get("window_title_sanitized") or record.get("foreground_window", {}).get("title", ""))
        visible_titles = " ".join([w.get("title", "") for w in record.get("visible_windows", [])])
        domain_label, dom_conf = self.extract_domain(title + " " + visible_titles)

        multi_states = self.evaluate_multi_states(record)

        if cog_state == "IDLE_AWAY":
            overall_conf = 1.0
            domain_label = "Idle"
        else:
            if domain_label != "Unlabeled":
                overall_conf = round((cog_conf * 0.5) + (dom_conf * 0.5), 2)
            else:
                overall_conf = round(cog_conf, 2)

        finalized_value = 1 if overall_conf >= CONFIDENCE_THRESHOLD else 0

        active_states_binary = {
            state: (1 if conf >= CONFIDENCE_THRESHOLD else 0)
            for state, conf in multi_states.items()
        }

        return {
            "cognitive_state": cog_state,
            "domain_label": domain_label,
            "confidence": overall_conf,
            "confidence_score": overall_conf,
            "finalized_value": finalized_value,
            "active_states": active_states_binary,
            "state_confidences": multi_states,
            "label_source": "HEURISTIC_RULE"
        }
