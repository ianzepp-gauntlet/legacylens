# LegacyLens

A RAG-powered system that makes legacy COBOL codebases queryable via natural language. Built for the AWS CardDemo credit card management application (~40K LOC across 206 mainframe source files).

## Architecture

```
Source Files ──> Parser ──> Chunker ──> Embeddings ──> Pinecone
                                                         │
User Query ──> Embed Query ──> Similarity Search ────────┘
                                       │
                              Retrieved Chunks ──> LLM ──> Answer + Citations
```

**Ingestion pipeline:** Files are discovered by extension, parsed with a COBOL-aware parser that detects sequence number formats and extracts divisions/paragraphs/COPY references/CALL targets, then chunked at syntactic boundaries (paragraphs for COBOL, DFHMDI for BMS, EXEC steps for JCL). Each chunk gets a descriptive preamble prepended before embedding.

**Retrieval pipeline:** User queries are embedded with the same model, matched against Pinecone via cosine similarity, and the top-k chunks are assembled into context for GPT-4o-mini, which generates answers with `[File:Line-Line]` citations.

### Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Vector DB | Pinecone Serverless | Free tier, managed, no infrastructure |
| Embedding model | Pinecone llama-text-embed-v2 (1024d) | Fastest + highest relevance in benchmarks |
| Chunking | Paragraph-level (COBOL), boundary-aware | Preserves semantic units; short paragraphs merged |
| LLM | GPT-4o-mini | Fast, cheap, sufficient for code Q&A |
| Framework | LangChain (core only) | Minimal abstraction, just prompt + LLM + parser |

### File Types Handled

| Type | Extension | Chunking Strategy |
|---|---|---|
| COBOL programs | `.cbl`, `.cob` | Header + DATA DIVISION (split at 01-level if >200 lines) + one chunk per paragraph |
| Copybooks | `.cpy` | Single chunk per file |
| BMS screen maps | `.bms` | Split on DFHMSD/DFHMDI boundaries |
| JCL job control | `.jcl` | Split on `//STEP EXEC` boundaries |
| Other mainframe | `.dcl`, `.ddl`, `.ctl`, `.csd`, `.dbd`, `.psb`, `.asm`, `.mac` | Single chunk per file |

## Setup

```bash
# Clone and install
git clone <repo-url>
cd legacylens
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your API keys and CardDemo path
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings and chat |
| `PINECONE_API_KEY` | Yes | Pinecone API key |
| `PINECONE_INDEX_NAME` | No | Index name (default: `legacylens`) |
| `CARDDEMO_PATH` | For ingestion | Path to CardDemo `app/` directory |
| `USE_OLLAMA` | No | Set `true` to use Ollama for local embeddings |

## Usage

### Ingest the codebase

```bash
python scripts/ingest_carddemo.py        # first run
python scripts/ingest_carddemo.py --clean # re-ingest from scratch
```

Output: 206 files parsed into ~1018 chunks, embedded and stored in Pinecone.

### CLI

```bash
# Ask a question (retrieval + LLM answer)
legacylens ask "What does the COCRDUPC program do?"

# Search only (no LLM, shows raw chunks)
legacylens search "credit card validation"

# Filter by file type
legacylens ask "How are VSAM files defined?" --type jcl
```

### Web UI

```bash
uvicorn web.app:app --port 8000
# Open http://localhost:8000
```

Single-page interface with query input, file type filter, LLM-generated answers, and collapsible source citations with relevance scores. Supports loading full file context from source links.

### API

```bash
# Ask with LLM answer
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does COCRDUPC do?", "top_k": 10}'

# Search only (no LLM)
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "credit card validation", "file_type": "cbl"}'

# Load full file context
curl -X POST http://localhost:8000/api/file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/COCRDUPC.cbl"}'
```

## Testing

```bash
# Unit tests (no API keys needed)
CARDDEMO_PATH=/path/to/carddemo/app pytest tests/ -v

# Include live retrieval tests against Pinecone
CARDDEMO_PATH=/path/to/carddemo/app LEGACYLENS_RUN_LIVE_TESTS=1 pytest tests/ -v
```

146 tests covering parser, chunker, ingestion, vector store, chain formatting, live retrieval quality, and benchmark infrastructure.

## Benchmarking

A performance benchmark suite compares retrieval latency and relevance across different embedding models, vector dimensions, chunking strategies, and top-k values.

### Test Matrix (16 index configurations)

| Model | Provider | Dimensions | Indexes |
|---|---|---|---|
| `text-embedding-3-small` | OpenAI | 512, 1024, 1536 | 6 (× 2 chunking strategies) |
| `text-embedding-3-large` | OpenAI | 512, 1024, 1536 | 6 (× 2 chunking strategies) |
| `multilingual-e5-large` | Pinecone integrated | 1024 | 2 (× 2 chunking strategies) |
| `llama-text-embed-v2` | Pinecone integrated | 1024 | 2 (× 2 chunking strategies) |

**Chunking strategies:** `paragraph` (syntax-aware, current default) and `fixed` (~500-token chunks with overlap).

**Top-k values:** 3, 5, 10, 20, 50.

Each configuration creates a separate Pinecone index named `legacylens-bench-{model}-{dims}-{chunking}`.

### Query Suite

10 predefined queries with expected file/chunk patterns for automated relevance scoring. Each query is run 3 times per configuration for timing stability. Metrics collected:

- **Latency:** mean, p50, p95, min, max (seconds)
- **Relevance:** fraction of expected files/chunks found in results (0.0 - 1.0)

### Results (2026-03-03)

Benchmark run: 16 configs, 10 queries, 5 top-k values (3/5/10/20/50), 3 repetitions per query (800 total query runs).

#### Overall Summary (ranked by relevance, then latency)

| Config | Avg Latency | Avg Relevance |
|---|--:|--:|
| **llama-1024-paragraph** | **0.459s** | **0.78** |
| small-1536-paragraph | 0.634s | 0.77 |
| small-1024-paragraph | 0.634s | 0.76 |
| small-512-paragraph | 0.633s | 0.76 |
| large-1024-paragraph | 0.666s | 0.74 |
| large-1536-paragraph | 0.642s | 0.74 |
| e5-1024-paragraph | 0.467s | 0.70 |
| large-512-paragraph | 0.607s | 0.70 |
| small-1536-fixed | 0.628s | 0.60 |
| small-1024-fixed | 0.648s | 0.59 |
| small-512-fixed | 0.598s | 0.58 |
| llama-1024-fixed | 0.427s | 0.57 |
| e5-1024-fixed | 0.436s | 0.53 |
| large-1536-fixed | 0.605s | 0.51 |
| large-1024-fixed | 0.651s | 0.49 |
| large-512-fixed | 0.595s | 0.47 |

#### Key Findings

1. **Paragraph chunking wins decisively.** Every paragraph config outperforms its fixed-size counterpart in relevance (0.70-0.78 vs 0.47-0.60). The COBOL-aware syntax chunking preserves meaningful code boundaries that matter for retrieval.

2. **Pinecone integrated models are ~30% faster.** Llama/E5 at 0.43-0.47s vs OpenAI at 0.60-0.67s. Server-side embedding eliminates the client-side API round-trip.

3. **`llama-text-embed-v2` is the best overall.** Fastest paragraph config (0.459s) with the highest relevance (0.78). Both fastest and most accurate.

4. **Dimension size barely matters for OpenAI `small`.** 512, 1024, and 1536 dimensions all score 0.76-0.77 relevance. Extra dimensions add latency without improving retrieval quality for this codebase.

5. **`text-embedding-3-large` offers no advantage.** Slower than `small` with equal or worse relevance. The COBOL-specific preambles and chunking strategy contribute more to retrieval quality than embedding model size.

6. **Hardest queries across all configs:** "File I/O operations" and "CICS screen navigation" consistently score low, suggesting the expected result patterns for these queries may need refinement.

### Running Benchmarks

```bash
# 1. Ingest into all 16 indexes (or a subset)
python benchmarks/ingest_all.py
python benchmarks/ingest_all.py --configs small-512-paragraph,large-1024-fixed
python benchmarks/ingest_all.py --clean  # delete and re-create indexes

# 2. Run benchmark suite
python benchmarks/run_benchmark.py
python benchmarks/run_benchmark.py --configs small-512-paragraph --top-k 5,10

# 3. Analyze results
python benchmarks/report.py                               # latest results
python benchmarks/report.py benchmarks/results/file.json  # specific file
```

Results are saved to `benchmarks/results/` as JSON (full detail) and CSV (summary). The report produces:
- Overall summary table ranked by relevance then latency
- Per-top-k breakdown
- Model comparison (averaged across chunking strategies)
- Chunking strategy comparison (paragraph vs fixed)

## Project Structure

```
legacylens/
├── legacylens/
│   ├── config.py          # Pydantic settings
│   ├── models.py          # CodeChunk, QueryResult dataclasses
│   ├── parser.py          # COBOL structure parser (divisions, paragraphs, COPY/CALL)
│   ├── chunker.py         # Syntax-aware + fixed-size chunking (COBOL/BMS/JCL/copybook)
│   ├── embeddings.py      # OpenAI / Ollama embedding generation
│   ├── vectorstore.py     # Pinecone index operations
│   ├── ingest.py          # Orchestrator: discover → chunk → embed → store
│   ├── retriever.py       # Query embedding + Pinecone search
│   ├── chain.py           # LangChain RAG chain (context + LLM)
│   └── cli.py             # Typer CLI (ask, search, ingest)
├── benchmarks/
│   ├── config.py          # Test matrix (16 configs), query suite, relevance scoring
│   ├── ingest_all.py      # Multi-index ingestion (OpenAI + Pinecone integrated)
│   ├── run_benchmark.py   # Benchmark runner (latency + relevance)
│   ├── report.py          # Results analysis and summary tables
│   └── results/           # JSON + CSV output
├── web/
│   ├── app.py             # FastAPI endpoints
│   └── templates/
│       └── index.html     # Single-page query UI
├── scripts/
│   └── ingest_carddemo.py # One-shot ingestion runner
└── tests/
    ├── test_parser.py     # 30 tests
    ├── test_chunker.py    # 29 tests
    ├── test_ingest.py     # 14 tests
    ├── test_vectorstore.py# 8 tests
    ├── test_chain.py      # 9 tests
    ├── test_retrieval.py  # 13 tests (6 live + 7 chunking)
    └── test_benchmark.py  # 23 tests (configs, queries, relevance scoring, fixed chunker)
```

## Deployment

```bash
# Railway / Render
uvicorn web.app:app --host 0.0.0.0 --port $PORT
```

Set `OPENAI_API_KEY` and `PINECONE_API_KEY` as environment variables. The Pinecone index persists in the cloud — ingestion only needs to run once locally.
