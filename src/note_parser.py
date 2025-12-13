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

        # Extract frontmatter (YAML between --- markers)
        if full_content.startswith('---'):
            parts = full_content.split('---', 2)
            if len(parts) >= 3:
                try:
                    self.frontmatter = yaml.safe_load(parts[1]) or {}
                    self.content = parts[2].lstrip('\n')
                except yaml.YAMLError as e:
                    logging.warning(f"Failed to parse frontmatter in {self.file_path.name}: {e}")
                    self.content = full_content
            else:
                self.content = full_content
        else:
            self.content = full_content

        # Extract key insight from callout (more flexible pattern)
        # Matches: > [!tip] What's the trick?
        #          > Key insight text here
        #          > Can be multiple lines
        self.key_insight = self._extract_callout_content()

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
        """
        Extract LeetCode URL from note.
        Looks for [LeetCode](url) or [LC](url) format.
        """
        # Try common patterns
        patterns = [
            r'\[LeetCode\]\((https://leetcode\.com/[^)]+)\)',
            r'\[LC\]\((https://leetcode\.com/[^)]+)\)',
            r'(https://leetcode\.com/problems/[^\s\)]+)',  # Bare URL
        ]

        for pattern in patterns:
            if match := re.search(pattern, self.content, re.IGNORECASE):
                return match.group(1)

        return ""

    def _extract_callout_content(self) -> str:
        """
        Extract content from Obsidian callout block.
        Handles: > [!tip] What's the trick? or similar variants.
        """
        lines = self.content.split('\n')
        callout_lines = []
        in_callout = False
        callout_started = False

        for line in lines:
            # Start of callout: > [!tip] or > [!note] etc.
            if re.match(r'>\s*\[!(?:tip|note|info)\]', line, re.IGNORECASE):
                in_callout = True
                callout_started = True
                continue

            # Inside callout
            if in_callout:
                if line.startswith('>'):
                    # Remove leading > and whitespace
                    content = line.lstrip('>').strip()
                    if content:
                        callout_lines.append(content)
                else:
                    # End of callout (line doesn't start with >)
                    break

        return '\n'.join(callout_lines) if callout_lines else ""

    def _extract_section(self, heading: str) -> str:
        """
        Extract content from a markdown section by heading.
        More robust than regex - splits on ## headings and finds the right one.
        """
        # Split content into sections by ## headings
        sections = re.split(r'\n##\s+', '\n' + self.content)

        for section in sections:
            lines = section.split('\n', 1)
            if not lines:
                continue

            section_heading = lines[0].strip()
            section_content = lines[1] if len(lines) > 1 else ""

            # Case-insensitive match for the heading
            if section_heading.lower() == heading.lower():
                # Clean up the content
                content = section_content.strip()
                # Remove HTML comments
                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
                # Remove code fences that might appear before next section
                content = re.split(r'\n```', content)[0].strip()
                return content

        return ""

    def extract_complexity(self) -> str:
        """Extract complexity from ## Complexity section."""
        return self._extract_section("Complexity")

    def extract_algorithm(self) -> str:
        """Extract algorithm steps from ## Algorithm section."""
        return self._extract_section("Algorithm")

    def extract_derivation(self) -> str:
        """Extract derivation from ## Derivation section."""
        return self._extract_section("Derivation")

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
        problem_content = ""

        if leetcode_url and leetcode_fetcher:
            logging.info(f"Fetching problem details from LeetCode: {leetcode_url}")
            try:
                problem_data = leetcode_fetcher.fetch_problem(leetcode_url)

                if problem_data:
                    # LeetCode API returns complete HTML with description, examples, and constraints
                    problem_content = problem_data.get('content', '')
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
            "ProblemContent": problem_content,
            "PatternTagsFront": pattern_tags_front,
            "PatternTagsBack": pattern_tags_back,
            "KeyInsight": key_insight_html,
            "Derivation": derivation_html,
            "Algorithm": algorithm_html,
            "Complexity": complexity_html,
            "LeetCodeLink": display_leetcode_link,
            "ObsidianLink": obsidian_link
        }
