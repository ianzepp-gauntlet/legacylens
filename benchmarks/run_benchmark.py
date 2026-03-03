"""Run the benchmark suite across all configurations.

Usage:
    python benchmarks/run_benchmark.py
    python benchmarks/run_benchmark.py --configs small-256-paragraph,large-1024-fixed
    python benchmarks/run_benchmark.py --top-k 5,10
"""

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, SearchQuery, SearchRerank

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.config import (
    CONFIGS,
    QUERIES,
    REPETITIONS,
    TOP_K_VALUES,
    BenchmarkConfig,
    BenchmarkQuery,
    score_relevance,
)
from legacylens.config import settings
from legacylens.vectorstore import METADATA_CONTENT_LIMIT


NAMESPACE = "carddemo"
TEXT_FIELD = "chunk_text"  # must match the field_map used during index creation
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _embed_query_openai(client: OpenAI, query: str, config: BenchmarkConfig) -> list[float]:
    response = client.embeddings.create(
        model=config.embedding_model,
        input=[query],
        dimensions=config.embedding_dimensions,
    )
    return response.data[0].embedding


def _query_openai_index(
    pc: Pinecone,
    openai_client: OpenAI,
    config: BenchmarkConfig,
    query: str,
    top_k: int,
) -> tuple[list[dict], float]:
    """Query an OpenAI-embedded index. Returns (results, elapsed_seconds)."""
    start = time.perf_counter()

    embedding = _embed_query_openai(openai_client, query, config)
    index = pc.Index(config.index_name)
    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=NAMESPACE,
    )

    elapsed = time.perf_counter() - start

    results = []
    for match in response.matches:
        results.append({
            "id": match.id,
            "score": match.score,
            "file_name": match.metadata.get("file_name", ""),
            "name": match.metadata.get("name", ""),
            "chunk_type": match.metadata.get("chunk_type", ""),
            "file_type": match.metadata.get("file_type", ""),
        })

    return results, elapsed


def _parse_search_hits(response) -> list[dict]:
    """Extract result dicts from a Pinecone search response."""
    results = []
    for hit in response.result.hits:
        fields = hit.fields or {}
        results.append({
            "id": hit.id,
            "score": hit.score,
            "file_name": fields.get("file_name", ""),
            "name": fields.get("name", ""),
            "chunk_type": fields.get("chunk_type", ""),
            "file_type": fields.get("file_type", ""),
        })
    return results


def _query_pinecone_integrated(
    pc: Pinecone,
    config: BenchmarkConfig,
    query: str,
    top_k: int,
) -> tuple[list[dict], float]:
    """Query a Pinecone integrated-embedding index.

    Supports optional reranking via config.rerank_model.
    Over-fetches at 2× top_k when reranking, then reranks down to rerank_top_n.
    """
    start = time.perf_counter()

    index = pc.Index(config.index_name)
    fetch_k = top_k * 2 if config.rerank_model else top_k

    rerank = None
    if config.rerank_model:
        rerank = SearchRerank(
            model=config.rerank_model,
            rank_fields=[TEXT_FIELD],
            top_n=config.rerank_top_n or top_k,
        )

    response = index.search(
        namespace=NAMESPACE,
        query=SearchQuery(
            inputs={"text": query},
            top_k=fetch_k,
        ),
        rerank=rerank,
    )

    elapsed = time.perf_counter() - start
    return _parse_search_hits(response), elapsed


def _query_hybrid(
    pc: Pinecone,
    config: BenchmarkConfig,
    query: str,
    top_k: int,
) -> tuple[list[dict], float]:
    """Hybrid search: query dense + sparse indexes, merge, then rerank.

    1. Query the dense index (llama) for top_k * 2 results
    2. Query the sparse index for top_k * 2 results
    3. Merge by record ID (union, deduplicate — keep higher score)
    4. Rerank merged set down to rerank_top_n
    """
    start = time.perf_counter()

    dense_index = pc.Index(config.index_name)
    sparse_index = pc.Index(config.sparse_index_name)
    fetch_k = top_k * 2

    search_query = SearchQuery(inputs={"text": query}, top_k=fetch_k)

    # Query both indexes
    dense_response = dense_index.search(
        namespace=NAMESPACE,
        query=search_query,
    )
    sparse_response = sparse_index.search(
        namespace=NAMESPACE,
        query=search_query,
    )

    # Merge by ID — keep the hit with the higher score on collision
    merged: dict[str, dict] = {}
    for hit in dense_response.result.hits:
        fields = hit.fields or {}
        merged[hit.id] = {
            "id": hit.id,
            "score": hit.score,
            "file_name": fields.get("file_name", ""),
            "name": fields.get("name", ""),
            "chunk_type": fields.get("chunk_type", ""),
            "file_type": fields.get("file_type", ""),
            TEXT_FIELD: fields.get(TEXT_FIELD, ""),
        }
    for hit in sparse_response.result.hits:
        fields = hit.fields or {}
        if hit.id not in merged or hit.score > merged[hit.id]["score"]:
            merged[hit.id] = {
                "id": hit.id,
                "score": hit.score,
                "file_name": fields.get("file_name", ""),
                "name": fields.get("name", ""),
                "chunk_type": fields.get("chunk_type", ""),
                "file_type": fields.get("file_type", ""),
                TEXT_FIELD: fields.get(TEXT_FIELD, ""),
            }

    # Rerank merged results using Pinecone inference API
    merged_list = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    rerank_top_n = config.rerank_top_n or top_k

    if config.rerank_model and len(merged_list) > 0:
        documents = [
            {"id": doc["id"], TEXT_FIELD: doc.get(TEXT_FIELD, "")}
            for doc in merged_list
        ]
        rerank_response = pc.inference.rerank(
            model=config.rerank_model,
            query=query,
            documents=documents,
            rank_fields=[TEXT_FIELD],
            top_n=rerank_top_n,
        )
        # Rebuild results in reranked order
        results = []
        for item in rerank_response.data:
            doc = merged_list[item.index]
            results.append({
                "id": doc["id"],
                "score": item.score,
                "file_name": doc["file_name"],
                "name": doc["name"],
                "chunk_type": doc["chunk_type"],
                "file_type": doc["file_type"],
            })
    else:
        results = [
            {k: v for k, v in doc.items() if k != TEXT_FIELD}
            for doc in merged_list[:rerank_top_n]
        ]

    elapsed = time.perf_counter() - start
    return results, elapsed


def run_single_query(
    pc: Pinecone,
    openai_client: OpenAI | None,
    config: BenchmarkConfig,
    query: BenchmarkQuery,
    top_k: int,
    repetitions: int,
) -> dict:
    """Run a single query against a config, timing multiple repetitions."""
    timings = []
    last_results = []
    relevance_scores = []

    for _ in range(repetitions):
        if config.is_hybrid:
            results, elapsed = _query_hybrid(pc, config, query.query, top_k)
        elif config.is_pinecone_integrated:
            results, elapsed = _query_pinecone_integrated(pc, config, query.query, top_k)
        else:
            if openai_client is None:
                raise ValueError(
                    f"OpenAI client is required for non-integrated config: {config.name}"
                )
            results, elapsed = _query_openai_index(pc, openai_client, config, query.query, top_k)
        timings.append(elapsed)
        relevance_scores.append(score_relevance(results, query))
        last_results = results

    return {
        "config": config.name,
        "query": query.query,
        "query_description": query.description,
        "top_k": top_k,
        "timings_s": timings,
        "mean_latency_s": statistics.mean(timings),
        "p50_latency_s": statistics.median(timings),
        "p95_latency_s": sorted(timings)[int(len(timings) * 0.95)] if len(timings) > 1 else timings[0],
        "min_latency_s": min(timings),
        "max_latency_s": max(timings),
        "relevance_score": statistics.mean(relevance_scores),
        "result_count": len(last_results),
        "top_results": last_results[:5],
    }


def run_benchmark(
    configs: list[BenchmarkConfig],
    queries: list[BenchmarkQuery],
    top_k_values: list[int],
    repetitions: int,
) -> list[dict]:
    """Run the full benchmark suite."""
    pc = Pinecone(api_key=settings.pinecone_api_key)
    needs_openai = any(not config.is_pinecone_integrated for config in configs)
    openai_client = OpenAI(api_key=settings.openai_api_key) if needs_openai else None

    all_results = []
    total = len(configs) * len(queries) * len(top_k_values)
    count = 0

    for config in configs:
        # Verify index exists
        existing = [idx.name for idx in pc.list_indexes()]
        if config.index_name not in existing:
            print(f"  SKIP {config.name}: index {config.index_name} not found")
            continue
        if config.is_hybrid and config.sparse_index_name not in existing:
            print(f"  SKIP {config.name}: sparse index {config.sparse_index_name} not found")
            continue

        print(f"\n--- {config.name} ---")

        for top_k in top_k_values:
            for query in queries:
                count += 1
                result = run_single_query(
                    pc,
                    openai_client,
                    config,
                    query,
                    top_k,
                    repetitions=repetitions,
                )
                all_results.append(result)

                print(
                    f"  [{count}/{total}] k={top_k:2d} | "
                    f"latency={result['mean_latency_s']:.3f}s | "
                    f"relevance={result['relevance_score']:.2f} | "
                    f"{query.description}"
                )

    return all_results


def save_results(results: list[dict], output_dir: Path):
    """Save benchmark results as JSON and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # JSON (full detail)
    json_path = output_dir / f"benchmark_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # CSV (summary)
    csv_path = output_dir / f"benchmark_{timestamp}.csv"
    with open(csv_path, "w") as f:
        headers = [
            "config", "top_k", "query_description",
            "mean_latency_s", "p50_latency_s", "p95_latency_s",
            "relevance_score", "result_count",
        ]
        f.write(",".join(headers) + "\n")
        for r in results:
            row = [
                r["config"],
                str(r["top_k"]),
                f'"{r["query_description"]}"',
                f"{r['mean_latency_s']:.4f}",
                f"{r['p50_latency_s']:.4f}",
                f"{r['p95_latency_s']:.4f}",
                f"{r['relevance_score']:.4f}",
                str(r["result_count"]),
            ]
            f.write(",".join(row) + "\n")
    print(f"CSV results:  {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Run LegacyLens retrieval benchmarks")
    parser.add_argument("--configs", help="Comma-separated config names (default: all)")
    parser.add_argument("--top-k", help="Comma-separated top-k values (default: 3,5,10,20,50)")
    parser.add_argument("--repetitions", type=int, default=REPETITIONS, help="Timing repetitions per query")
    args = parser.parse_args()

    if not settings.pinecone_api_key:
        print("ERROR: PINECONE_API_KEY must be set")
        sys.exit(1)

    configs = CONFIGS
    if args.configs:
        names = {n.strip() for n in args.configs.split(",")}
        configs = [c for c in CONFIGS if c.name in names]
        if not configs:
            print(f"No matching configs. Available: {', '.join(c.name for c in CONFIGS)}")
            sys.exit(1)

    top_k_values = TOP_K_VALUES
    if args.top_k:
        top_k_values = [int(k.strip()) for k in args.top_k.split(",")]

    needs_openai = any(not config.is_pinecone_integrated for config in configs)
    if needs_openai and not settings.openai_api_key:
        print("ERROR: OPENAI_API_KEY must be set for OpenAI embedding benchmark configs")
        sys.exit(1)

    print(f"Benchmark: {len(configs)} configs × {len(QUERIES)} queries × {len(top_k_values)} top-k values")
    print(f"Top-k values: {top_k_values}")
    print(f"Repetitions: {args.repetitions}")

    results = run_benchmark(configs, QUERIES, top_k_values, repetitions=args.repetitions)
    save_results(results, RESULTS_DIR)

    # Quick summary
    if results:
        by_config = {}
        for r in results:
            key = r["config"]
            if key not in by_config:
                by_config[key] = {"latencies": [], "relevances": []}
            by_config[key]["latencies"].append(r["mean_latency_s"])
            by_config[key]["relevances"].append(r["relevance_score"])

        print(f"\n{'Config':<40} {'Avg Latency':>12} {'Avg Relevance':>14}")
        print("-" * 68)
        for name, data in sorted(by_config.items()):
            avg_lat = statistics.mean(data["latencies"])
            avg_rel = statistics.mean(data["relevances"])
            print(f"{name:<40} {avg_lat:>10.3f}s {avg_rel:>13.2f}")


if __name__ == "__main__":
    main()
