# DataCollector — Behavior Telemetry & Dataset Engine

A zero-elevation, standalone Windows application for capturing behavioral interaction kinetics and application context to build empirical datasets for AI task scheduling models.

## Structure
- `src/`: Telemetry collection modules, heuristic classification engine, and UI components.
- `assets/`: UI styling, iconography, and terms/privacy disclaimer assets.
- `dist/`: Output directory for standalone portable `DataCollector.exe`.
- `exports/`: Destination for local, deduplicated dataset dumps (Parquet, JSONL, CSV).
- `tests/`: Automated unit and integration test suite.

## Build & Test
- Build: `./build.sh`
- Test: `python3 -m unittest discover -s tests -p "test_*.py"`
