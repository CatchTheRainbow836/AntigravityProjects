-- DataCollector SQLite Storage Schema with WAL Mode
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

-- 1. Telemetry Slices Table (High-frequency granular feature vectors)
CREATE TABLE IF NOT EXISTS telemetry_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL, -- ISO 8601 UTC string
    duration_seconds REAL NOT NULL DEFAULT 5.0,
    app_name TEXT NOT NULL,
    window_title_sanitized TEXT NOT NULL,
    screen_area_pct REAL NOT NULL DEFAULT 100.0,
    is_fullscreen INTEGER NOT NULL DEFAULT 0,
    keystrokes_per_min REAL NOT NULL DEFAULT 0.0,
    typing_burst_rate REAL NOT NULL DEFAULT 0.0,
    mouse_velocity_avg REAL NOT NULL DEFAULT 0.0,
    clicks_count INTEGER NOT NULL DEFAULT 0,
    scroll_delta INTEGER NOT NULL DEFAULT 0,
    is_audio_playing INTEGER NOT NULL DEFAULT 0,
    is_audio_recording INTEGER NOT NULL DEFAULT 0,
    system_idle_seconds REAL NOT NULL DEFAULT 0.0,
    cognitive_state TEXT NOT NULL DEFAULT 'UNCLASSIFIED',
    domain_label TEXT NOT NULL DEFAULT 'Unlabeled',
    confidence REAL NOT NULL DEFAULT 0.0,
    label_source TEXT NOT NULL DEFAULT 'HEURISTIC_RULE',
    is_exported INTEGER NOT NULL DEFAULT 0
);

-- Indexes for rapid time-range queries and ML batch exports
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_records (timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_exported ON telemetry_records (is_exported);
CREATE INDEX IF NOT EXISTS idx_telemetry_app ON telemetry_records (app_name);
CREATE INDEX IF NOT EXISTS idx_telemetry_cognitive ON telemetry_records (cognitive_state);
CREATE INDEX IF NOT EXISTS idx_telemetry_domain ON telemetry_records (domain_label);

-- 2. Aggregated Continuous Behavior Segments Table
CREATE TABLE IF NOT EXISTS behavior_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_minutes REAL NOT NULL,
    primary_app TEXT NOT NULL,
    cognitive_state TEXT NOT NULL,
    domain_label TEXT NOT NULL,
    confidence REAL NOT NULL,
    source TEXT NOT NULL,
    sample_count INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_segments_timespan ON behavior_segments (start_time, end_time);

-- 3. Export History Table (Ensures deduplication across multiple exports)
CREATE TABLE IF NOT EXISTS export_history (
    export_id TEXT PRIMARY KEY,
    exported_at TEXT NOT NULL,
    record_count INTEGER NOT NULL,
    start_timestamp TEXT NOT NULL,
    end_timestamp TEXT NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL
);

-- 4. User Configuration & Subject Presets Table
CREATE TABLE IF NOT EXISTS user_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preset_name TEXT UNIQUE NOT NULL, -- e.g. "Specialist Mathematics", "Physics", "Chemistry"
    color_hex TEXT NOT NULL DEFAULT '#3B82F6',
    default_keywords TEXT NOT NULL, -- JSON array of matching keyword tokens
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
