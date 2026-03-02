"""Embedding generation using OpenAI or Ollama."""

from openai import OpenAI

from .config import settings


def get_embeddings(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    if settings.use_ollama:
        return _ollama_embeddings(texts, batch_size)
    return _openai_embeddings(texts, batch_size)


def get_query_embedding(text: str) -> list[float]:
    """Generate embedding for a single query."""
    return get_embeddings([text])[0]


def _openai_embeddings(texts: list[str], batch_size: int) -> list[list[float]]:
    client = OpenAI(api_key=settings.openai_api_key)
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
            dimensions=settings.embedding_dimensions,
        )
        all_embeddings.extend([d.embedding for d in response.data])

    return all_embeddings


def _ollama_embeddings(texts: list[str], batch_size: int) -> list[list[float]]:
    client = OpenAI(
        base_url=f"{settings.ollama_base_url}/v1",
        api_key="ollama",
    )
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=settings.ollama_embed_model,
            input=batch,
        )
        all_embeddings.extend([d.embedding for d in response.data])

    return all_embeddings
