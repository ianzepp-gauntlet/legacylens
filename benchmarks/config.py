"""Benchmark configuration: test matrix, query suite, and scoring."""

from dataclasses import dataclass, field


@dataclass
class BenchmarkConfig:
    """A single benchmark configuration (one Pinecone index)."""

    name: str
    index_name: str
    embedding_provider: str  # "openai" | "pinecone"
    embedding_model: str
    embedding_dimensions: int
    chunking_strategy: str  # "paragraph" | "fixed"
    pinecone_model: str | None = None  # for Pinecone integrated indexes
    rerank_model: str | None = None  # e.g. "pinecone-rerank-v0"
    rerank_top_n: int | None = None  # rerank down from top_k to this
    sparse_index_name: str | None = None  # for hybrid: the sparse index to also query

    @property
    def is_pinecone_integrated(self) -> bool:
        return self.embedding_provider == "pinecone"

    @property
    def is_hybrid(self) -> bool:
        return self.sparse_index_name is not None


@dataclass
class BenchmarkQuery:
    """A benchmark query with expected results for relevance scoring."""

    query: str
    expected_files: list[str] = field(default_factory=list)
    expected_chunks: list[str] = field(default_factory=list)
    description: str = ""


TOP_K_VALUES = [3, 5, 10, 20, 50]
REPETITIONS = 3  # timing runs per query


def _build_openai_configs(
    model: str,
    short_name: str,
    dimensions: list[int],
) -> list[BenchmarkConfig]:
    configs = []
    for dims in dimensions:
        for chunking in ("paragraph", "fixed"):
            name = f"{short_name}-{dims}-{chunking}"
            configs.append(BenchmarkConfig(
                name=name,
                index_name=f"legacylens-bench-{name}",
                embedding_provider="openai",
                embedding_model=model,
                embedding_dimensions=dims,
                chunking_strategy=chunking,
            ))
    return configs


def _build_pinecone_configs(
    model: str,
    short_name: str,
    dimensions: int,
) -> list[BenchmarkConfig]:
    configs = []
    for chunking in ("paragraph", "fixed"):
        name = f"{short_name}-{dimensions}-{chunking}"
        configs.append(BenchmarkConfig(
            name=name,
            index_name=f"legacylens-bench-{name}",
            embedding_provider="pinecone",
            embedding_model=model,
            embedding_dimensions=dimensions,
            chunking_strategy=chunking,
            pinecone_model=model,
        ))
    return configs


SPARSE_INDEX_NAME = "legacylens-bench-sparse-paragraph"

CONFIGS: list[BenchmarkConfig] = [
    # OpenAI text-embedding-3-small: 512, 1024, 1536
    *_build_openai_configs("text-embedding-3-small", "small", [512, 1024, 1536]),
    # OpenAI text-embedding-3-large: 512, 1024, 1536
    *_build_openai_configs("text-embedding-3-large", "large", [512, 1024, 1536]),
    # Pinecone integrated models
    *_build_pinecone_configs("multilingual-e5-large", "e5", 1024),
    *_build_pinecone_configs("llama-text-embed-v2", "llama", 1024),
    # Reranking configs (best dense index + each reranker)
    BenchmarkConfig(
        name="llama-rerank-pinecone",
        index_name="legacylens-bench-llama-1024-paragraph",
        embedding_provider="pinecone",
        embedding_model="llama-text-embed-v2",
        embedding_dimensions=1024,
        chunking_strategy="paragraph",
        pinecone_model="llama-text-embed-v2",
        rerank_model="pinecone-rerank-v0",
        rerank_top_n=10,
    ),
    BenchmarkConfig(
        name="llama-rerank-bge",
        index_name="legacylens-bench-llama-1024-paragraph",
        embedding_provider="pinecone",
        embedding_model="llama-text-embed-v2",
        embedding_dimensions=1024,
        chunking_strategy="paragraph",
        pinecone_model="llama-text-embed-v2",
        rerank_model="bge-reranker-v2-m3",
        rerank_top_n=10,
    ),
    BenchmarkConfig(
        name="llama-rerank-cohere",
        index_name="legacylens-bench-llama-1024-paragraph",
        embedding_provider="pinecone",
        embedding_model="llama-text-embed-v2",
        embedding_dimensions=1024,
        chunking_strategy="paragraph",
        pinecone_model="llama-text-embed-v2",
        rerank_model="cohere-rerank-3.5",
        rerank_top_n=10,
    ),
    # Hybrid config (dense llama + sparse + rerank)
    BenchmarkConfig(
        name="llama-hybrid-rerank",
        index_name="legacylens-bench-llama-1024-paragraph",
        embedding_provider="pinecone",
        embedding_model="llama-text-embed-v2",
        embedding_dimensions=1024,
        chunking_strategy="paragraph",
        pinecone_model="llama-text-embed-v2",
        rerank_model="pinecone-rerank-v0",
        rerank_top_n=10,
        sparse_index_name=SPARSE_INDEX_NAME,
    ),
]


QUERY_SETS = {
    "curated": "benchmarks.queries_curated",
    "suggestions": "benchmarks.queries_suggestions",
}
DEFAULT_QUERY_SET = "curated"


def load_queries(query_set: str = DEFAULT_QUERY_SET) -> list[BenchmarkQuery]:
    """Load a query set by name ('curated' or 'suggestions')."""
    import importlib

    if query_set not in QUERY_SETS:
        raise ValueError(f"Unknown query set '{query_set}'. Available: {list(QUERY_SETS.keys())}")
    module = importlib.import_module(QUERY_SETS[query_set])
    # Convention: module exports QUERIES_CURATED or QUERIES_SUGGESTIONS
    attr = f"QUERIES_{query_set.upper()}"
    return getattr(module, attr)


def score_relevance(
    results: list[dict],
    query: BenchmarkQuery,
) -> float:
    """Score retrieval results against expected patterns.

    Returns a value between 0.0 and 1.0.
    """
    if not query.expected_files and not query.expected_chunks:
        return 1.0 if results else 0.0

    expected = query.expected_files + query.expected_chunks
    if not expected:
        return 1.0

    hits = 0
    result_files = [r.get("file_name", "") for r in results]
    result_names = [r.get("name", "") for r in results]
    all_result_text = " ".join(result_files + result_names).upper()

    for pattern in expected:
        if pattern.upper() in all_result_text:
            hits += 1

    return hits / len(expected)
