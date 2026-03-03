"""Pre-compute search results for all 209 suggestion queries.

Runs each query against Pinecone (top_k=10) and saves serialized results
to web/cache/search_cache.json. This file is loaded by the web app at
startup so suggestion queries skip the vector search round-trip.

Usage:
    python scripts/warmup_cache.py
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from benchmarks.queries_suggestions import QUERIES_SUGGESTIONS
from legacylens.chain import _serialize_source
from legacylens.retriever import retrieve

CACHE_DIR = Path(__file__).resolve().parent.parent / "web" / "cache"
CACHE_FILE = CACHE_DIR / "search_cache.json"
TOP_K = 10


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    queries = [q.query for q in QUERIES_SUGGESTIONS]
    print(f"Warming up search cache for {len(queries)} queries (top_k={TOP_K})...")

    cache = {}
    t0 = time.time()

    for i, q in enumerate(queries, 1):
        results = retrieve(q, top_k=TOP_K)
        cache[q] = [_serialize_source(r) for r in results]
        elapsed = time.time() - t0
        rate = elapsed / i
        remaining = rate * (len(queries) - i)
        print(f"  [{i}/{len(queries)}] {elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining | {q[:60]}")

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, separators=(",", ":"))

    size_mb = os.path.getsize(CACHE_FILE) / 1024 / 1024
    print(f"\nDone in {time.time() - t0:.0f}s. Cache: {CACHE_FILE} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
