#!/usr/bin/env python3
"""
Inspect Vector Database
Shows what's actually stored in your ChromaDB
"""
import sys
from src.backend.vectorize import VectorDB
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import numpy as np

console = Console()


def inspect_database():
    """Inspect the vector database contents"""

    console.print(Panel.fit(
        "[bold blue]Vector Database Inspector[/bold blue]\n"
        "See what's actually stored in your ChromaDB",
        border_style="blue"
    ))

    # Load database
    console.print("\n[dim]Loading vector database...[/dim]")
    db = VectorDB()

    # Get stats
    stats = db.get_collection_stats()

    # Get all data
    all_data = db.collection.get(
        include=["documents", "metadatas"]
    )

    # Get embeddings separately (if needed)
    try:
        embeddings_data = db.collection.get(
            limit=1,
            include=["embeddings"]
        )
        all_data['embeddings'] = embeddings_data.get('embeddings', None)
    except:
        all_data['embeddings'] = None

    console.print(Panel(
        f"[bold]Collection:[/bold] {stats['collection_name']}\n"
        f"[bold]Total Chunks:[/bold] {stats['document_count']}\n"
        f"[bold]Location:[/bold] {stats['persist_directory']}",
        title="Database Stats",
        border_style="green"
    ))

    # Show sample documents
    console.print("\n[bold cyan]Sample Documents:[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=20)
    table.add_column("Source", style="cyan", width=20)
    table.add_column("Chunk", style="green", width=10)
    table.add_column("Content Preview", style="white")

    # Show first 5 documents
    for i in range(min(5, len(all_data['ids']))):
        doc_id = all_data['ids'][i]
        doc = all_data['documents'][i]
        meta = all_data['metadatas'][i]

        preview = doc[:80] + "..." if len(doc) > 80 else doc

        table.add_row(
            doc_id[:20] + "...",
            meta.get('filename', 'Unknown'),
            f"{meta.get('chunk_index', 0) + 1}/{meta.get('total_chunks', 1)}",
            preview
        )

    console.print(table)

    # Show vector embeddings
    if all_data.get('embeddings') is not None and len(all_data['embeddings']) > 0:
        console.print("\n[bold cyan]Vector Embeddings (First Document):[/bold cyan]")

        embedding = all_data['embeddings'][0] if isinstance(all_data['embeddings'], list) else all_data['embeddings']
        if not isinstance(embedding, list):
            embedding = list(embedding)
        console.print(f"[dim]Embedding dimensions:[/dim] {len(embedding)}")
        console.print(f"[dim]First 10 values:[/dim] {embedding[:10]}")
        console.print(f"[dim]Data type:[/dim] {type(embedding[0])}")

        # Show statistics
        embedding_array = np.array(embedding)
        console.print(f"\n[bold]Embedding Statistics:[/bold]")
        console.print(f"  Min value: {embedding_array.min():.4f}")
        console.print(f"  Max value: {embedding_array.max():.4f}")
        console.print(f"  Mean: {embedding_array.mean():.4f}")
        console.print(f"  Std dev: {embedding_array.std():.4f}")

    # File sizes
    console.print("\n[bold cyan]Storage Analysis:[/bold cyan]")

    import os
    from pathlib import Path

    vector_db_path = Path(stats['persist_directory'])
    total_size = 0

    console.print(f"\n[bold]Files in {vector_db_path}:[/bold]")

    for file in vector_db_path.rglob('*'):
        if file.is_file():
            size = file.stat().st_size
            total_size += size
            size_mb = size / (1024 * 1024)
            console.print(f"  {file.name}: {size_mb:.2f} MB")

    console.print(f"\n[bold green]Total size: {total_size / (1024 * 1024):.2f} MB[/bold green]")

    # Query example
    console.print("\n[bold cyan]Testing Query:[/bold cyan]")

    test_query = "machine learning"
    console.print(f"[dim]Query:[/dim] '{test_query}'")

    results = db.query(test_query, n_results=3)

    if results and results['documents'][0]:
        console.print("\n[bold]Top 3 Results:[/bold]")

        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            similarity = max(0, 100 * (1 - dist / 2))
            console.print(
                f"\n{i}. [green]{similarity:.1f}%[/green] similarity - "
                f"{meta.get('filename', 'Unknown')}"
            )
            console.print(f"   {doc[:100]}...")

    # Show breakdown by file
    console.print("\n[bold cyan]Documents by Source:[/bold cyan]")

    file_counts = {}
    for meta in all_data['metadatas']:
        filename = meta.get('filename', 'Unknown')
        file_counts[filename] = file_counts.get(filename, 0) + 1

    file_table = Table(show_header=True, header_style="bold magenta")
    file_table.add_column("PDF File", style="cyan")
    file_table.add_column("# Chunks", justify="right", style="green")

    for filename, count in sorted(file_counts.items()):
        file_table.add_row(filename, str(count))

    console.print(file_table)

    console.print("\n" + "=" * 70)
    console.print("[bold green]Inspection Complete![/bold green]")
    console.print("=" * 70)


if __name__ == "__main__":
    try:
        inspect_database()
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        console.print("\n[yellow]Make sure you've run: python process_pdfs.py[/yellow]")
        sys.exit(1)
