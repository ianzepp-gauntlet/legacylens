"""Pinecone vector store operations."""

import hashlib

from pinecone import Pinecone, ServerlessSpec

from .config import settings
from .models import CodeChunk


METADATA_CONTENT_LIMIT = 10000  # Pinecone 40KB metadata limit


def _is_not_found_error(exc: Exception) -> bool:
    """Return True for namespace-not-found style errors."""
    status = getattr(exc, "status", None) or getattr(exc, "status_code", None)
    if status == 404:
        return True
    return "404" in str(exc)


def make_vector_id(chunk: CodeChunk) -> str:
    """Build a stable, unique vector ID for a chunk."""
    path_digest = hashlib.sha1(chunk.file_path.encode("utf-8")).hexdigest()[:12]
    return f"{chunk.file_name}:{path_digest}:{chunk.start_line}-{chunk.end_line}"


def get_index():
    """Get or create the Pinecone index."""
    pc = Pinecone(api_key=settings.pinecone_api_key)

    existing = [idx.name for idx in pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimensions,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return pc.Index(settings.pinecone_index_name)


def upsert_chunks(
    chunks: list[CodeChunk],
    embeddings: list[list[float]],
    batch_size: int = 100,
) -> int:
    """Upsert chunk embeddings into Pinecone."""
    index = get_index()
    total = 0

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_embeds = embeddings[i : i + batch_size]

        vectors = []
        for chunk, embedding in zip(batch_chunks, batch_embeds):
            vec_id = make_vector_id(chunk)
            metadata = {
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
            vectors.append({"id": vec_id, "values": embedding, "metadata": metadata})

        index.upsert(vectors=vectors, namespace=settings.pinecone_namespace)
        total += len(vectors)

    return total


def query_vectors(
    embedding: list[float],
    top_k: int | None = None,
    file_type_filter: str | None = None,
    metadata_filters: dict[str, str] | None = None,
) -> list[dict]:
    """Query Pinecone for similar vectors."""
    index = get_index()
    k = top_k or settings.top_k

    filter_dict = {}
    if file_type_filter:
        filter_dict["file_type"] = {"$eq": file_type_filter}
    if metadata_filters:
        for key, value in metadata_filters.items():
            if value:
                filter_dict[key] = {"$eq": value}

    results = index.query(
        vector=embedding,
        top_k=k,
        include_metadata=True,
        namespace=settings.pinecone_namespace,
        filter=filter_dict if filter_dict else None,
    )

    return [
        {
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata,
        }
        for match in results.matches
    ]


def delete_namespace():
    """Delete all vectors in the namespace."""
    index = get_index()
    try:
        index.delete(delete_all=True, namespace=settings.pinecone_namespace)
    except Exception as exc:
        if not _is_not_found_error(exc):
            raise
