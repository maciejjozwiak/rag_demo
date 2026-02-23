"""
Configuration Module
Stores project configuration and paths
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# ChromaDB settings
CHROMA_COLLECTION_NAME = "pdf_documents"
CHROMA_DB_PATH = str(VECTOR_DB_DIR)

# Text processing settings
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # sentence-transformers model

# LLM settings for answer generation
LLM_PROVIDER = "anthropic"  # Options: "anthropic", "openai", "ollama"
# API keys should be set in environment variables:
# - ANTHROPIC_API_KEY for Anthropic Claude
# - OPENAI_API_KEY for OpenAI GPT
