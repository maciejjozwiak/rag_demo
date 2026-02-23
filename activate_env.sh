#!/bin/bash
# Quick activation script
source venv/bin/activate
echo "✓ Virtual environment activated"
echo "Run: python process_pdfs.py --reset   (to process PDFs)"
echo "Run: python -m src.cli.query_cli      (to query documents)"
