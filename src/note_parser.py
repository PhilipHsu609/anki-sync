"""LeetCode note parser for extracting problem details."""

import logging
import re
from pathlib import Path
from urllib.parse import quote

import yaml

from .markdown_utils import convert_markdown_to_html, convert_algorithm_to_html, convert_derivation_to_html


class LeetCodeNote:
    """Parser for LeetCode problem notes."""

    def __init__(self, file_path: Path, config: dict):
        self.file_path = file_path
        self.config = config
        self.frontmatter: dict = {}
        self.content: str = ""
        self.key_insight: str = ""

    def parse(self):
        """Parse the markdown file."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

        # Extract frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', full_content, re.DOTALL)
        if frontmatter_match:
            self.frontmatter = yaml.safe_load(frontmatter_match.group(1)) or {}
            self.content = full_content[frontmatter_match.end():]
        else:
            self.content = full_content

        # Extract key insight from callout
        callout_match = re.search(
            r'>\s*\[!tip\]-?\s*What\'s the trick\?\s*\n>\s*(.*?)(?:\n>|(?:\n(?!>)))',
            self.content,
            re.DOTALL
        )
        if callout_match:
            self.key_insight = callout_match.group(1).strip().replace('> ', '')

    def extract_problem_number(self) -> str:
        """Extract problem number from filename."""
        match = re.match(r'(\d+)\.', self.file_path.name)
        return match.group(1) if match else ""

    def extract_problem_title(self) -> str:
        """Extract problem title from filename."""
        match = re.match(r'\d+\.\s+(.+)\.md$', self.file_path.name)
        return match.group(1) if match else ""

    def extract_tags(self) -> list[str]:
        """Extract pattern tags from frontmatter based on configured prefixes."""
        tags = self.frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]

        tag_prefixes = self.config['sync']['tag_prefixes']
        pattern_tags = [
            tag for tag in tags
            if any(prefix in tag for prefix in tag_prefixes)
        ]

        return pattern_tags[:self.config['card']['max_tags_display']]

    def extract_leetcode_link(self) -> str:
        """Extract LeetCode URL."""
        if match := re.search(r'\[LeetCode\]\((https://leetcode\.com/[^)]+)\)', self.content):
            return match.group(1)
        return ""

    def extract_complexity(self) -> str:
        """Extract complexity from ## Complexity section."""
        if match := re.search(
            r'##\s+Complexity\s*\n(.*?)(?:\n\s*##|\n\s*```|\Z)',
            self.content,
            re.DOTALL
        ):
            complexity_text = re.sub(r'\*\*|\`', '', match.group(1).strip())
            return re.sub(r'\s+', ' ', complexity_text)
        return ""

    def extract_algorithm(self) -> str:
        """Extract algorithm steps from ## Algorithm section."""
        if match := re.search(
            r'##\s+Algorithm\s*\n(.*?)(?:\n\s*##|\n\s*```|\Z)',
            self.content,
            re.DOTALL
        ):
            return re.sub(r'\n\s*\n\s*\n', '\n\n', match.group(1).strip())
        return ""

    def extract_derivation(self) -> str:
        """Extract derivation section (optional for math-heavy problems)."""
        if match := re.search(
            r'##\s+Derivation\s*\n(.*?)(?:\n\s*##|\Z)',
            self.content,
            re.DOTALL
        ):
            deriv_text = re.sub(r'<!--.*?-->', '', match.group(1), flags=re.DOTALL).strip()
            return deriv_text if deriv_text and not deriv_text.isspace() else ""
        return ""

    def should_sync(self) -> bool:
        """Check if this note should be synced to Anki."""
        if not self.extract_leetcode_link():
            return False

        exclude_tags = self.config['sync']['exclude_tags']
        if exclude_tags:
            note_tags = self.frontmatter.get('tags', [])
            if isinstance(note_tags, str):
                note_tags = [note_tags]

            for tag in note_tags:
                if tag in exclude_tags:
                    return False

        return True

    def to_anki_fields(self, leetcode_fetcher=None) -> dict[str, str]:
        """Convert note to Anki fields."""
        vault_name = self.config['obsidian']['vault_name']
        vault_path = self.config['obsidian']['vault_path']

        relative_path = str(self.file_path.relative_to(vault_path))
        obsidian_link = f"obsidian://open?vault={quote(vault_name)}&file={quote(relative_path)}"

        problem_number = self.extract_problem_number()
        problem_title = self.extract_problem_title()
        leetcode_url = self.extract_leetcode_link()

        # Format pattern tags (strip prefixes)
        tags = self.extract_tags()
        tag_prefixes = self.config['sync']['tag_prefixes']

        display_tags = []
        for tag in tags:
            for prefix in tag_prefixes:
                if tag.startswith(prefix):
                    tag = tag[len(prefix):]
                    break
            display_tags.append(tag)

        pattern_tags_html = ' '.join(f'<span class="pattern-tag">{tag}</span>' for tag in display_tags)

        pattern_tags_front = pattern_tags_html if self.config['card']['show_tags'] else ""
        pattern_tags_back = pattern_tags_html

        # Fetch problem details from LeetCode
        problem_description = ""
        problem_examples = ""
        problem_constraints = ""

        if leetcode_url and leetcode_fetcher:
            logging.info(f"Fetching problem details from LeetCode: {leetcode_url}")
            try:
                problem_data = leetcode_fetcher.fetch_problem(leetcode_url)

                if problem_data:
                    # LeetCode API returns HTML directly
                    problem_description = problem_data.get('description', '')

                    # Format examples with headers
                    examples = problem_data.get('examples', [])
                    if examples:
                        example_blocks = []
                        for ex in examples[:2]:
                            block = f'''<div class="example-block">
    <div class="example-header">Example {ex['number']}:</div>
    <div class="example-content">{ex['html']}</div>
</div>'''
                            example_blocks.append(block)
                        problem_examples = '\n'.join(example_blocks)

                    # Constraints are already in <li> format, just wrap in <ul>
                    constraints_html = problem_data.get('constraints', '')
                    if constraints_html:
                        problem_constraints = f'<ul>\n{constraints_html}\n</ul>'

                    logging.info("Successfully fetched problem details")
                else:
                    logging.warning("Could not fetch problem details from LeetCode")

            except Exception as e:
                logging.warning(f"Failed to fetch problem details: {e}")

        # Extract and convert markdown content to HTML
        key_insight_md = self.key_insight or "No key insight provided"
        key_insight_html = convert_markdown_to_html(key_insight_md)

        derivation_md = self.extract_derivation()
        derivation_html = convert_derivation_to_html(derivation_md) if derivation_md else ""

        algorithm_md = self.extract_algorithm() or "No algorithm steps provided"
        algorithm_html = convert_algorithm_to_html(algorithm_md)

        complexity_md = self.extract_complexity() or "Not specified"
        complexity_html = convert_markdown_to_html(complexity_md)

        display_leetcode_link = leetcode_url if self.config['card']['show_leetcode_link'] else ""

        return {
            "ProblemNumber": problem_number,
            "ProblemTitle": problem_title,
            "ProblemDescription": problem_description,
            "ProblemExamples": problem_examples,
            "ProblemConstraints": problem_constraints,
            "PatternTagsFront": pattern_tags_front,
            "PatternTagsBack": pattern_tags_back,
            "KeyInsight": key_insight_html,
            "Derivation": derivation_html,
            "Algorithm": algorithm_html,
            "Complexity": complexity_html,
            "LeetCodeLink": display_leetcode_link,
            "ObsidianLink": obsidian_link
        }
