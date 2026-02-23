#!/usr/bin/env python3
"""
Main script to process PDFs and create vector database

This script:
1. Loads PDFs from data/pdfs directory
2. Converts them to markdown
3. Cleans the markdown content
4. Creates ChromaDB vector database
"""
import argparse
from pathlib import Path
from src.backend.pdf_loader import load_pdfs
from src.backend.converter import convert_to_markdown
from src.backend.cleaner import clean_markdown
from src.backend.vectorize import create_vector_db
from src.utils.config import PDF_DIR, PROCESSED_DIR


def save_processed_files(documents):
    """Save processed markdown files to disk"""
    print("\nSaving processed files...")

    for doc in documents:
        filename = Path(doc["filename"]).stem
        output_path = PROCESSED_DIR / f"{filename}.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc.get("cleaned_markdown", doc.get("markdown", "")))

        print(f"  ✓ Saved: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Process PDFs and create vector database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the vector database before processing"
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default=str(PDF_DIR),
        help=f"Directory containing PDF files (default: {PDF_DIR})"
    )
    parser.add_argument(
        "--save-markdown",
        action="store_true",
        help="Save processed markdown files to data/processed/"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("PDF Processing and Vector Database Creation")
    print("=" * 60)

    # Step 1: Load PDFs
    print("\n[1/4] Loading PDFs...")
    documents = load_pdfs(args.pdf_dir)

    if not documents:
        print("No PDFs to process. Exiting.")
        return

    # Step 2: Convert to Markdown
    print(f"\n[2/4] Converting {len(documents)} PDFs to markdown...")
    for i, doc in enumerate(documents, 1):
        print(f"  [{i}/{len(documents)}] {doc['filename']}")
        documents[i-1] = convert_to_markdown(doc)

    # Step 3: Clean Markdown
    print(f"\n[3/4] Cleaning markdown content...")
    for i, doc in enumerate(documents, 1):
        print(f"  [{i}/{len(documents)}] {doc['filename']}")
        documents[i-1] = clean_markdown(doc)

    # Optional: Save processed files
    if args.save_markdown:
        save_processed_files(documents)

    # Step 4: Create Vector Database
    print(f"\n[4/4] Creating vector database...")
    if args.reset:
        print("  (Resetting existing database)")

    vector_db = create_vector_db(documents, reset=args.reset)

    print("\n" + "=" * 60)
    print("✓ Processing complete!")
    print("=" * 60)
    print("\nYou can now use the CLI to query your documents:")
    print("  python -m src.cli.query_cli")


if __name__ == "__main__":
    main()
