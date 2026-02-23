"""
PDF Loader Module
Loads PDF files from the data/pdfs directory
"""
import os
from pathlib import Path
from typing import List, Dict
import pdfplumber


def load_pdfs(pdf_directory: str) -> List[Dict[str, str]]:
    """
    Load all PDF files from the specified directory

    Args:
        pdf_directory: Path to directory containing PDF files

    Returns:
        List of dictionaries containing PDF metadata and content
    """
    pdf_dir = Path(pdf_directory)

    if not pdf_dir.exists():
        raise ValueError(f"Directory {pdf_directory} does not exist")

    pdf_files = list(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}")
        return []

    print(f"Found {len(pdf_files)} PDF files")

    documents = []

    for pdf_path in pdf_files:
        print(f"Loading: {pdf_path.name}")
        try:
            text_content = extract_text_from_pdf(pdf_path)

            documents.append({
                "filename": pdf_path.name,
                "filepath": str(pdf_path),
                "content": text_content
            })

            print(f"  ✓ Loaded {len(text_content)} characters")

        except Exception as e:
            print(f"  ✗ Error loading {pdf_path.name}: {str(e)}")
            continue

    return documents


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text content from a PDF file

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content
    """
    text_content = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                text_content.append(f"--- Page {page_num} ---\n{text}")

    return "\n\n".join(text_content)
