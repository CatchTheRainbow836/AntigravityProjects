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

## ADR-004: Multi-State Activity & 75% Confidence Thresholding
- **Context**: Users multitask across monitors and audio sessions (e.g. coding + music + call). Single categorical states lose concurrent context.
- **Decision**: Track multi-label activity dimensions simultaneously with multi-monitor window and audio session context. Output continuous confidence $C \in [0.0, 1.0]$ and store a separate finalized binary value ($1$ if $C \ge 0.75$, else $0$).
- **Consequences**: Preserves raw probabilistic scores while providing unambiguous binary ground truth for downstream scheduling.

## ADR-005: Desktop GUI Architecture & System Tray Daemon Lifecycle
- **Context**: CLI requires terminal interaction; background logging must survive window closure and laptop reboots.
- **Decision**: Build modern GUI using CustomTkinter with dynamic canvas timeline visualization. Integrate `pystray` system tray daemon so window close minimizes to tray, and configure post-consent registry autostart.
- **Consequences**: Seamless user experience, dynamic timeline interaction, and non-intrusive background recording.

## ADR-006: GitHub Releases for Binary Artifacts & Clean Repository
- **Context**: Committing heavy compiled `.exe` files bloats git repository history.
- **Decision**: Keep compiled binaries in `.gitignore` and publish native Windows `.exe` artifacts via GitHub Actions Releases / Prereleases, supported by containerized Wine/MinGW and native build scripts.
- **Consequences**: Keeps git repo fast and lightweight while delivering accessible standalone Windows executables.

