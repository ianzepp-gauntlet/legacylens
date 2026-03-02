"""Ingestion orchestrator: parse → chunk → embed → store."""

import os
from pathlib import Path

from .chunker import chunk_file
from .embeddings import get_embeddings
from .models import CodeChunk
from .vectorstore import METADATA_CONTENT_LIMIT, upsert_chunks


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


def discover_files(base_path: str) -> list[str]:
    """Find all supported source files under a directory."""
    files = []
    for root, _dirs, filenames in os.walk(base_path):
        for fname in filenames:
            if Path(fname).suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(os.path.join(root, fname))
    return sorted(files)


def ingest_codebase(
    base_path: str,
    verbose: bool = True,
) -> dict:
    """Run the full ingestion pipeline on a codebase directory."""
    files = discover_files(base_path)
    if verbose:
        print(f"Found {len(files)} source files")

    all_chunks: list[CodeChunk] = []
    errors = []

    for f in files:
        try:
            chunks = chunk_file(f)
            all_chunks.extend(chunks)
            if verbose:
                print(f"  {Path(f).name}: {len(chunks)} chunks")
        except Exception as e:
            errors.append((f, str(e)))
            if verbose:
                print(f"  ERROR {Path(f).name}: {e}")

    if verbose:
        print(f"\nTotal chunks: {len(all_chunks)}")
        print("Generating embeddings...")

    # Build texts for embedding: preamble + content
    texts = [
        f"{chunk.preamble}\n\n{chunk.content[:METADATA_CONTENT_LIMIT]}" for chunk in all_chunks
    ]

    embeddings = get_embeddings(texts)

    if verbose:
        print(f"Generated {len(embeddings)} embeddings")
        print("Upserting to Pinecone...")

    total = upsert_chunks(all_chunks, embeddings)

    if verbose:
        print(f"Upserted {total} vectors")
        if errors:
            print(f"\n{len(errors)} errors:")
            for path, err in errors:
                print(f"  {path}: {err}")

    return {
        "files": len(files),
        "chunks": len(all_chunks),
        "vectors": total,
        "errors": errors,
    }
