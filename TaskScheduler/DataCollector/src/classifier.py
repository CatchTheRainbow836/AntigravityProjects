"""
Heuristic Classifier for DataCollector.
Provides deterministic multi-layer baseline classification:
- Layer 1: Cognitive State (Writing, Coding, Reading, Media, Gaming, Idle)
- Layer 2: Domain / Subject Label (Mathematics, Physics, Chemistry, Software, etc.)
- Confidence Score: Multi-signal convergence rating (0.0 to 1.0)
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
        app_name = record.get("app_name", "").lower()
        kpm = record.get("keystrokes_per_min", 0.0)
        mouse_vel = record.get("mouse_velocity_avg", 0.0)
        clicks = record.get("clicks_count", 0)
        scroll = record.get("scroll_delta", 0)
        is_audio = record.get("is_audio_playing", False)
        is_fullscreen = record.get("is_fullscreen", False)

        # 1. Idle Detection
        if idle_secs >= 60.0:
            return ("IDLE_AWAY", 1.0)

        # 2. Gaming / High Interaction Detection
        if is_fullscreen and (mouse_vel > 250.0 or clicks > 12) and app_name not in IDE_APPS and app_name not in BROWSER_APPS:
            return ("HIGH_INTERACTION_GAMING", 0.90)

        # 3. Media / Video Watching Detection
        if is_audio and kpm < 15.0 and mouse_vel < 40.0:
            return ("MEDIA_CONSUMPTION", 0.88)

        # 4. Active Coding Detection
        if app_name in IDE_APPS:
            if kpm > 20.0 or clicks > 2:
                return ("ACTIVE_CODING", 0.95)
            return ("ACTIVE_CODING", 0.75)

        # 5. Deep Focus Writing Detection
        if app_name in WRITING_APPS:
            if kpm > 40.0:
                return ("DEEP_FOCUS_WRITING", 0.92)
            elif kpm > 10.0 or clicks > 3:
                return ("DEEP_FOCUS_WRITING", 0.80)
            return ("DEEP_FOCUS_WRITING", 0.65)

        # 6. Research / Reading Detection
        if app_name in BROWSER_APPS:
            if scroll > 30 and kpm < 30.0:
                return ("RESEARCH_READING", 0.85)
            elif kpm > 50.0:
                return ("DEEP_FOCUS_WRITING", 0.75)
            elif clicks > 3:
                return ("RESEARCH_READING", 0.70)
            return ("RESEARCH_READING", 0.60)

        # Fallback
        return ("UNCLASSIFIED", 0.30)

    def classify(self, record: Dict[str, Any]) -> Dict[str, Any]:
        cognitive_state, cog_conf = self.classify_cognitive_state(record)
        domain_label, dom_conf = self.extract_domain(record.get("window_title_sanitized", ""))

        # Overall confidence is weighted average
        if cognitive_state == "IDLE_AWAY":
            overall_conf = 1.0
            domain_label = "Idle"
        else:
            overall_conf = round((cog_conf * 0.6) + (dom_conf * 0.4), 2)

        return {
            "cognitive_state": cognitive_state,
            "domain_label": domain_label,
            "confidence": overall_conf,
            "label_source": "HEURISTIC_RULE"
        }
