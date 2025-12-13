"""Simple, reliable Markdown to HTML converter for Anki cards."""

import html
import re


def convert_markdown_to_html(text: str) -> str:
    """
    Convert markdown text to HTML using simple, reliable patterns.
    Handles: LaTeX math, bold, italic, code, links, lists.

    This is intentionally simple to avoid fragile parsing.
    """
    if not text or not text.strip():
        return ""

    # Start with HTML-escaped text for safety
    result = html.escape(text)

    # 1. Protect and convert LaTeX math (before other processing)
    # Display math: $$...$$ → \[...\]
    result = re.sub(
        r'\$\$(.*?)\$\$',
        lambda m: f'\\[{m.group(1)}\\]',
        result,
        flags=re.DOTALL
    )

    # Inline math: $...$ → \(...\)
    result = re.sub(
        r'\$([^\$\n]+?)\$',
        lambda m: f'\\({m.group(1)}\\)',
        result
    )

    # 2. Convert markdown formatting
    # Bold: **text** or __text__
    result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)
    result = re.sub(r'__(.+?)__', r'<strong>\1</strong>', result)

    # Italic: *text* or _text_ (but not in middle of words)
    result = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'<em>\1</em>', result)
    result = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', result)

    # Inline code: `code`
    result = re.sub(r'`([^`]+?)`', r'<code>\1</code>', result)

    # Links: [text](url)
    result = re.sub(r'\[([^\]]+?)\]\(([^\)]+?)\)', r'<a href="\2">\1</a>', result)

    # 3. Convert lists (simple approach)
    lines = result.split('\n')
    in_list = False
    list_type = None
    processed_lines = []

    for line in lines:
        # Ordered list item: 1. text
        if re.match(r'^\d+\.\s+', line):
            if not in_list or list_type != 'ol':
                if in_list:
                    processed_lines.append(f'</{list_type}>')
                processed_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            item = re.sub(r'^\d+\.\s+', '', line)
            processed_lines.append(f'<li>{item}</li>')

        # Unordered list item: - text or * text
        elif re.match(r'^[\-\*]\s+', line):
            if not in_list or list_type != 'ul':
                if in_list:
                    processed_lines.append(f'</{list_type}>')
                processed_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            item = re.sub(r'^[\-\*]\s+', '', line)
            processed_lines.append(f'<li>{item}</li>')

        # Not a list item
        else:
            if in_list:
                processed_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None

            # Empty lines become line breaks
            if not line.strip():
                processed_lines.append('<br>')
            else:
                processed_lines.append(f'<p>{line}</p>')

    # Close any open list
    if in_list:
        processed_lines.append(f'</{list_type}>')

    result = '\n'.join(processed_lines)

    # 4. Clean up excessive breaks and empty paragraphs
    result = re.sub(r'<p>\s*</p>', '', result)
    result = re.sub(r'(<br>\s*){3,}', '<br><br>', result)

    return result.strip()


def convert_algorithm_to_html(text: str) -> str:
    """
    Convert algorithm markdown to HTML with algorithm-specific styling.
    """
    if not text or not text.strip():
        return ""

    html = convert_markdown_to_html(text)

    # Add custom classes for styling
    html = html.replace('<ol>', '<ol class="algorithm-steps">')
    html = html.replace('<ul>', '<ul class="algorithm-items">')

    return html


def convert_derivation_to_html(text: str) -> str:
    """
    Convert derivation markdown to HTML with derivation-specific styling.
    """
    if not text or not text.strip():
        return ""

    html = convert_markdown_to_html(text)

    # Add custom classes for styling
    html = html.replace('<ol>', '<ol class="derivation-steps">')
    html = html.replace('<ul>', '<ul class="derivation-items">')

    return html
