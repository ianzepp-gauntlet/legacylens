"""Typer CLI interface for LegacyLens."""

import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(name="legacylens", help="Query legacy COBOL codebases with natural language")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question about the codebase"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results"),
    file_type: str | None = typer.Option(None, "--type", "-t", help="Filter by file type (cbl, cpy, bms, jcl)"),
):
    """Ask a question about the CardDemo COBOL codebase."""
    from .chain import ask as chain_ask

    typer.echo(f"Querying: {question}\n")
    result = chain_ask(question, top_k=top_k, file_type=file_type)

    typer.echo(result["answer"])
    typer.echo("\n--- Sources ---")
    for s in result["sources"]:
        typer.echo(f"  [{s['file_name']}:{s['start_line']}-{s['end_line']}] "
                   f"{s['name']} (score: {s['score']:.3f})")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(10, "--top-k", "-k"),
    file_type: str | None = typer.Option(None, "--type", "-t"),
):
    """Search for relevant code chunks (no LLM, debug mode)."""
    from .retriever import retrieve

    results = retrieve(query, top_k=top_k, file_type=file_type)
    for i, r in enumerate(results, 1):
        typer.echo(f"\n--- Result {i} (score: {r.score:.3f}) ---")
        typer.echo(f"File: {r.file_name}:{r.start_line}-{r.end_line}")
        typer.echo(f"Type: {r.chunk_type} | Name: {r.name}")
        typer.echo(r.content[:500])


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to codebase directory"),
    clean: bool = typer.Option(False, "--clean", help="Clear existing vectors first"),
):
    """Ingest a codebase into the vector store."""
    from .ingest import ingest_codebase
    from .vectorstore import delete_namespace

    if clean:
        typer.echo("Clearing existing namespace...")
        delete_namespace()

    result = ingest_codebase(path, verbose=True)
    typer.echo(f"\nDone: {result['files']} files, {result['chunks']} chunks, {result['vectors']} vectors")


if __name__ == "__main__":
    app()
