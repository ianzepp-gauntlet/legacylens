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


QUERIES: list[BenchmarkQuery] = [
    # ── User Management (2) ──
    BenchmarkQuery(
        query="What does COUSR00C do?",
        expected_files=["COUSR00C"],
        expected_chunks=["RECEIVE-USRLST-SCREEN", "SEND-USRLST-SCREEN"],
        description="Identify user list program",
    ),
    BenchmarkQuery(
        query="How does the sign-on screen COSGN00C work?",
        expected_files=["COSGN00C"],
        expected_chunks=["SEND-SIGNON-SCREEN", "MAIN-PARA"],
        description="Sign-on screen logic",
    ),
    # ── Account Processing (2) ──
    BenchmarkQuery(
        query="What does COACTUPC do for account updates?",
        expected_files=["COACTUPC"],
        expected_chunks=["9000-READ-ACCT"],
        description="Account update program",
    ),
    BenchmarkQuery(
        query="What is the account record structure in CVACT01Y?",
        expected_files=["CVACT01Y"],
        expected_chunks=[],
        description="Account record copybook lookup",
    ),
    # ── Card Processing (2) ──
    BenchmarkQuery(
        query="How are credit card numbers validated?",
        expected_files=["COCRDSLC", "COCRDUPC", "COCRDLIC"],
        expected_chunks=["EDIT-CARD"],
        description="Credit card validation logic",
    ),
    BenchmarkQuery(
        query="How does the card list BMS map COCRDLI work?",
        expected_files=["COCRDLI"],
        expected_chunks=["CCRDLIA"],
        description="Card list BMS map",
    ),
    # ── Transaction Processing (2) ──
    BenchmarkQuery(
        query="How does CBTRN01C process daily transactions?",
        expected_files=["CBTRN01C"],
        expected_chunks=["1000-DALYTRAN-GET-NEXT", "0000-DALYTRAN-OPEN"],
        description="Daily transaction batch processing",
    ),
    BenchmarkQuery(
        query="How are transaction amounts validated?",
        expected_files=["COTRN02C", "CBTRN02C"],
        expected_chunks=["VALIDATE"],
        description="Transaction amount validation",
    ),
    # ── Export/Import (2) ──
    BenchmarkQuery(
        query="How does CBEXPORT export customer data?",
        expected_files=["CBEXPORT"],
        expected_chunks=["2200-CREATE-CUSTOMER-EXP-REC", "2000-EXPORT-CUSTOMERS"],
        description="Customer data export",
    ),
    BenchmarkQuery(
        query="What validation does CBIMPORT perform on import?",
        expected_files=["CBIMPORT"],
        expected_chunks=["3000-VALIDATE-IMPORT", "0000-MAIN-PROCESSING"],
        description="Import validation logic",
    ),
    # ── Admin & Menu (2) ──
    BenchmarkQuery(
        query="How does the menu program COMEN01C work?",
        expected_files=["COMEN01C"],
        expected_chunks=["POPULATE-HEADER-INFO", "MAIN-PARA"],
        description="Main menu program",
    ),
    BenchmarkQuery(
        query="What admin options are in COADM02Y?",
        expected_files=["COADM02Y"],
        expected_chunks=["BUILD-MENU-OPTIONS"],
        description="Admin options copybook",
    ),
    # ── Date/Utility Programs (2) ──
    BenchmarkQuery(
        query="How does CSUTLDTC handle date and time?",
        expected_files=["CSUTLDTC"],
        expected_chunks=["A000-MAIN"],
        description="Date/time utility program",
    ),
    BenchmarkQuery(
        query="How is GENERATE-TIMESTAMP implemented?",
        expected_files=["CBEXPORT"],
        expected_chunks=["1050-GENERATE-TIMESTAMP"],
        description="Timestamp generation",
    ),
    # ── Copybook Structures (2) ──
    BenchmarkQuery(
        query="What is the customer record structure in CVCUS01Y?",
        expected_files=["CVCUS01Y"],
        expected_chunks=[],
        description="Customer record copybook",
    ),
    BenchmarkQuery(
        query="Explain the communication area COCOM01Y",
        expected_files=["COCOM01Y"],
        expected_chunks=["DFHCOMMAREA"],
        description="Communication area copybook",
    ),
    # ── BMS Maps & Screens (2) ──
    BenchmarkQuery(
        query="How is the sign-on BMS map COSGN00 structured?",
        expected_files=["COSGN00"],
        expected_chunks=["COSGN0A"],
        description="Sign-on BMS map structure",
    ),
    BenchmarkQuery(
        query="What does the card update map COCRDUP contain?",
        expected_files=["COCRDUP"],
        expected_chunks=["CCRDUPA"],
        description="Card update BMS map",
    ),
    # ── JCL Jobs (2) ──
    BenchmarkQuery(
        query="How does the POSTTRAN JCL post transactions?",
        expected_files=["POSTTRAN"],
        expected_chunks=["2000-POST-TRANSACTION"],
        description="Transaction posting JCL",
    ),
    BenchmarkQuery(
        query="What does the CREADB21 JCL create in DB2?",
        expected_files=["CREADB21"],
        expected_chunks=[],
        description="DB2 creation JCL",
    ),
    # ── CICS Operations (2) ──
    BenchmarkQuery(
        query="How is the COMMAREA used for inter-program communication?",
        expected_files=["COCOM01Y"],
        expected_chunks=["WS-COMMAREA"],
        description="COMMAREA inter-program communication",
    ),
    BenchmarkQuery(
        query="How does CICS RECEIVE capture user input?",
        expected_files=["COUSR00C", "COUSR01C", "COMEN01C"],
        expected_chunks=["RECEIVE"],
        description="CICS RECEIVE operations",
    ),
    # ── DB2 Operations (2) ──
    BenchmarkQuery(
        query="How is the SQLCA used for DB2 error handling?",
        expected_files=["CSDB2RPY"],
        expected_chunks=[],
        description="SQLCA DB2 error handling",
    ),
    BenchmarkQuery(
        query="What DB2 tables does CardDemo define?",
        expected_files=["DB2CREAT"],
        expected_chunks=[],
        description="DB2 table definitions",
    ),
    # ── VSAM File Operations (2) ──
    BenchmarkQuery(
        query="What VSAM file status codes are checked?",
        expected_files=["CBTRN02C", "CBTRN03C", "CBACT01C"],
        expected_chunks=["9910-DISPLAY-IO-STATUS"],
        description="VSAM file status code checks",
    ),
    BenchmarkQuery(
        query="How does STARTBR begin a VSAM browse?",
        expected_files=["COTRN00C", "COUSR00C"],
        expected_chunks=["STARTBR"],
        description="VSAM browse start operations",
    ),
    # ── Paragraph/Section Patterns (2) ──
    BenchmarkQuery(
        query="What does the MAIN-PARA entry point do?",
        expected_files=["COMEN01C", "COADM01C"],
        expected_chunks=["MAIN-PARA"],
        description="MAIN-PARA entry point",
    ),
    BenchmarkQuery(
        query="How does PROCESS-ENTER-KEY handle user input?",
        expected_files=["COTRN00C", "COSGN00C"],
        expected_chunks=["PROCESS-ENTER-KEY"],
        description="Enter key processing pattern",
    ),
    # ── Data Elements (2) ──
    BenchmarkQuery(
        query="What is WS-PGMNAME used for?",
        expected_files=[],
        expected_chunks=["DATA DIVISION"],
        description="WS-PGMNAME working storage variable",
    ),
    BenchmarkQuery(
        query="What is in the DFHCOMMAREA linkage section?",
        expected_files=["COCOM01Y"],
        expected_chunks=["DFHCOMMAREA"],
        description="DFHCOMMAREA linkage section",
    ),
    # ── Cross-Cutting Concerns (2) ──
    BenchmarkQuery(
        query="How does RETURN-TO-PREV-SCREEN navigate on errors?",
        expected_files=["COUSR02C", "COTRN02C"],
        expected_chunks=["RETURN-TO-PREV-SCREEN"],
        description="Screen return navigation pattern",
    ),
    BenchmarkQuery(
        query="How do programs pass data via the communication area?",
        expected_files=["COCOM01Y"],
        expected_chunks=["WS-COMMAREA"],
        description="Communication area data passing",
    ),
    # ── Business Domain (2) ──
    BenchmarkQuery(
        query="How does CardDemo handle interest calculation?",
        expected_files=["CBACT04C", "INTCALC"],
        expected_chunks=["1300-COMPUTE-INTEREST"],
        description="Interest calculation logic",
    ),
    BenchmarkQuery(
        query="How are transaction categories and types classified?",
        expected_files=["CVTRA03Y", "CVTRA04Y"],
        expected_chunks=[],
        description="Transaction category/type classification",
    ),
    # ── Architecture & Integration (2) ──
    BenchmarkQuery(
        query="What batch vs online programs exist?",
        expected_files=["CBTRN01C", "CBACT01C"],
        expected_chunks=[],
        description="Batch vs online program inventory",
    ),
    BenchmarkQuery(
        query="How do copybooks reduce code duplication?",
        expected_files=["COCOM01Y", "CSUSR01Y"],
        expected_chunks=[],
        description="Copybook reuse patterns",
    ),
    # ── Specific Operations (2) ──
    BenchmarkQuery(
        query="How does LOOKUP-XREF perform cross-reference lookups?",
        expected_files=["CBACT03C", "CVACT03Y"],
        expected_chunks=["XREF"],
        description="Cross-reference lookup operation",
    ),
    BenchmarkQuery(
        query="What does HANDLE-DB2-ERROR do on SQL failures?",
        expected_files=["COPAUS2C"],
        expected_chunks=["FRAUD-UPDATE"],
        description="DB2 error handler",
    ),
    # ── File Definitions (2) ──
    BenchmarkQuery(
        query="How does COMBTRAN combine transaction data?",
        expected_files=["COMBTRAN"],
        expected_chunks=[],
        description="Transaction data combining JCL",
    ),
    BenchmarkQuery(
        query="What does the DUSRSECJ JCL do for user security?",
        expected_files=["DUSRSECJ"],
        expected_chunks=[],
        description="User security file JCL",
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
