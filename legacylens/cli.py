"""Typer CLI interface for LegacyLens."""

from collections.abc import Callable

import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(name="legacylens", help="Query legacy COBOL codebases with natural language")


def _print_sources(
    sources: list[dict],
    *,
    echo: Callable[[str], None],
) -> None:
    echo("\n--- Sources ---")
    for s in sources:
        echo(
            f"  [{s['file_name']}:{s['start_line']}-{s['end_line']}] "
            f"{s['name']} (score: {s['score']:.3f})"
        )


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question about the codebase"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results"),
    file_type: str | None = typer.Option(None, "--type", "-t", help="Filter by file type (cbl, cpy, bms, jcl)"),
):
    """Ask a question about the CardDemo COBOL codebase."""
    from .chain import ask as chain_ask

    _run_ask(
        question=question,
        top_k=top_k,
        file_type=file_type,
        ask_fn=chain_ask,
        echo=typer.echo,
    )


def _run_ask(
    *,
    question: str,
    top_k: int,
    file_type: str | None,
    ask_fn: Callable[..., dict],
    echo: Callable[[str], None],
) -> None:
    echo(f"Querying: {question}\n")
    result = ask_fn(question, top_k=top_k, file_type=file_type)
    echo(result["answer"])
    _print_sources(result["sources"], echo=echo)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(10, "--top-k", "-k"),
    file_type: str | None = typer.Option(None, "--type", "-t"),
):
    """Search for relevant code chunks (no LLM, debug mode)."""
    from .retriever import retrieve

    _run_search(
        query=query,
        top_k=top_k,
        file_type=file_type,
        retrieve_fn=retrieve,
        echo=typer.echo,
    )


def _run_search(
    *,
    query: str,
    top_k: int,
    file_type: str | None,
    retrieve_fn: Callable[..., list],
    echo: Callable[[str], None],
) -> None:
    results = retrieve_fn(query, top_k=top_k, file_type=file_type)
    for i, r in enumerate(results, 1):
        echo(f"\n--- Result {i} (score: {r.score:.3f}) ---")
        echo(f"File: {r.file_name}:{r.start_line}-{r.end_line}")
        echo(f"Type: {r.chunk_type} | Name: {r.name}")
        echo(r.content[:500])


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to codebase directory"),
    clean: bool = typer.Option(False, "--clean", help="Clear existing vectors first"),
):
    """Ingest a codebase into the vector store."""
    from .ingest import ingest_codebase
    from .vectorstore import delete_namespace

    _run_ingest(
        path=path,
        clean=clean,
        delete_namespace_fn=delete_namespace,
        ingest_fn=ingest_codebase,
        echo=typer.echo,
    )


def _run_ingest(
    *,
    path: str,
    clean: bool,
    delete_namespace_fn: Callable[[], None],
    ingest_fn: Callable[..., dict],
    echo: Callable[[str], None],
) -> None:
    if clean:
        echo("Clearing existing namespace...")
        delete_namespace_fn()

    result = ingest_fn(path, verbose=True)
    echo(f"\nDone: {result['files']} files, {result['chunks']} chunks, {result['vectors']} vectors")


if __name__ == "__main__":
    app()
