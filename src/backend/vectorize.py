"""
Vector Database Module
Creates and manages vector database for RAG
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from ..utils.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from .cleaner import chunk_text


class VectorDB:
    """Vector database manager using ChromaDB"""

    def __init__(self, persist_directory: Optional[str] = None, collection_name: Optional[str] = None):
        """
        Initialize ChromaDB client

        Args:
            persist_directory: Path to persist the database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or CHROMA_DB_PATH
        self.collection_name = collection_name or CHROMA_COLLECTION_NAME

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        print(f"ChromaDB initialized at: {self.persist_directory}")
        print(f"Collection: {self.collection_name}")

    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the vector database

        Args:
            documents: List of document dictionaries with cleaned_markdown content
        """
        all_chunks = []
        all_metadatas = []
        all_ids = []

        chunk_counter = 0

        for doc in documents:
            content = doc.get("cleaned_markdown", doc.get("markdown", doc.get("content", "")))
            filename = doc.get("filename", "unknown")

            # Split document into chunks
            chunks = chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)

            print(f"Processing {filename}: {len(chunks)} chunks")

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "filename": filename,
                    "filepath": doc.get("filepath", ""),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                all_ids.append(f"{filename}_chunk_{i}")
                chunk_counter += 1

        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))

            self.collection.add(
                documents=all_chunks[i:batch_end],
                metadatas=all_metadatas[i:batch_end],
                ids=all_ids[i:batch_end]
            )

            print(f"  Added chunks {i+1}-{batch_end} / {len(all_chunks)}")

        print(f"✓ Total chunks added to database: {chunk_counter}")

    def query(self, query_text: str, n_results: int = 5, keyword_filter: str = None) -> Dict:
        """
        Query the vector database

        Args:
            query_text: Query string
            n_results: Number of results to return
            keyword_filter: Optional keyword that must be present in results

        Returns:
            Query results with documents, metadata, and distances
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results * 3 if keyword_filter else n_results,  # Get more for filtering
            include=["documents", "metadatas", "distances"]
        )

        # Filter by keyword if specified
        if keyword_filter and results['documents'][0]:
            keyword_lower = keyword_filter.lower()
            filtered_docs = []
            filtered_metas = []
            filtered_dists = []

            for doc, meta, dist in zip(results['documents'][0],
                                      results['metadatas'][0],
                                      results['distances'][0]):
                if keyword_lower in doc.lower():
                    filtered_docs.append(doc)
                    filtered_metas.append(meta)
                    filtered_dists.append(dist)

                    if len(filtered_docs) >= n_results:
                        break

            results = {
                'documents': [filtered_docs],
                'metadatas': [filtered_metas],
                'distances': [filtered_dists]
            }

        return results

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }

    def reset_collection(self):
        """Delete and recreate the collection"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"✓ Collection '{self.collection_name}' reset")


def create_vector_db(documents: List[Dict[str, str]], reset: bool = False) -> VectorDB:
    """
    Create vector database from processed documents

    Args:
        documents: List of processed documents
        reset: Whether to reset the collection before adding documents

    Returns:
        VectorDB instance
    """
    db = VectorDB()

    if reset:
        db.reset_collection()

    db.add_documents(documents)

    stats = db.get_collection_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Total chunks: {stats['document_count']}")
    print(f"  Location: {stats['persist_directory']}")

    return db


def query_vector_db(query: str, n_results: int = 5) -> Dict:
    """
    Query the vector database

    Args:
        query: Query string
        n_results: Number of results to return

    Returns:
        Query results
    """
    db = VectorDB()
    return db.query(query, n_results)
