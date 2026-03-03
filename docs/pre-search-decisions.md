# Pre-Search Decisions

## Phase 1: Constraints

### Scale & Load Profile
- **Target codebase:** AWS CardDemo (aws-mainframe-modernization-carddemo)
  - Credit card management mainframe application (COBOL/CICS/VSAM/JCL)
  - 44 COBOL programs (~28K LOC), 62 copybooks (~10.7K LOC), 106 COBOL files total (~40.8K LOC)
  - Plus JCL, BMS maps, DDL, assembly — rich supporting artifacts
  - Real business logic: accounts, cards, transactions, bill payments, statements
  - Intentionally varied coding styles for analysis tooling — ideal for RAG
  - Apache 2.0 licensed, well-documented
- **Exceeds minimum:** 10,000+ LOC across 50+ files
- **Query volume:** Low steady-state (developer + reviewers), spiky from automated parallel evals
- **Ingestion:** Batch (one-time ingest of static codebase)
- **Latency target:** <3 seconds end-to-end

### Budget & Cost Ceiling
- **Overall budget:** ~$100/month comfortable
- **Embedding costs:** No ceiling (negligible for codebase size)
- **LLM costs:** No ceiling, OpenAI
- **Preference:** Managed services to save time

### Time to Ship
- **MVP deadline:** Tuesday night (36 hours real time, 16-20 hours work)
- **4-of-8 code understanding features:** Deferred to Final submission
- **Framework:** LangChain (prework exposure lowers learning curve)

### Data Sensitivity
- **Codebase:** Open source, no restrictions
- **External APIs:** No concerns sending code to OpenAI/Pinecone
- **Data residency:** US data center expected, not a hard requirement

### Team & Skill Constraints
- **Vector databases:** Very limited experience
- **RAG frameworks:** First exposure (cookbook prework only)
- **COBOL:** No experience reading COBOL code

## Phase 2: Architecture Decisions

### Vector Database: Pinecone
- Managed cloud, free tier for MVP, paid tier for final submission
- Hybrid search (vector + keyword) enabled
- Metadata fields: file path, line numbers, section type, function/paragraph name, has_comments
- Comments are high-priority content — preserve alongside associated code

### Embedding Strategy
- **Model:** OpenAI text-embedding-3-small (1536 dimensions)
- **Fallback/alternative:** Can switch to text-embedding-3-large if quality is poor (re-index takes minutes)
- **Local toggle:** Ollama support for offline dev/testing (configurable provider)
- **Batch processing:** Optimize later

### Chunking Approach
- **Strategy:** Syntax-aware from the start (COBOL DIVISIONs, SECTIONs, PARAGRAPHs)
- **Max chunk size:** ~1000 tokens, split if exceeded
- **Overlap strategy:** Deferred until codebase is reviewed
- **Fallback:** Fixed-size + overlap for anything that doesn't parse cleanly

### Retrieval Pipeline
- **Top-k:** 10 (configurable)
- **Re-ranking:** None for MVP
- **Context window management:** None for MVP
- **Multi-query / query expansion:** Deferred (not MVP)
- **Dynamic k (LLM-suggested):** Stretch goal

### Answer Generation
- **LLM:** OpenAI (GPT-4o and GPT-4o-mini, configurable, test both)
- **Prompt design:** Keep simple for MVP
- **Citations:** Inline file/line references, e.g. `(file.cob:42-58)`
- **Streaming:** No, full response for MVP

### Framework: LangChain
- Pairs with OpenAI + Pinecone
- Prior exposure from RAG cookbook prework

## Phase 3: Deferred to Implementation

- Evaluation & observability
- Failure mode analysis
- Evaluation strategy
- Performance optimization
- Observability / logging / metrics
- Deployment & DevOps
