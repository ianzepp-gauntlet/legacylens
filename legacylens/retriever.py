"""Query embedding and Pinecone search."""

from .embeddings import get_query_embedding
from .models import QueryResult
from .vectorstore import query_vectors


def retrieve(
    query: str,
    top_k: int | None = None,
    file_type: str | None = None,
    metadata_filters: dict[str, str] | None = None,
) -> list[QueryResult]:
    """Embed a query and retrieve matching code chunks."""
    embedding = get_query_embedding(query)
    raw_results = query_vectors(
        embedding,
        top_k=top_k,
        file_type_filter=file_type,
        metadata_filters=metadata_filters,
    )

    results = []
    for r in raw_results:
        meta = r["metadata"]
        copy_references = [ref for ref in meta.get("copy_references", "").split(",") if ref]
        calls_to = [call for call in meta.get("calls_to", "").split(",") if call]
        results.append(QueryResult(
            content=meta.get("content", ""),
            file_path=meta.get("file_path", ""),
            file_name=meta.get("file_name", ""),
            file_type=meta.get("file_type", ""),
            chunk_type=meta.get("chunk_type", ""),
            name=meta.get("name", ""),
            start_line=meta.get("start_line", 0),
            end_line=meta.get("end_line", 0),
            score=r["score"],
            preamble=meta.get("preamble", ""),
            comments=meta.get("comments", ""),
            copy_references=copy_references,
            calls_to=calls_to,
        ))

    return results
