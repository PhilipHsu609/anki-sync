"""Markdown to HTML converter for Anki cards."""

import re
import markdown


def convert_markdown_to_html(text: str) -> str:
    """
    Convert markdown text to HTML suitable for Anki cards.
    Handles LaTeX math, lists, code blocks, and other formatting.
    """
    if not text or not text.strip():
        return ""

    # Protect LaTeX math from markdown processing and convert to Anki format
    # Input: $...$ and $$...$$
    # Output: \(...\) and \[...\] (Anki's MathJax format)
    math_placeholders = []

    def save_display_math(match):
        idx = len(math_placeholders)
        # Convert $$...$$ to \[...\] for Anki
        content = match.group(1)
        math_placeholders.append(f'\\[{content}\\]')
        return f"XMATHX{idx}XMATHX"

    def save_inline_math(match):
        idx = len(math_placeholders)
        # Convert $...$ to \(...\) for Anki
        content = match.group(1)
        math_placeholders.append(f'\\({content}\\)')
        return f"XMATHX{idx}XMATHX"

    # Save display math first ($$...$$)
    text = re.sub(r'\$\$(.*?)\$\$', save_display_math, text, flags=re.DOTALL)
    # Then inline math ($...$)
    text = re.sub(r'\$([^\$\n]+?)\$', save_inline_math, text)

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'extra',          # Tables, footnotes, abbreviations, etc.
        'sane_lists',     # Better list handling
        'fenced_code',    # ```code blocks```
    ])

    html = md.convert(text)

    # Restore LaTeX math in Anki format
    for i, math_expr in enumerate(math_placeholders):
        placeholder = f"XMATHX{i}XMATHX"
        html = html.replace(placeholder, math_expr)

    return html


def convert_algorithm_to_html(text: str) -> str:
    """
    Convert algorithm markdown to HTML with proper formatting.
    Handles numbered lists and nested structures.
    """
    if not text or not text.strip():
        return ""

    # Algorithms often have numbered lists with nested items
    # The markdown converter should handle this, but we can add custom styling
    html = convert_markdown_to_html(text)

    # Add custom class for algorithm lists
    html = html.replace('<ol>', '<ol class="algorithm-steps">')
    html = html.replace('<ul>', '<ul class="algorithm-items">')

    return html


def convert_derivation_to_html(text: str) -> str:
    """
    Convert derivation markdown to HTML.
    Handles mathematical notation and lists.
    """
    if not text or not text.strip():
        return ""

    html = convert_markdown_to_html(text)

    # Add custom class for derivation lists
    html = html.replace('<ol>', '<ol class="derivation-steps">')
    html = html.replace('<ul>', '<ul class="derivation-items">')

    return html
