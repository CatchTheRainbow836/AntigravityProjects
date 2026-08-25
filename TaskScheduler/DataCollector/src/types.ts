/**
 * DataCollector TypeScript Type Definitions
 * Defines strong types for telemetry feature streams, behavior segments, and active learning labels.
 */

export type CognitiveState =
  | 'DEEP_FOCUS_WRITING'
  | 'ACTIVE_CODING'
  | 'RESEARCH_READING'
  | 'MEDIA_CONSUMPTION'
  | 'HIGH_INTERACTION_GAMING'
  | 'COMMUNICATION'
  | 'IDLE_AWAY'
  | 'UNCLASSIFIED';

export type LabelSource =
  | 'HEURISTIC_RULE'
  | 'USER_CONFIRMED'
  | 'ACTIVE_PROMPT'
  | 'RETROSPECTIVE_EDIT';

export interface TelemetryRecord {
  id?: string;
  timestamp: string; // ISO 8601 UTC
  duration_seconds: number;
  app_name: string;
  window_title_sanitized: string;
  screen_area_pct: number;
  is_fullscreen: boolean;
  keystrokes_per_min: number;
  typing_burst_rate: number;
  mouse_velocity_avg: number;
  clicks_count: number;
  scroll_delta: number;
  is_audio_playing: boolean;
  is_audio_recording: boolean;
  system_idle_seconds: number;
  cognitive_state: CognitiveState;
  domain_label: string;
  confidence: number;
  label_source: LabelSource;
}

export interface BehaviorSegment {
  id?: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  primary_app: string;
  cognitive_state: CognitiveState;
  domain_label: string;
  confidence: number;
  source: LabelSource;
  sample_count: number;
}

export interface ExportManifest {
  export_id: string;
  exported_at: string;
  record_count: number;
  start_timestamp: string;
  end_timestamp: string;
  format: 'parquet' | 'jsonl' | 'csv';
  file_path: string;
  content_hash: string;
}
