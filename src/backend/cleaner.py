"""
Markdown Cleaner Module
Cleans and preprocesses markdown content
"""
import re
from typing import Dict, List


def clean_markdown(document: Dict[str, str]) -> Dict[str, str]:
    """
    Clean and preprocess markdown content

    Args:
        document: Dictionary containing markdown content

    Returns:
        Document with cleaned markdown
    """
    markdown = document.get("markdown", document.get("content", ""))

    # Remove special characters that might cause issues
    markdown = remove_special_characters(markdown)

    # Fix common OCR errors
    markdown = fix_ocr_errors(markdown)

    # Normalize spacing
    markdown = normalize_spacing(markdown)

    return {
        **document,
        "cleaned_markdown": markdown
    }


def remove_special_characters(text: str) -> str:
    """Remove or replace problematic special characters"""
    # Remove form feed, vertical tab, etc.
    text = re.sub(r'[\f\v]', '', text)

    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    # Fix bullet points
    text = re.sub(r'[•●◦⦿]', '-', text)

    return text


def fix_ocr_errors(text: str) -> str:
    """Fix common OCR errors"""
    # Fix common ligatures
    replacements = {
        'ﬁ': 'fi',
        'ﬂ': 'fl',
        'ﬀ': 'ff',
        'ﬃ': 'ffi',
        'ﬄ': 'ffl',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def normalize_spacing(text: str) -> str:
    """Normalize spacing and line breaks"""
    # Remove trailing spaces
    text = re.sub(r' +\n', '\n', text)

    # Remove leading spaces (except for code blocks)
    lines = text.split('\n')
    normalized_lines = []

    for line in lines:
        if not line.startswith('    '):  # Preserve code blocks
            line = line.lstrip()
        normalized_lines.append(line)

    text = '\n'.join(normalized_lines)

    # Normalize multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks

    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Find the end of this chunk
        end = start + chunk_size

        # If this isn't the last chunk, try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence boundary (. ! ?)
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('! ', start, end),
                text.rfind('? ', start, end)
            )

            if sentence_end > start:
                end = sentence_end + 1
            else:
                # Look for word boundary
                space = text.rfind(' ', start, end)
                if space > start:
                    end = space

        chunks.append(text[start:end].strip())

        # Move start position with overlap
        start = end - overlap

        # Make sure we're making progress
        if start <= 0:
            start = end

    return chunks
