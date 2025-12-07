#!/usr/bin/env python3
"""
LeetCode Problem Fetcher

Fetches problem description, examples, and constraints from LeetCode.
Uses GraphQL API for reliable data extraction.
"""

import logging
import re

import requests


class LeetCodeFetcher:
    """Fetches problem data from LeetCode."""

    GRAPHQL_URL = "https://leetcode.com/graphql"

    QUERY = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        title
        titleSlug
        difficulty
        content
        exampleTestcases
        topicTags {
          name
        }
        hints
        companyTagStats
      }
    }
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_problem(self, leetcode_url: str) -> dict | None:
        """
        Fetch problem data from LeetCode URL.

        Args:
            leetcode_url: Full LeetCode problem URL

        Returns:
            Dictionary with problem data or None if failed
        """
        # Extract title slug from URL
        if not (title_slug := self._extract_title_slug(leetcode_url)):
            logging.error(f"Could not extract title slug from URL: {leetcode_url}")
            return None

        # Fetch from GraphQL API
        try:
            response = self.session.post(
                self.GRAPHQL_URL,
                json={
                    "query": self.QUERY,
                    "variables": {"titleSlug": title_slug}
                },
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            
            print(data)

            if 'errors' in data:
                logging.error(f"GraphQL error: {data['errors']}")
                return None

            question = data.get('data', {}).get('question')
            if not question:
                logging.error("No question data returned")
                return None

            # Parse and return
            return self._parse_question_data(question)

        except requests.RequestException as e:
            logging.error(f"Failed to fetch from LeetCode: {e}")
            return None

    def _extract_title_slug(self, url: str) -> str | None:
        """Extract title slug from LeetCode URL."""
        # https://leetcode.com/problems/sliding-window-maximum/
        if match := re.search(r'/problems/([^/]+)/?', url):
            return match.group(1)
        return None

    def _parse_question_data(self, question: dict) -> dict:
        """Parse GraphQL response into structured data."""
        content_html = question.get('content', '')

        # Extract HTML sections directly from LeetCode's API
        description_html = self._extract_description_html(content_html)
        examples_html = self._extract_examples_html(content_html)
        constraints_html = self._extract_constraints_html(content_html)

        return {
            'number': question.get('questionId', ''),
            'title': question.get('title', ''),
            'titleSlug': question.get('titleSlug', ''),
            'difficulty': question.get('difficulty', 'Medium'),
            'description': description_html,
            'examples': examples_html,
            'constraints': constraints_html,
            'tags': [tag['name'] for tag in question.get('topicTags', [])],
            'hints': question.get('hints', [])
        }

    def _extract_description_html(self, html: str) -> str:
        """Extract problem description HTML (content before first example)."""
        # Split at first example
        pattern = r'<p><strong[^>]*class="example"[^>]*>Example\s+\d+:'
        parts = re.split(pattern, html, maxsplit=1)
        if len(parts) > 1:
            return parts[0].strip()

        # Fallback: split at constraints
        pattern = r'<p><strong[^>]*>Constraints:</strong></p>'
        parts = re.split(pattern, html, maxsplit=1)
        return parts[0].strip()

    def _extract_examples_html(self, html: str) -> list[dict]:
        """Extract example blocks with HTML intact."""
        examples = []

        # Pattern: <strong class="example">Example X:</strong> ... <div class="example-block">...</div>
        pattern = r'<p><strong[^>]*class="example"[^>]*>\s*Example\s+(\d+):\s*</strong></p>\s*<div class="example-block">(.*?)</div>'

        for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            examples.append({
                'number': int(match.group(1)),
                'html': match.group(2).strip()
            })

        return examples

    def _extract_constraints_html(self, html: str) -> str:
        """Extract constraints HTML (the <ul> with all <li> items)."""
        # Pattern: <strong>Constraints:</strong> followed by <ul>...</ul>
        pattern = r'<p><strong[^>]*>\s*Constraints?:\s*</strong></p>\s*<ul>(.*?)</ul>'

        if match := re.search(pattern, html, re.DOTALL | re.IGNORECASE):
            return match.group(1).strip()

        return ""

def test():
    """Test the fetcher."""
    logging.basicConfig(level=logging.INFO)

    fetcher = LeetCodeFetcher()

    # Test with a known problem
    url = "https://leetcode.com/problems/count-partitions-with-max-min-difference-at-most-k"
    print(f"Fetching: {url}")

    data = fetcher.fetch_problem(url)

    if data:
        print(f"\nNumber: {data['number']}")
        print(f"Title: {data['title']}")
        print(f"Difficulty: {data['difficulty']}")
        print(f"Tags: {', '.join(data['tags'])}")
        print(f"\nDescription (first 200 chars):\n{data['description'][:200]}...")
        print(f"\nExamples: {len(data['examples'])}")
        print(f"Constraints length: {len(data['constraints'])}")

        if data['examples']:
            print("\n" + "="*60)
            print("FIRST EXAMPLE HTML:")
            print("="*60)
            print(data['examples'][0]['html'][:300])
    else:
        print("Failed to fetch problem")


if __name__ == '__main__':
    test()
