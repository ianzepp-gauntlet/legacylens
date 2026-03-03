# RAG Cookbook Summary

A progressive, hands-on tutorial for building RAG (Retrieval-Augmented Generation) systems, using Warren Buffett's Berkshire Hathaway shareholder letters (2004–2023) as the corpus.

## Tech Stack

- **Python** + **LangChain** + **OpenAI** (gpt-4o-mini, text-embedding-3-small)
- **MongoDB Atlas** for vector storage
- **Neo4j** for knowledge graphs (step 04 only)
- **rank_bm25** for keyword search (step 03)

## Modules

### 01 — Naive RAG

Core RAG pipeline: load PDFs, chunk text (1000 tokens, 200 overlap), create embeddings with text-embedding-3-small, store in MongoDB, retrieve via vector similarity, generate answers with an LLM.

**Evals:** Precision (LLM-as-judge relevance) and Groundedness (hallucination detection).

### 02 — Metadata-Filtered RAG

Enhances ingestion with rich metadata: year, decade, topic buckets (insurance, acquisitions, investments, etc.), companies mentioned, and financial content flags. Pre-filters documents by metadata before vector search to narrow the result set.

**Evals:** Latency measurement and Precision Delta (improvement vs. naive RAG).

### 03 — Hybrid Search

Combines BM25 keyword search with vector semantic search using Reciprocal Rank Fusion (RRF). Tunable weights let you favor keyword or semantic results depending on query type. Reuses MongoDB vectors from earlier steps.

### 04 — Graph RAG

Builds a Neo4j knowledge graph by extracting entities (companies, people, concepts) and their relationships from chunks. Retrieval combines graph traversal (1–2 hops) with vector search, boosting chunks that have graph connections. Enables multi-hop reasoning (e.g., "How did Buffett's insurance business connect to GEICO?").

**Evals:** Entity extraction accuracy and multi-hop reasoning verification.

### 05 — Agentic RAG

A ReAct (Reason + Act) agent that dynamically decides whether and how to retrieve. Three tools: `no_retrieval` (answer from model knowledge), `vector_search` (general semantic search), and `filtered_search` (metadata-filtered vector search). The agent decomposes complex queries into sub-questions, executes retrieval for each, evaluates sufficiency, and synthesizes a final answer.

**Evals:** Tool selection accuracy, query decomposition quality, and end-to-end pipeline evaluation.

## Key Design Patterns

- **Progressive complexity:** each step is self-contained and builds on the previous one.
- **Reusability:** steps 03–05 reuse MongoDB vectors from earlier steps (no re-ingestion).
- **LLM-as-Judge:** evaluations use the LLM itself to assess retrieval precision, groundedness, and answer quality.
- **Separation of concerns:** each step separates ingestion, retrieval, and generation into distinct scripts.

## Corpus

20 Berkshire Hathaway shareholder letters (2004–2023), ~6.5MB of PDFs covering insurance, acquisitions, investments, management philosophy, and market commentary. Chosen for temporal diversity, topic variety, and rich named entities.

## Configuration

- Vector dimensions: 1536 (text-embedding-3-small)
- Chunking: 1000 tokens, 200-token overlap
- MongoDB collections: `naive_rag`, `metadata_filtered_rag`
- Vector indexes must be created manually in MongoDB Atlas UI
- LLM temperature: 0.0 for deterministic evaluation
