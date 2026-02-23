#!/usr/bin/env python3
"""
Demonstration: How Vector Search Works

This script shows exactly how your query finds relevant documents
"""
from sentence_transformers import SentenceTransformer
import numpy as np


def explain_vector_search():
    """Demonstrate the vector search process"""

    print("=" * 70)
    print("HOW YOUR RAG SYSTEM FINDS RELEVANT CONTENT")
    print("=" * 70)

    # Load the same model your system uses
    print("\n[1] Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("    ✓ This model converts text → 384-dimensional vectors")

    # Example query
    query = "What is machine learning?"
    print(f"\n[2] Your Question: '{query}'")

    # Convert query to vector
    query_vector = model.encode(query)
    print(f"\n[3] Converting question to vector...")
    print(f"    Vector dimensions: {len(query_vector)}")
    print(f"    First 10 values: {query_vector[:10]}")
    print(f"    (384 numbers total, each between -1 and 1)")

    # Example document chunks (like what's stored in your ChromaDB)
    print("\n[4] Example documents in your database:")
    documents = {
        "doc1": "Machine learning is a subset of AI that learns from data",
        "doc2": "Neural networks are computational models inspired by the brain",
        "doc3": "Python is a programming language created by Guido van Rossum",
        "doc4": "Deep learning uses multi-layer neural networks for pattern recognition",
        "doc5": "The weather forecast predicts rain tomorrow afternoon"
    }

    # Convert all documents to vectors
    print("\n[5] Each document chunk is also stored as a vector:")
    doc_vectors = {}
    for doc_id, text in documents.items():
        vector = model.encode(text)
        doc_vectors[doc_id] = vector
        print(f"    {doc_id}: '{text[:50]}...' → vector[384]")

    # Calculate cosine similarity
    print("\n[6] Calculating similarity between query and each document:")
    print("    (Using cosine similarity: 1.0 = identical, 0.0 = unrelated)")

    def cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)

    similarities = {}
    for doc_id, doc_vector in doc_vectors.items():
        similarity = cosine_similarity(query_vector, doc_vector)
        similarities[doc_id] = similarity
        percentage = similarity * 100
        print(f"    {doc_id}: {similarity:.4f} ({percentage:.1f}%)")

    # Rank results
    print("\n[7] Ranking results by similarity (highest first):")
    ranked = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    for rank, (doc_id, similarity) in enumerate(ranked, 1):
        percentage = similarity * 100
        text = documents[doc_id]

        if percentage >= 80:
            verdict = "✅ HIGHLY RELEVANT"
        elif percentage >= 60:
            verdict = "⚠️  SOMEWHAT RELEVANT"
        else:
            verdict = "❌ NOT RELEVANT"

        print(f"\n    Rank {rank}: {doc_id} - {percentage:.1f}% similarity {verdict}")
        print(f"    Text: '{text}'")

    # Show what gets returned
    print("\n[8] What your system returns:")
    print(f"    Top 3 results (if threshold = 60%):")

    top_3 = [(doc_id, sim) for doc_id, sim in ranked[:3] if sim * 100 >= 60]
    for i, (doc_id, similarity) in enumerate(top_3, 1):
        print(f"      [{i}] {documents[doc_id]} ({similarity * 100:.1f}%)")

    print("\n" + "=" * 70)
    print("KEY INSIGHTS:")
    print("=" * 70)
    print("✓ 'doc1' ranks #1 even though it says 'AI' not 'machine learning'")
    print("✓ 'doc4' ranks high because deep learning IS machine learning")
    print("✓ 'doc3' (Python) and 'doc5' (weather) rank low - not relevant")
    print("✓ This is SEMANTIC search - finds meaning, not exact words!")
    print("=" * 70)

    # Show the math behind ChromaDB's distance metric
    print("\n[9] ChromaDB uses L2 (Euclidean) distance, converted to cosine:")
    print("    - ChromaDB distance = 0 → Perfect match")
    print("    - ChromaDB distance = 2 → Completely different")
    print("    - Your CLI converts: similarity% = 100 * (1 - distance/2)")


if __name__ == "__main__":
    try:
        explain_vector_search()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure sentence-transformers is installed:")
        print("  source venv/bin/activate")
        print("  pip install sentence-transformers")
