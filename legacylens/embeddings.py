"""Embedding generation using OpenAI or Ollama."""

from collections.abc import Callable

from openai import OpenAI

from .config import settings


def _default_client_factory(**kwargs) -> OpenAI:
    return OpenAI(**kwargs)


def get_embeddings(
    texts: list[str],
    batch_size: int = 100,
    *,
    use_ollama: bool | None = None,
    client_factory: Callable[..., OpenAI] | None = None,
) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    active_client_factory = client_factory or _default_client_factory
    if use_ollama if use_ollama is not None else settings.use_ollama:
        return _ollama_embeddings(texts, batch_size, client_factory=active_client_factory)
    return _openai_embeddings(texts, batch_size, client_factory=active_client_factory)


def get_query_embedding(
    text: str,
    *,
    use_ollama: bool | None = None,
    client_factory: Callable[..., OpenAI] | None = None,
) -> list[float]:
    """Generate embedding for a single query."""
    return get_embeddings(
        [text],
        use_ollama=use_ollama,
        client_factory=client_factory,
    )[0]


def _openai_embeddings(
    texts: list[str],
    batch_size: int,
    *,
    client_factory: Callable[..., OpenAI],
) -> list[list[float]]:
    client = client_factory(api_key=settings.openai_api_key)
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


def _ollama_embeddings(
    texts: list[str],
    batch_size: int,
    *,
    client_factory: Callable[..., OpenAI],
) -> list[list[float]]:
    client = client_factory(
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
