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

    @property
    def is_pinecone_integrated(self) -> bool:
        return self.embedding_provider == "pinecone"


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


CONFIGS: list[BenchmarkConfig] = [
    # OpenAI text-embedding-3-small: 512, 1024, 1536
    *_build_openai_configs("text-embedding-3-small", "small", [512, 1024, 1536]),
    # OpenAI text-embedding-3-large: 512, 1024, 1536
    *_build_openai_configs("text-embedding-3-large", "large", [512, 1024, 1536]),
    # Pinecone integrated models
    *_build_pinecone_configs("multilingual-e5-large", "e5", 1024),
    *_build_pinecone_configs("llama-text-embed-v2", "llama", 1024),
]


QUERIES: list[BenchmarkQuery] = [
    BenchmarkQuery(
        query="Where is the main entry point of the CardDemo application?",
        expected_files=["COMEN01", "COSGN00"],
        expected_chunks=["MAIN", "PROCESS"],
        description="Find main menu / sign-on entry point",
    ),
    BenchmarkQuery(
        query="What does the COCRDUPC program do?",
        expected_files=["COCRDUPC"],
        expected_chunks=[],
        description="Identify credit card update program",
    ),
    BenchmarkQuery(
        query="Find all file I/O operations and VSAM file handling",
        expected_files=["CBACT", "CBTRN"],
        expected_chunks=["READ", "WRITE", "OPEN", "CLOSE"],
        description="Locate file I/O code",
    ),
    BenchmarkQuery(
        query="What are the dependencies and COPY references of COCRDUPC?",
        expected_files=["COCRDUPC"],
        expected_chunks=[],
        description="Find COPY dependencies",
    ),
    BenchmarkQuery(
        query="What functions modify the customer record?",
        expected_files=["CUS"],
        expected_chunks=[],
        description="Find customer record modification code",
    ),
    BenchmarkQuery(
        query="How are credit cards validated?",
        expected_files=["COCRDSLC", "COCRDUPC"],
        expected_chunks=["EDIT", "VALID"],
        description="Find credit card validation logic",
    ),
    BenchmarkQuery(
        query="How does the sign-on screen authenticate users?",
        expected_files=["COSGN00"],
        expected_chunks=["SIGN", "AUTH", "PROCESS"],
        description="Find authentication logic",
    ),
    BenchmarkQuery(
        query="What batch jobs process transaction files?",
        expected_files=["CBTRN", "CBACT"],
        expected_chunks=[],
        description="Find batch transaction processing",
    ),
    BenchmarkQuery(
        query="How are BMS screen maps defined for the credit card display?",
        expected_files=["COCRDSL", "COCRDUP"],
        expected_chunks=[],
        description="Find BMS screen definitions",
    ),
    BenchmarkQuery(
        query="What CICS commands are used for screen navigation?",
        expected_files=["COMEN", "COSGN"],
        expected_chunks=["SEND", "RECEIVE", "RETURN", "XCTL"],
        description="Find CICS screen navigation",
    ),
]


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
