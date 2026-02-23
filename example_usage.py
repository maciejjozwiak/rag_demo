#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the RAG system
"""
from src.backend.pdf_loader import load_pdfs
from src.backend.converter import convert_to_markdown
from src.backend.cleaner import clean_markdown
from src.backend.vectorize import VectorDB
from src.utils.config import PDF_DIR


def example_processing():
    """Example: Process PDFs and query the database"""

    # Load PDFs
    print("Loading PDFs...")
    documents = load_pdfs(PDF_DIR)

    if not documents:
        print("No PDFs found. Please add PDFs to data/pdfs/")
        return

    # Convert to markdown
    print("\nConverting to markdown...")
    for doc in documents:
        doc = convert_to_markdown(doc)

    # Clean markdown
    print("Cleaning markdown...")
    for doc in documents:
        doc = clean_markdown(doc)

    # Create vector database
    print("\nCreating vector database...")
    db = VectorDB()
    db.add_documents(documents)

    # Query example
    print("\n" + "=" * 60)
    print("Example Queries:")
    print("=" * 60)

    queries = [
        "What are the main topics discussed?",
        "Tell me about the methodology",
        "What are the conclusions?"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        results = db.query(query, n_results=3)

        if results['documents'][0]:
            for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                print(f"\n  Result {i}: {meta.get('filename', 'Unknown')}")
                print(f"  {doc[:150]}...")


def example_query_only():
    """Example: Query existing database"""

    db = VectorDB()
    stats = db.get_collection_stats()

    print(f"Database Stats: {stats['document_count']} chunks")

    if stats['document_count'] == 0:
        print("Database is empty. Run process_pdfs.py first.")
        return

    query = "machine learning"
    print(f"\nSearching for: '{query}'")

    results = db.query(query, n_results=5)

    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\n{i}. {meta.get('filename', 'Unknown')} (Chunk {meta.get('chunk_index', 0) + 1})")
        print(f"   {doc[:200]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "query":
        example_query_only()
    else:
        example_processing()
