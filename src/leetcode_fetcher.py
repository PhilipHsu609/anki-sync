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
        content
        exampleTestcases
        topicTags {
          name
        }
        hints
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
        # Use the entire content HTML as-is from LeetCode
        # The content already contains description, examples, and constraints in proper HTML
        content_html = question.get('content', '')

        return {
            'number': question.get('questionId', ''),
            'title': question.get('title', ''),
            'titleSlug': question.get('titleSlug', ''),
            'difficulty': question.get('difficulty', 'Medium'),
            'content': content_html,
            'tags': [tag['name'] for tag in question.get('topicTags', [])],
            'hints': question.get('hints', [])
        }

def test():
    """Test the fetcher."""
    logging.basicConfig(level=logging.INFO)

    fetcher = LeetCodeFetcher()

    # Test with a known problem
    url = "https://leetcode.com/problems/partition-to-k-equal-sum-subsets"
    print(f"Fetching: {url}")

    data = fetcher.fetch_problem(url)

    if data:
        print(f"\nNumber: {data['number']}")
        print(f"Title: {data['title']}")
        print(f"Difficulty: {data['difficulty']}")
        print(f"Tags: {', '.join(data['tags'])}")
        print(f"\nContent (first 200 chars):\n{data['content'][:200]}...")
        print(f"\nContent length: {len(data['content'])}")
    else:
        print("Failed to fetch problem")


if __name__ == '__main__':
    test()
