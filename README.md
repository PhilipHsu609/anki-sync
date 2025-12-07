# LeetCode → Anki Sync System

Automated sync from Obsidian LeetCode notes to Anki via AnkiConnect API. Fetches problem descriptions, examples, and constraints directly from LeetCode's GraphQL API and creates beautifully styled flashcards with Nord theme.

---

## Architecture

```
┌─────────────────┐
│ Obsidian Note   │
│ (LeetCode prob) │
└────────┬────────┘
         │
         │ Parse YAML + Content + Fetch from LeetCode API
         ▼
┌─────────────────┐
│  Python Script  │
│  sync_to_anki   │
└────────┬────────┘
         │
         │ HTTP POST (AnkiConnect API)
         ▼
┌─────────────────────────┐      ┌──────────────┐
│ Anki (Local or Remote)  │◄────►│   AnkiWeb    │
│ • AnkiConnect           │      │   (Sync)     │
│ • Nord Theme            │      └──────┬───────┘
│ • MathJax               │             │
└─────────────────────────┘      ┌──────▼───────┐
                                 │ Mobile/Other │
                                 │    Devices   │
                                 └──────────────┘
```

---

## Setup

1. Install AnkiConnect add-on (code: 2055492159)
2. Install Python dependencies: `pip install requests pyyaml markdown`
3. Update `config.yaml` with your Anki URL and vault path

---

## Usage

```bash
python sync_to_anki.py "/path/to/note.md"
```
