"""Ingestion orchestrator: parse -> chunk -> embed -> store."""

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .chunker import chunk_file
from .config import settings
from .models import CodeChunk
from .vectorstore import METADATA_CONTENT_LIMIT, upsert_chunks, upsert_records


SUPPORTED_EXTENSIONS = {
    ".cbl",
    ".cob",
    ".cpy",
    ".bms",
    ".jcl",
    ".dcl",
    ".ddl",
    ".ctl",
    ".csd",
    ".dbd",
    ".psb",
    ".asm",
    ".mac",
}


@dataclass(frozen=True)
class IngestDependencies:
    """Dependency bundle for ingestion execution."""

    chunk_file_fn: Callable[[str], list[CodeChunk]]
    upsert_records_fn: Callable[[list[CodeChunk], list[str]], int]
    upsert_chunks_fn: Callable[[list[CodeChunk], list[list[float]]], int]
    get_embeddings_fn: Callable[[list[str]], list[list[float]]]


def _default_dependencies() -> IngestDependencies:
    from .embeddings import get_embeddings

    return IngestDependencies(
        chunk_file_fn=chunk_file,
        upsert_records_fn=upsert_records,
        upsert_chunks_fn=upsert_chunks,
        get_embeddings_fn=get_embeddings,
    )


def _select_reporter(
    verbose: bool,
    reporter: Callable[[str], None] | None,
) -> Callable[[str], None]:
    if reporter is not None:
        return reporter
    if verbose:
        return print
    return lambda _msg: None


def discover_files(base_path: str) -> list[str]:
    """Find all supported source files under a directory."""
    files = []
    for root, _dirs, filenames in os.walk(base_path):
        for fname in filenames:
            if Path(fname).suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(os.path.join(root, fname))
    return sorted(files)


def _embed_text(chunk: CodeChunk) -> str:
    """Build the text that gets embedded (preamble + content)."""
    return f"{chunk.preamble}\n\n{chunk.content[:METADATA_CONTENT_LIMIT]}"


def _chunk_files(
    files: list[str],
    *,
    chunk_file_fn: Callable[[str], list[CodeChunk]],
    report: Callable[[str], None],
) -> tuple[list[CodeChunk], list[tuple[str, str]]]:
    all_chunks: list[CodeChunk] = []
    errors: list[tuple[str, str]] = []

    for f in files:
        try:
            chunks = chunk_file_fn(f)
            all_chunks.extend(chunks)
            report(f"  {Path(f).name}: {len(chunks)} chunks")
        except Exception as exc:
            errors.append((f, str(exc)))
            report(f"  ERROR {Path(f).name}: {exc}")

    return all_chunks, errors


def _upsert_for_provider(
    chunks: list[CodeChunk],
    *,
    texts: list[str],
    embedding_provider: str,
    pinecone_model: str,
    deps: IngestDependencies,
    report: Callable[[str], None],
) -> int:
    if embedding_provider == "pinecone":
        report(f"Upserting to Pinecone (server-side embedding with {pinecone_model})...")
        return deps.upsert_records_fn(chunks, texts)

    report("Generating embeddings...")
    embeddings = deps.get_embeddings_fn(texts)
    report(f"Generated {len(embeddings)} embeddings")
    report("Upserting to Pinecone...")
    return deps.upsert_chunks_fn(chunks, embeddings)


def ingest_codebase(
    base_path: str,
    verbose: bool = True,
    *,
    deps: IngestDependencies | None = None,
    reporter: Callable[[str], None] | None = None,
    embedding_provider: str | None = None,
    pinecone_model: str | None = None,
) -> dict:
    """Run the full ingestion pipeline on a codebase directory."""
    active_deps = deps or _default_dependencies()
    report = _select_reporter(verbose, reporter)

    files = discover_files(base_path)
    report(f"Found {len(files)} source files")

    all_chunks, errors = _chunk_files(
        files,
        chunk_file_fn=active_deps.chunk_file_fn,
        report=report,
    )
    report(f"\nTotal chunks: {len(all_chunks)}")

    total = _upsert_for_provider(
        all_chunks,
        texts=[_embed_text(chunk) for chunk in all_chunks],
        embedding_provider=embedding_provider or settings.embedding_provider,
        pinecone_model=pinecone_model or settings.pinecone_model,
        deps=active_deps,
        report=report,
    )

    report(f"Upserted {total} vectors")
    if errors:
        report(f"\n{len(errors)} errors:")
        for path, err in errors:
            report(f"  {path}: {err}")

    return {
        "files": len(files),
        "chunks": len(all_chunks),
        "vectors": total,
        "errors": errors,
    }
