"""
Interactive CLI for RAG Queries
Provides a command-line interface to query the vector database
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from ..backend.vectorize import VectorDB
from ..backend.llm import LLMAnswerGenerator
from ..utils.config import LLM_PROVIDER

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

console = Console()


def display_results(results, query, min_similarity=60.0):
    """Display query results in a formatted way"""
    if not results or not results['documents'][0]:
        console.print("[yellow]No results found.[/yellow]")
        return

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results.get('distances', [[0] * len(documents)])[0]

    # Filter by minimum similarity and prepare rows
    filtered_results = []
    for doc, metadata, distance in zip(documents, metadatas, distances):
        # Convert distance to similarity score (0-100%)
        # ChromaDB uses cosine distance: 0 = identical, 2 = opposite
        similarity = max(0, 100 * (1 - distance / 2))

        if similarity >= min_similarity:
            filtered_results.append((doc, metadata, similarity))

    if not filtered_results:
        console.print(f"[yellow]No results found with similarity >= {min_similarity}%[/yellow]")
        console.print("[dim]Try a different query or lower the threshold[/dim]")
        return

    # Create results table
    table = Table(title=f"Results for: '{query}'", show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Similarity", style="yellow", width=10)
    table.add_column("Source", style="cyan")
    table.add_column("Chunk", style="green", width=8)
    table.add_column("Preview", style="white")

    for i, (doc, metadata, similarity) in enumerate(filtered_results, 1):
        # Color code similarity
        if similarity >= 80:
            sim_color = "green"
        elif similarity >= 70:
            sim_color = "yellow"
        else:
            sim_color = "red"

        preview = doc[:80] + "..." if len(doc) > 80 else doc
        table.add_row(
            str(i),
            f"[{sim_color}]{similarity:.1f}%[/{sim_color}]",
            metadata.get('filename', 'Unknown'),
            f"{metadata.get('chunk_index', 0) + 1}/{metadata.get('total_chunks', 1)}",
            preview
        )

    console.print(table)
    console.print(f"[dim]Showing {len(filtered_results)} results (minimum similarity: {min_similarity}%)[/dim]")

    # Show detailed view option
    console.print("\n[dim]Type a number (1-5) to see full content, or press Enter to continue[/dim]")
    choice = input("> ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(documents):
        idx = int(choice) - 1
        console.print(Panel(
            documents[idx],
            title=f"[bold]{metadatas[idx].get('filename', 'Unknown')} - Chunk {metadatas[idx].get('chunk_index', 0) + 1}[/bold]",
            border_style="blue"
        ))


def main():
    """Main CLI loop for interactive querying"""
    console.print(Panel.fit(
        "[bold blue]RAG Query CLI[/bold blue]\n"
        "Query your PDF documents using natural language",
        border_style="blue"
    ))

    try:
        # Initialize vector database
        console.print("\n[dim]Connecting to vector database...[/dim]")
        db = VectorDB()
        stats = db.get_collection_stats()

        console.print(f"[green]✓[/green] Connected to '{stats['collection_name']}'")
        console.print(f"[dim]  Documents in database: {stats['document_count']}[/dim]\n")

        if stats['document_count'] == 0:
            console.print("[yellow]Warning: Database is empty. Run 'python process_pdfs.py' first.[/yellow]")
            return

    except Exception as e:
        console.print(f"[red]Error connecting to database: {str(e)}[/red]")
        console.print("[yellow]Make sure to run 'python process_pdfs.py' first.[/yellow]")
        return

    # Initialize LLM (optional)
    llm = None
    answer_mode = False

    console.print("\n[bold cyan]Setup LLM for Answers (Optional)[/bold cyan]")
    console.print("Do you want natural language answers? (Requires API key)")
    console.print("1. Anthropic Claude (recommended)")
    console.print("2. OpenAI GPT")
    console.print("3. Ollama (local, free, requires Ollama installed)")
    console.print("4. Skip (just show matching chunks)")

    choice = console.input("\n[cyan]Choose (1-4):[/cyan] ").strip()

    if choice in ['1', '2', '3']:
        provider_map = {'1': 'anthropic', '2': 'openai', '3': 'ollama'}
        provider = provider_map[choice]

        try:
            if provider == 'ollama':
                console.print("[dim]Using Ollama (make sure it's running: ollama serve)[/dim]")
                llm = LLMAnswerGenerator(provider='ollama')
            else:
                api_key_env = 'ANTHROPIC_API_KEY' if provider == 'anthropic' else 'OPENAI_API_KEY'
                if os.getenv(api_key_env):
                    console.print(f"[dim]Using {api_key_env} from environment[/dim]")
                    llm = LLMAnswerGenerator(provider=provider)
                else:
                    console.print(f"[yellow]No {api_key_env} found in environment.[/yellow]")
                    api_key = console.input(f"Enter your API key (or press Enter to skip): ").strip()
                    if api_key:
                        llm = LLMAnswerGenerator(provider=provider, api_key=api_key)
                    else:
                        console.print("[dim]Skipping LLM setup[/dim]")

            if llm:
                answer_mode = True
                console.print(f"[green]✓[/green] LLM enabled: {provider}")
        except Exception as e:
            console.print(f"[red]Error setting up LLM: {str(e)}[/red]")
            console.print("[dim]Continuing without LLM...[/dim]")

    console.print("\n[dim]Commands:[/dim]")
    console.print("[dim]  'exit' or 'quit' - Exit the CLI[/dim]")
    console.print("[dim]  'stats' - Database statistics[/dim]")
    console.print("[dim]  'threshold <number>' - Set minimum similarity (default: 60%)[/dim]")
    console.print("[dim]  'mode answer/chunks' - Switch between answer mode and chunk display[/dim]")
    console.print("=" * 60)

    min_similarity = 60.0  # Default minimum similarity threshold

    while True:
        try:
            query = console.input("\n[bold cyan]Query>[/bold cyan] ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                console.print("\n[dim]Goodbye![/dim]")
                break

            if query.lower() == 'stats':
                stats = db.get_collection_stats()
                console.print(f"\n[bold]Database Statistics:[/bold]")
                console.print(f"  Collection: {stats['collection_name']}")
                console.print(f"  Total chunks: {stats['document_count']}")
                console.print(f"  Location: {stats['persist_directory']}")
                console.print(f"  Current threshold: {min_similarity}%")
                console.print(f"  Keyword mode: {'ON (exact matches only)' if keyword_mode else 'OFF (semantic search)'}")
                continue

            if query.lower().startswith('mode '):
                mode = query.split()[1].lower() if len(query.split()) > 1 else ''
                if mode == 'answer' and llm:
                    answer_mode = True
                    console.print("[green]✓[/green] Answer mode: Natural language answers enabled")
                elif mode == 'chunks':
                    answer_mode = False
                    console.print("[green]✓[/green] Chunk mode: Showing matching document chunks")
                elif mode == 'answer' and not llm:
                    console.print("[yellow]LLM not configured. Run the CLI again to set up an LLM.[/yellow]")
                else:
                    console.print("[red]Usage: mode answer | mode chunks[/red]")
                continue

            if query.lower().startswith('threshold '):
                try:
                    new_threshold = float(query.split()[1])
                    if 0 <= new_threshold <= 100:
                        min_similarity = new_threshold
                        console.print(f"[green]✓[/green] Minimum similarity set to {min_similarity}%")
                    else:
                        console.print("[red]Threshold must be between 0 and 100[/red]")
                except (IndexError, ValueError):
                    console.print("[red]Usage: threshold <number>[/red]")
                    console.print("[dim]Example: threshold 70[/dim]")
                continue

            # Query the database
            console.print(f"[dim]Searching...[/dim]")
            results = db.query(query, n_results=10)  # Get more results, filter by similarity

            # Check if we have results
            if not results or not results['documents'][0]:
                console.print("[yellow]No results found.[/yellow]")
                continue

            # Filter by similarity threshold
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results.get('distances', [[0] * len(documents)])[0]

            filtered_chunks = []
            filtered_metas = []

            for doc, meta, distance in zip(documents, metadatas, distances):
                similarity = max(0, 100 * (1 - distance / 2))
                if similarity >= min_similarity:
                    filtered_chunks.append(doc)
                    filtered_metas.append(meta)

            if not filtered_chunks:
                console.print(f"[yellow]No results found with similarity >= {min_similarity}%[/yellow]")
                continue

            # Display results
            console.print()

            if answer_mode and llm:
                # Generate natural language answer
                console.print("[dim]Generating answer...[/dim]\n")

                answer = llm.generate_answer(query, filtered_chunks[:5], filtered_metas[:5])

                # Display answer in a nice panel
                console.print(Panel(
                    Markdown(answer),
                    title="[bold green]Answer[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))

                # Show sources used
                console.print("\n[dim]Sources used:[/dim]")
                for i, meta in enumerate(filtered_metas[:5], 1):
                    console.print(f"  [{i}] {meta.get('filename', 'Unknown')} (Chunk {meta.get('chunk_index', 0) + 1})")

            else:
                # Show chunk results (original behavior)
                display_results(results, query, min_similarity=min_similarity)

        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    main()
