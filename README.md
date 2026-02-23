# RAG Demo Project

A Retrieval-Augmented Generation (RAG) system with PDF processing and interactive CLI querying using ChromaDB.

## Project Structure

```
rag_demo/
├── data/
│   ├── pdfs/           # Place your PDF files here
│   └── processed/      # Processed markdown files (optional)
├── vector_db/          # ChromaDB vector database storage
├── src/
│   ├── backend/        # PDF processing and vectorization
│   │   ├── pdf_loader.py      # Load PDFs from folder
│   │   ├── converter.py       # Convert PDFs to markdown
│   │   ├── cleaner.py         # Clean and chunk markdown
│   │   └── vectorize.py       # ChromaDB vector database
│   ├── cli/
│   │   └── query_cli.py       # Interactive query CLI
│   └── utils/
│       └── config.py          # Configuration and paths
├── process_pdfs.py     # Main processing script
├── requirements.txt    # Python dependencies
└── README.md
```

## Features

- **PDF Processing**: Automatically extracts text from PDFs using pdfplumber
- **Markdown Conversion**: Converts PDF content to clean markdown format
- **Text Cleaning**: Removes OCR errors, normalizes spacing, and fixes formatting
- **Smart Chunking**: Splits documents into overlapping chunks at sentence boundaries
- **Vector Database**: Uses ChromaDB for efficient semantic search
- **Interactive CLI**: Rich terminal interface for querying documents

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Add PDFs

Place your PDF files in the `data/pdfs/` directory:
```bash
cp /path/to/your/documents/*.pdf data/pdfs/
```

### Step 2: Process PDFs and Build Vector Database

Run the processing script:
```bash
python process_pdfs.py
```

Options:
- `--reset`: Reset the vector database before processing (deletes existing data)
- `--save-markdown`: Save processed markdown files to `data/processed/`
- `--pdf-dir PATH`: Use a different directory for PDF files

Example with options:
```bash
python process_pdfs.py --reset --save-markdown
```

### Step 3: Query Your Documents

Launch the interactive CLI:
```bash
python -m src.cli.query_cli
```

CLI Commands:
- Enter any natural language query to search your documents
- Type a number (1-5) to view full content of a result
- `stats` - Show database statistics
- `exit`, `quit`, or `q` - Exit the CLI

## Example Session

```
RAG Query CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Query your PDF documents using natural language

✓ Connected to 'pdf_documents'
  Documents in database: 145

Commands: 'exit' or 'quit' to exit, 'stats' for database statistics
============================================================

Query> What is machine learning?

Searching...

                    Results for: 'What is machine learning?'
┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Rank ┃ Source         ┃ Chunk ┃ Preview                 ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ ml_intro.pdf   │ 3/12  │ Machine learning is...  │
│ 2    │ ai_basics.pdf  │ 1/8   │ Introduction to AI...   │
└──────┴────────────────┴───────┴─────────────────────────┘
```

## Configuration

Edit `src/utils/config.py` to customize:

- `CHUNK_SIZE`: Size of text chunks (default: 1000 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 characters)
- `EMBEDDING_MODEL`: Sentence transformer model (default: "all-MiniLM-L6-v2")
- `CHROMA_COLLECTION_NAME`: ChromaDB collection name

## How It Works

1. **PDF Loading**: `pdf_loader.py` reads all PDFs from the specified directory using pdfplumber
2. **Conversion**: `converter.py` converts PDF text to markdown format with page headers
3. **Cleaning**: `cleaner.py` removes OCR errors, normalizes spacing, and splits into chunks
4. **Vectorization**: `vectorize.py` creates embeddings and stores them in ChromaDB
5. **Querying**: `query_cli.py` provides an interface to search using semantic similarity

## Dependencies

- **pdfplumber**: PDF text extraction
- **chromadb**: Vector database for semantic search
- **sentence-transformers**: Generate text embeddings
- **rich**: Beautiful terminal formatting

## Troubleshooting

### "No PDFs to process"
Make sure PDF files are in the `data/pdfs/` directory.

### "Database is empty"
Run `python process_pdfs.py` to build the vector database first.

### Memory issues with large PDFs
Adjust `CHUNK_SIZE` in `config.py` to a smaller value.

### Poor search results
- Try different queries or rephrase your question
- Ensure PDFs have good text extraction quality (not scanned images)
- Increase the number of results with `n_results` parameter

## License

MIT
