"""AnkiConnect API client for managing Anki decks and cards."""

import logging
from pathlib import Path
from typing import Any

import requests


def load_template(filename: str) -> str:
    """Load template file from templates directory."""
    template_path = Path(__file__).parent.parent / 'templates' / filename
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


CARD_CSS = load_template('card_style.css')
CARD_FRONT = load_template('card_front.html')
CARD_BACK = load_template('card_back.html')


class AnkiConnect:
    """Client for interacting with AnkiConnect API."""

    def __init__(self, url: str, api_key: str | None = None):
        self.url = url
        self.api_key = api_key
        self.version = 6

    def invoke(self, action: str, **params) -> Any:
        """Invoke AnkiConnect API action."""
        payload = {
            "action": action,
            "version": self.version,
            "params": params,
        }
        if self.api_key:
            payload["key"] = self.api_key

        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"AnkiConnect request failed: {e}")
            raise

        if error := result.get("error"):
            logging.error(f"AnkiConnect error: {error}")
            raise Exception(error)

        return result.get("result")

    def test_connection(self) -> bool:
        """Test connection to AnkiConnect."""
        try:
            version = self.invoke("version")
            logging.info(f"Connected to AnkiConnect (API version {version})")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to AnkiConnect: {e}")
            return False

    def create_deck(self, deck_name: str):
        """Create deck if it doesn't exist."""
        return self.invoke("createDeck", deck=deck_name)

    def model_exists(self, model_name: str) -> bool:
        """Check if model exists."""
        try:
            models = self.invoke("modelNames")
            return model_name in models
        except Exception:
            return False

    def get_model_field_names(self, model_name: str) -> list[str]:
        """Get field names for a model."""
        try:
            return self.invoke("modelFieldNames", modelName=model_name)
        except Exception:
            return []

    def add_model_field(self, model_name: str, field_name: str, index: int | None = None):
        """Add a field to an existing model."""
        try:
            self.invoke("modelFieldAdd",
                       modelName=model_name,
                       fieldName=field_name,
                       index=index)
            logging.info(f"Added field '{field_name}' to model '{model_name}'")
        except Exception as e:
            logging.warning(f"Could not add field '{field_name}': {e}")

    def update_model_styling(self, model_name: str, css: str):
        """Update model CSS styling."""
        try:
            self.invoke("updateModelStyling", model={"name": model_name, "css": css})
            logging.info(f"Updated styling for model '{model_name}'")
        except Exception as e:
            logging.warning(f"Could not update styling: {e}")

    def update_model_templates(self, model_name: str, front: str, back: str):
        """Update model card templates."""
        try:
            templates = {
                "LeetCode Card": {
                    "Front": front,
                    "Back": back
                }
            }
            self.invoke("updateModelTemplates", model={"name": model_name, "templates": templates})
            logging.info(f"Updated templates for model '{model_name}'")
        except Exception as e:
            logging.warning(f"Could not update templates: {e}")

    def create_or_update_model(self, model_name: str):
        """Create or update the LeetCode note type."""
        expected_fields = [
            "ProblemNumber",
            "ProblemTitle",
            "ProblemContent",
            "PatternTagsFront",
            "PatternTagsBack",
            "KeyInsight",
            "Derivation",
            "Algorithm",
            "Complexity",
            "LeetCodeLink",
            "ObsidianLink"
        ]

        if self.model_exists(model_name):
            logging.info(f"Model '{model_name}' exists, checking fields...")

            current_fields = self.get_model_field_names(model_name)
            for i, field_name in enumerate(expected_fields):
                if field_name not in current_fields:
                    logging.info(f"Adding missing field: {field_name}")
                    self.add_model_field(model_name, field_name, index=i)

            self.update_model_styling(model_name, CARD_CSS)
            self.update_model_templates(model_name, CARD_FRONT, CARD_BACK)
        else:
            model_config = {
                "modelName": model_name,
                "inOrderFields": expected_fields,
                "css": CARD_CSS,
                "cardTemplates": [
                    {
                        "Name": "LeetCode Card",
                        "Front": CARD_FRONT,
                        "Back": CARD_BACK
                    }
                ]
            }

            try:
                self.invoke("createModel", **model_config)
                logging.info(f"Created model '{model_name}'")
            except Exception as e:
                logging.error(f"Could not create model: {e}")

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: dict[str, str],
        tags: list[str] | None = None
    ) -> int | None:
        """Add note to Anki."""
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or [],
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
            },
        }

        try:
            return self.invoke("addNote", note=note)
        except Exception as e:
            logging.error(f"Failed to add note: {e}")
            return None

    def update_note(self, note_id: int, fields: dict[str, str]):
        """Update existing note fields."""
        self.invoke("updateNoteFields", note={"id": note_id, "fields": fields})

    def find_notes(self, query: str) -> list[int]:
        """Find notes matching query."""
        return self.invoke("findNotes", query=query)
