"""Sync manager for coordinating Obsidian to Anki synchronization."""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from .leetcode_fetcher import LeetCodeFetcher
from .anki_client import AnkiConnect
from .note_parser import LeetCodeNote


class SyncManager:
    """Manages syncing between Obsidian and Anki."""

    def __init__(self, config_path: Path):
        self.config = self.load_config(config_path)

        anki_config = self.config['anki']
        self.anki = AnkiConnect(
            url=anki_config['url'],
            api_key=anki_config.get('api_key')
        )

        self.deck_name = anki_config['deck_name']
        self.model_name = anki_config['model_name']
        self.leetcode_fetcher = LeetCodeFetcher()

    @staticmethod
    def load_config(config_path: Path) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def setup_anki(self):
        """Setup Anki deck and note type."""
        logging.info("Setting up Anki deck and note type...")
        self.anki.create_deck(self.deck_name)
        self.anki.create_or_update_model(self.model_name)

    def sync_note(self, note_path: Path) -> bool:
        """
        Sync a single note to Anki.

        Returns:
            True if synced successfully, False if skipped or failed
        """
        try:
            note = LeetCodeNote(note_path, self.config)
            note.parse()

            if not note.should_sync():
                logging.debug(f"Skipping {note_path.name} - excluded or missing LeetCode URL")
                return False

            problem_title = note.extract_problem_title()

            logging.info(f"Syncing: {problem_title}")

            # Fetch and build Anki fields
            fields = note.to_anki_fields(self.leetcode_fetcher)

            # Check if card already exists
            query = f'deck:"{self.deck_name}" ProblemTitle:"{fields["ProblemTitle"]}"'
            existing_notes = self.anki.find_notes(query)

            if existing_notes:
                self.anki.update_note(existing_notes[0], fields)
                logging.info(f"✓ Updated: {fields['ProblemTitle']}")
            else:
                tags = note.extract_tags()
                self.anki.add_note(self.deck_name, self.model_name, fields, tags)
                logging.info(f"✓ Created: {fields['ProblemTitle']}")

            return True

        except Exception as e:
            logging.error(f"✗ Failed to sync {note_path.name}: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return False

    def sync_all(self, problems_dir: Path, days: int | None = None) -> dict[str, int]:
        """
        Sync all LeetCode problems in a directory.

        Args:
            problems_dir: Directory containing LeetCode note files
            days: If specified, only sync files modified in the last N days

        Returns:
            Dictionary with sync statistics
        """
        stats = {"synced": 0, "skipped": 0, "failed": 0}

        # Find all markdown files
        md_files = list(problems_dir.glob("*.md"))

        # Filter by modification date if specified
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            md_files = [
                f for f in md_files
                if datetime.fromtimestamp(f.stat().st_mtime) > cutoff_date
            ]
            logging.info(f"Found {len(md_files)} notes modified in last {days} days")
        else:
            logging.info(f"Found {len(md_files)} notes to process")

        # Sync each file
        for i, md_file in enumerate(md_files, 1):
            logging.info(f"[{i}/{len(md_files)}] Processing {md_file.name}")

            try:
                if self.sync_note(md_file):
                    stats["synced"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                logging.error(f"Unexpected error processing {md_file.name}: {e}")
                stats["failed"] += 1

        return stats
