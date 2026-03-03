"""Ingest CardDemo data into all benchmark Pinecone indexes.

Usage:
    python benchmarks/ingest_all.py [--configs small-256-paragraph,large-1024-fixed]
    python benchmarks/ingest_all.py --clean   # delete and re-create all indexes
"""

import argparse
import hashlib
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import (
    Pinecone,
    ServerlessSpec,
)

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.config import CONFIGS, BenchmarkConfig
from legacylens.chunker import chunk_file
from legacylens.config import settings
from legacylens.ingest import discover_files
from legacylens.models import CodeChunk
from legacylens.vectorstore import METADATA_CONTENT_LIMIT


NAMESPACE = "carddemo"
TEXT_FIELD = "chunk_text"  # field name used in Pinecone integrated indexes


def _make_vector_id(chunk: CodeChunk) -> str:
    path_digest = hashlib.sha1(chunk.file_path.encode("utf-8")).hexdigest()[:12]
    return f"{chunk.file_name}:{path_digest}:{chunk.start_line}-{chunk.end_line}"


def _chunk_metadata(chunk: CodeChunk) -> dict:
    return {
        "file_path": chunk.file_path,
        "file_name": chunk.file_name,
        "file_type": chunk.file_type,
        "chunk_type": chunk.chunk_type,
        "name": chunk.name,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "parent_program": chunk.parent_program,
        "comments": chunk.comments[:1000],
        "has_comments": bool(chunk.comments.strip()),
        "content": chunk.content[:METADATA_CONTENT_LIMIT],
        "preamble": chunk.preamble,
        "copy_references": ",".join(chunk.copy_references),
        "calls_to": ",".join(chunk.calls_to),
    }


def _embed_text(chunk: CodeChunk) -> str:
    """Build the text that gets embedded (preamble + content)."""
    return f"{chunk.preamble}\n\n{chunk.content[:METADATA_CONTENT_LIMIT]}"


def _wait_for_index(pc: Pinecone, index_name: str, timeout: int = 120):
    """Wait until an index is ready."""
    start = time.time()
    while time.time() - start < timeout:
        desc = pc.describe_index(index_name)
        if desc.status.get("ready", False):
            return
        print(f"  Waiting for {index_name} to be ready...")
        time.sleep(5)
    raise TimeoutError(f"Index {index_name} not ready after {timeout}s")


def create_index(pc: Pinecone, config: BenchmarkConfig, clean: bool = False):
    """Create a Pinecone index for a benchmark config."""
    existing = [idx.name for idx in pc.list_indexes()]

    if config.index_name in existing:
        if clean:
            print(f"  Deleting existing index {config.index_name}...")
            pc.delete_index(config.index_name)
            time.sleep(5)
        else:
            print(f"  Index {config.index_name} already exists, skipping creation")
            return

    if config.is_pinecone_integrated:
        print(f"  Creating integrated index {config.index_name} ({config.pinecone_model})...")
        pc.create_index_for_model(
            name=config.index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": config.pinecone_model,
                "field_map": {"text": TEXT_FIELD},
            },
        )
    else:
        print(f"  Creating index {config.index_name} (dim={config.embedding_dimensions})...")
        pc.create_index(
            name=config.index_name,
            dimension=config.embedding_dimensions,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    _wait_for_index(pc, config.index_name)


def ingest_openai(
    pc: Pinecone,
    config: BenchmarkConfig,
    chunks: list[CodeChunk],
):
    """Embed with OpenAI and upsert vectors into Pinecone."""
    client = OpenAI(api_key=settings.openai_api_key)
    index = pc.Index(config.index_name)
    batch_size = 100

    texts = [_embed_text(c) for c in chunks]
    all_embeddings = []

    print(f"  Embedding {len(texts)} chunks with {config.embedding_model} (dim={config.embedding_dimensions})...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=config.embedding_model,
            input=batch,
            dimensions=config.embedding_dimensions,
        )
        all_embeddings.extend([d.embedding for d in response.data])

    print(f"  Upserting {len(all_embeddings)} vectors...")
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_embeds = all_embeddings[i : i + batch_size]
        vectors = []
        for chunk, emb in zip(batch_chunks, batch_embeds):
            vectors.append({
                "id": _make_vector_id(chunk),
                "values": emb,
                "metadata": _chunk_metadata(chunk),
            })
        index.upsert(vectors=vectors, namespace=NAMESPACE)


def ingest_pinecone_integrated(
    pc: Pinecone,
    config: BenchmarkConfig,
    chunks: list[CodeChunk],
):
    """Upsert records for Pinecone integrated embedding.

    Uses upsert_records() — Pinecone generates embeddings server-side
    from the text field specified in the index's field_map.
    """
    index = pc.Index(config.index_name)
    batch_size = 96  # Pinecone integrated indexes limit batches to 96

    print(f"  Upserting {len(chunks)} records (Pinecone will embed with {config.pinecone_model})...")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        records = []
        for chunk in batch:
            record = _chunk_metadata(chunk)
            record["_id"] = _make_vector_id(chunk)
            record[TEXT_FIELD] = _embed_text(chunk)
            records.append(record)
        index.upsert_records(NAMESPACE, records)


def ingest_config(
    pc: Pinecone,
    config: BenchmarkConfig,
    all_files: list[str],
    clean: bool = False,
):
    """Ingest all files into a single benchmark index."""
    print(f"\n{'='*60}")
    print(f"Config: {config.name}")
    print(f"  Provider: {config.embedding_provider}, Model: {config.embedding_model}")
    print(f"  Dimensions: {config.embedding_dimensions}, Chunking: {config.chunking_strategy}")
    print(f"{'='*60}")

    create_index(pc, config, clean=clean)
    index = pc.Index(config.index_name)
    try:
        index.delete(delete_all=True, namespace=NAMESPACE)
        print(f"  Cleared namespace '{NAMESPACE}' in {config.index_name}")
    except Exception as exc:
        status = getattr(exc, "status", None) or getattr(exc, "status_code", None)
        if status != 404 and "404" not in str(exc):
            raise

    # Chunk files
    chunks = []
    errors = []
    for f in all_files:
        try:
            file_chunks = chunk_file(f, strategy=config.chunking_strategy)
            chunks.extend(file_chunks)
        except Exception as e:
            errors.append((f, str(e)))
            print(f"  ERROR chunking {Path(f).name}: {e}")

    print(f"  Chunked {len(all_files)} files → {len(chunks)} chunks ({len(errors)} errors)")

    if config.is_pinecone_integrated:
        ingest_pinecone_integrated(pc, config, chunks)
    else:
        ingest_openai(pc, config, chunks)

    print(f"  Done: {config.name}")


def main():
    parser = argparse.ArgumentParser(description="Ingest CardDemo into benchmark indexes")
    parser.add_argument("--configs", help="Comma-separated config names to run (default: all)")
    parser.add_argument("--clean", action="store_true", help="Delete and recreate indexes")
    args = parser.parse_args()

    if not settings.pinecone_api_key:
        print("ERROR: PINECONE_API_KEY not set")
        sys.exit(1)
    if not settings.carddemo_path:
        print("ERROR: CARDDEMO_PATH not set")
        sys.exit(1)

    pc = Pinecone(api_key=settings.pinecone_api_key)

    configs = CONFIGS
    if args.configs:
        names = {n.strip() for n in args.configs.split(",")}
        configs = [c for c in CONFIGS if c.name in names]
        if not configs:
            print(f"No matching configs found for: {args.configs}")
            print(f"Available: {', '.join(c.name for c in CONFIGS)}")
            sys.exit(1)

    needs_openai = any(not config.is_pinecone_integrated for config in configs)
    if needs_openai and not settings.openai_api_key:
        print("ERROR: OPENAI_API_KEY not set (required for OpenAI embedding benchmark configs)")
        sys.exit(1)

    print(f"Discovering files in {settings.carddemo_path}...")
    all_files = discover_files(settings.carddemo_path)
    print(f"Found {len(all_files)} source files")
    print(f"\nWill ingest into {len(configs)} indexes")

    for config in configs:
        ingest_config(pc, config, all_files, clean=args.clean)

    print(f"\n{'='*60}")
    print(f"All done! Ingested into {len(configs)} indexes.")


if __name__ == "__main__":
    main()
