#!/usr/bin/env python3
"""
Sync LeetCode notes from Obsidian to Anki via AnkiConnect API.

Usage:
    python sync_to_anki.py <file_path>           # Sync single file
    python sync_to_anki.py --all                 # Sync all problems
    python sync_to_anki.py --recent <days>       # Sync recent problems
"""

import argparse
import logging
from pathlib import Path

from src import SyncManager


def main() -> int:
    """Main entry point for syncing LeetCode notes to Anki."""
    parser = argparse.ArgumentParser(description="Sync LeetCode notes to Anki")
    parser.add_argument("file_path", nargs="?", help="Path to note file")
    parser.add_argument("--all", action="store_true", help="Sync all problems")
    parser.add_argument("--recent", type=int, metavar="DAYS", help="Sync problems modified in last N days")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Load config
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.yaml"

    if not config_path.exists():
        logging.error(f"Config file not found: {config_path}")
        return 1

    # Initialize sync manager
    manager = SyncManager(config_path)

    # Test connection
    if not manager.anki.test_connection():
        logging.error("Could not connect to Anki. Make sure Anki is running with AnkiConnect installed.")
        return 1

    # Setup Anki
    manager.setup_anki()

    # Sync based on arguments
    problems_dir = Path(manager.config['obsidian']['vault_path']) / manager.config['obsidian']['problems_path']

    if args.file_path:
        # Sync single file
        if not (note_path := problems_dir / Path(args.file_path)).exists():
            logging.error(f"File not found: {note_path}")
            return 1

        return 0 if manager.sync_note(note_path) else 1

    if args.all or args.recent:
        # Sync multiple files

        if not problems_dir.exists():
            logging.error(f"Problems directory not found: {problems_dir}")
            return 1

        stats = manager.sync_all(problems_dir, days=args.recent)

        logging.info("\nSync complete:")
        logging.info(f"  Synced: {stats['synced']}")
        logging.info(f"  Skipped: {stats['skipped']}")
        logging.info(f"  Failed: {stats['failed']}")

        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    exit(main())
