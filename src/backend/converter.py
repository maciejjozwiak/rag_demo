"""
PDF to Markdown Converter Module
Converts PDF content to markdown format
"""
import re
from typing import Dict


def convert_to_markdown(document: Dict[str, str]) -> Dict[str, str]:
    """
    Convert PDF content to markdown format

    Args:
        document: Dictionary containing PDF content and metadata

    Returns:
        Document with markdown-formatted content
    """
    content = document["content"]
    filename = document["filename"]

    # Add document header
    markdown = f"# {filename}\n\n"

    # Convert page separators to markdown headers
    content = re.sub(r'--- Page (\d+) ---', r'## Page \1', content)

    # Normalize whitespace while preserving paragraph breaks
    lines = content.split('\n')
    processed_lines = []

    for line in lines:
        # Keep headers and empty lines
        if line.startswith('#') or line.strip() == '':
            processed_lines.append(line)
        else:
            # Clean up extra spaces in regular text
            processed_lines.append(' '.join(line.split()))

    markdown += '\n'.join(processed_lines)

    # Remove excessive blank lines (more than 2 consecutive)
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return {
        **document,
        "markdown": markdown
    }
