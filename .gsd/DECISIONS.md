# DECISIONS.md — Architecture Decision Record (ADR)

## ADR-001: Aggregate Kinetics over Raw Event Logging
- **Context**: Need mouse and keyboard metrics to classify focus/idle without triggering antivirus false positives or violating privacy.
- **Decision**: Capture statistical rates (keystrokes/sec, mouse velocity, click count) instead of raw characters or keycodes.
- **Consequences**: Antivirus-safe, GDPR/privacy compliant, non-invasive.

## ADR-002: Multi-Layer Labeling for Fine-Grained Subject Differentiation
- **Context**: Statistical kinetics cannot differentiate identical interaction workflows (e.g. Specialist Math vs Physics).
- **Decision**: Combine kinetic features (Layer 1: Cognitive State) with semantic window cues + active few-shot prompt tags (Layer 2: Domain/Subject).
- **Consequences**: Enables accurate sub-discipline classification for future AI scheduler training.

## ADR-003: Local-Only Storage & Deduplicated Incremental Export
- **Context**: Privacy for third-party users and ease of dataset compilation.
- **Decision**: SQLite local database + timestamp/hash tracking for incremental exports to CSV/JSONL/Parquet.
- **Consequences**: No external cloud exposure; clean, uncorrupted dataset drops.
