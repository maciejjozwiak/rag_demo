# Quick Start Guide

## ✅ Setup Complete!

Your RAG system is ready to use. The virtual environment has been created with Python 3.12 and all dependencies are installed.

## 📝 Next Steps

### 1. Activate the Virtual Environment

**Every time you work on this project**, activate the virtual environment first:

```bash
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when it's active.

### 2. Add Your PDF Files

Place your PDF files in the `data/pdfs/` directory:

```bash
# Example: copy PDFs from another location
cp ~/Documents/*.pdf data/pdfs/

# Or manually drag and drop PDFs into data/pdfs/ folder
```

### 3. Process PDFs and Build Vector Database

Run the processing script:

```bash
python process_pdfs.py --reset --save-markdown
```

This will:
- ✅ Load all PDFs from `data/pdfs/`
- ✅ Convert them to markdown
- ✅ Clean and chunk the text
- ✅ Create embeddings and store in ChromaDB
- ✅ Save processed markdown files (optional with `--save-markdown`)

### 4. Query Your Documents

Launch the interactive CLI:

```bash
python -m src.cli.query_cli
```

Then ask questions about your documents!

Example queries:
- "What are the main topics discussed?"
- "Summarize the key findings"
- "What methodology was used?"

## 🔧 Useful Commands

### Reprocess PDFs (keeps existing data)
```bash
python process_pdfs.py
```

### Reset and rebuild database from scratch
```bash
python process_pdfs.py --reset
```

### Use a different PDF directory
```bash
python process_pdfs.py --pdf-dir /path/to/other/pdfs
```

### View database statistics in CLI
```bash
python -m src.cli.query_cli
# Then type: stats
```

### Deactivate virtual environment (when done)
```bash
deactivate
```

## 📊 Example Session

```bash
# Activate environment
source venv/bin/activate

# Process PDFs
python process_pdfs.py --reset

# Output:
# ============================================================
# PDF Processing and Vector Database Creation
# ============================================================
#
# [1/4] Loading PDFs...
# Found 3 PDF files
# Loading: document1.pdf
#   ✓ Loaded 15234 characters
# ...
#
# [4/4] Creating vector database...
#   Added chunks 1-100 / 145
#   Added chunks 101-145 / 145
# ✓ Total chunks added to database: 145
#
# ============================================================
# ✓ Processing complete!
# ============================================================

# Query documents
python -m src.cli.query_cli

# Output:
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ RAG Query CLI                          ┃
# ┃ Query your PDF documents using         ┃
# ┃ natural language                        ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
#
# ✓ Connected to 'pdf_documents'
#   Documents in database: 145
#
# Query> What is machine learning?
```

## 🛠️ Troubleshooting

### "No PDFs to process"
- Make sure PDF files are in `data/pdfs/` directory
- Check that files have `.pdf` extension

### "Database is empty"
- Run `python process_pdfs.py` first to build the database

### "ModuleNotFoundError"
- Make sure virtual environment is activated: `source venv/bin/activate`
- If still failing, reinstall: `pip install -r requirements.txt`

### Poor search results
- Try rephrasing your query
- Ensure PDFs are text-based (not scanned images)
- Check that PDFs were processed correctly by looking at `data/processed/` files

## 📚 Documentation

See `README.md` for complete documentation including:
- Project structure
- Configuration options
- Programmatic usage
- Advanced features

## 🎯 Pro Tips

1. **Use specific queries**: Instead of "tell me about the document", ask "what were the key findings about X?"

2. **Check processed files**: Look at `data/processed/*.md` files to see how your PDFs were parsed

3. **Adjust chunk size**: Edit `src/utils/config.py` to change `CHUNK_SIZE` if needed (default: 1000)

4. **View context**: In the CLI, enter a number (1-5) to see the full text of any search result

5. **Batch processing**: Drop many PDFs at once - the system handles them all automatically

Happy querying! 🚀
