"""
Main Application Entry Point for DataCollector.
Coordinates the desktop GUI app, background tray daemon, telemetry engine,
heuristic classification, active learning, and dataset exporter.
"""

import sys
import os
import time
import argparse

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from db_manager import DatabaseManager
from classifier import HeuristicClassifier
from engine import TelemetryEngine
from exporter import DatasetExporter
from ui.disclaimer import DisclaimerManager
from ui.dashboard import DashboardPresenter
from simulator import generate_sample_session

def run_gui(db_path: str = "datacollector.db"):
    try:
        from ui.app import create_app
        app = create_app(db_path=db_path)
        app.mainloop()
    except Exception as e:
        print(f"[GUI Notice] Unable to initialize window interface: {e}")
        print("Falling back to CLI mode...")
        run_live_cli(db_path)

def run_live_cli(db_path: str = "datacollector.db"):
    print("═" * 60)
    print("      AI TASK SCHEDULER — BEHAVIOR DATA COLLECTOR (CLI)")
    print("═" * 60)

    disclaimer = DisclaimerManager()
    if not disclaimer.has_consented():
        print(disclaimer.get_disclaimer_text())
        print("\nDo you agree to the privacy policy and consent to local data recording? (y/n): ")
        try:
            choice = input().strip().lower()
        except EOFError:
            choice = "y"
        if choice in ("y", "yes"):
            disclaimer.grant_consent()
            print("✓ Consent granted. Initializing telemetry engine...")
        else:
            print("✗ Consent not granted. Exiting without recording.")
            sys.exit(0)

    db = DatabaseManager(db_path)
    classifier = HeuristicClassifier()
    engine = TelemetryEngine(db=db, classifier_fn=classifier.classify)
    presenter = DashboardPresenter(engine=engine, db=db, disclaimer_mgr=disclaimer)

    print("Starting background telemetry recording (5s intervals)... Press Ctrl+C to stop.")
    presenter.start_recording()

    try:
        while True:
            time.sleep(5)
            state = presenter.get_dashboard_state()
            latest_app = state.get("current_app")
            latest_state = state.get("current_cognitive_state")
            latest_domain = state.get("current_domain")
            conf = state.get("confidence", 0.0)
            total = state.get("total_db_records", 0)

            print(f"[{time.strftime('%H:%M:%S')}] App: {latest_app[:20]:<20} | State: {latest_state:<20} | Domain: {latest_domain:<18} | Conf: {conf:.2f} | Total: {total}")
    except KeyboardInterrupt:
        print("\nStopping telemetry engine...")
        presenter.stop_recording()
        print(f"✓ Saved {db.count_records()} records to local database: {db_path}")

def run_simulate(count: int = 50, db_path: str = "datacollector.db"):
    db = DatabaseManager(db_path)
    print(f"Generating {count} synthetic multi-signal telemetry samples...")
    samples = generate_sample_session(count)
    inserted = db.insert_batch(samples)
    print(f"✓ Successfully stored {inserted} synthetic records in {db_path}")

def run_export(fmt: str = "jsonl", db_path: str = "datacollector.db"):
    db = DatabaseManager(db_path)
    exporter = DatasetExporter(db)
    manifest = exporter.export_incremental(fmt=fmt)
    if manifest.get("export_id"):
        print(f"✓ Export completed: {manifest['record_count']} records exported to {manifest['file_path']}")
        print(f"  SHA256 Hash: {manifest['content_hash']}")
    else:
        print(manifest.get("message", "No new records to export."))

def main():
    parser = argparse.ArgumentParser(description="AI Task Scheduler: DataCollector Standalone Executable")
    parser.add_argument("command", nargs="?", default="gui", choices=["gui", "cli", "run", "simulate", "export", "status"])
    parser.add_argument("--cli", action="store_true", help="Force running in command-line interface mode")
    parser.add_argument("--background", action="store_true", help="Launch minimized to background tray")
    parser.add_argument("--format", default="jsonl", choices=["jsonl", "csv"], help="Export format")
    parser.add_argument("--count", type=int, default=50, help="Number of simulated records")
    parser.add_argument("--db", default="datacollector.db", help="Database file path")

    args = parser.parse_args()

    if args.cli or args.command in ("cli", "run"):
        run_live_cli(args.db)
    elif args.command == "simulate":
        run_simulate(args.count, args.db)
    elif args.command == "export":
        run_export(args.format, args.db)
    elif args.command == "status":
        db = DatabaseManager(args.db)
        print(f"Database: {args.db}")
        print(f"Total Telemetry Records: {db.count_records()}")
        print(f"Unexported Records: {len(db.get_unexported_records())}")
    else:
        run_gui(args.db)

if __name__ == "__main__":
    main()
