"""Analyze benchmark results and produce summary reports.

Usage:
    python benchmarks/report.py                              # latest results
    python benchmarks/report.py benchmarks/results/file.json # specific file
"""

import json
import statistics
import sys
from pathlib import Path


RESULTS_DIR = Path(__file__).resolve().parent / "results"


def load_results(path: Path | None = None) -> list[dict]:
    if path:
        with open(path) as f:
            return json.load(f)

    json_files = sorted(RESULTS_DIR.glob("benchmark_*.json"))
    if not json_files:
        print("No benchmark results found in benchmarks/results/")
        sys.exit(1)

    latest = json_files[-1]
    print(f"Loading: {latest}\n")
    with open(latest) as f:
        return json.load(f)


def aggregate_by_config(results: list[dict]) -> dict:
    """Aggregate results by config name."""
    by_config = {}
    for r in results:
        key = r["config"]
        if key not in by_config:
            by_config[key] = {"latencies": [], "relevances": [], "by_top_k": {}}
        by_config[key]["latencies"].append(r["mean_latency_s"])
        by_config[key]["relevances"].append(r["relevance_score"])

        k = r["top_k"]
        if k not in by_config[key]["by_top_k"]:
            by_config[key]["by_top_k"][k] = {"latencies": [], "relevances": []}
        by_config[key]["by_top_k"][k]["latencies"].append(r["mean_latency_s"])
        by_config[key]["by_top_k"][k]["relevances"].append(r["relevance_score"])

    return by_config


def print_summary_table(by_config: dict):
    """Print overall summary table."""
    print("=" * 80)
    print("OVERALL SUMMARY (averaged across all queries and top-k values)")
    print("=" * 80)
    print(f"{'Config':<40} {'Avg Latency':>12} {'P95 Latency':>12} {'Avg Relevance':>14}")
    print("-" * 80)

    rows = []
    for name, data in by_config.items():
        avg_lat = statistics.mean(data["latencies"])
        p95_lat = sorted(data["latencies"])[int(len(data["latencies"]) * 0.95)]
        avg_rel = statistics.mean(data["relevances"])
        rows.append((name, avg_lat, p95_lat, avg_rel))

    # Sort by relevance desc, then latency asc
    for name, avg_lat, p95_lat, avg_rel in sorted(rows, key=lambda x: (-x[3], x[1])):
        print(f"{name:<40} {avg_lat:>10.3f}s {p95_lat:>10.3f}s {avg_rel:>13.2%}")


def print_top_k_breakdown(by_config: dict):
    """Print breakdown by top-k value."""
    # Collect all top-k values
    all_k = set()
    for data in by_config.values():
        all_k.update(data["by_top_k"].keys())
    all_k = sorted(all_k)

    for k in all_k:
        print(f"\n{'='*80}")
        print(f"TOP-K = {k}")
        print(f"{'='*80}")
        print(f"{'Config':<40} {'Avg Latency':>12} {'Avg Relevance':>14}")
        print("-" * 68)

        rows = []
        for name, data in by_config.items():
            if k in data["by_top_k"]:
                kd = data["by_top_k"][k]
                avg_lat = statistics.mean(kd["latencies"])
                avg_rel = statistics.mean(kd["relevances"])
                rows.append((name, avg_lat, avg_rel))

        for name, avg_lat, avg_rel in sorted(rows, key=lambda x: (-x[2], x[1])):
            print(f"{name:<40} {avg_lat:>10.3f}s {avg_rel:>13.2%}")


def print_model_comparison(by_config: dict):
    """Compare models across dimensions."""
    print(f"\n{'='*80}")
    print("MODEL COMPARISON (averaged across chunking strategies)")
    print(f"{'='*80}")

    # Group by model prefix
    model_groups = {}
    for name, data in by_config.items():
        parts = name.split("-")
        model = parts[0]  # small, large, e5, llama
        dims = parts[1]
        chunking = parts[2]

        key = f"{model}-{dims}"
        if key not in model_groups:
            model_groups[key] = {"latencies": [], "relevances": []}
        model_groups[key]["latencies"].extend(data["latencies"])
        model_groups[key]["relevances"].extend(data["relevances"])

    print(f"{'Model-Dims':<25} {'Avg Latency':>12} {'Avg Relevance':>14}")
    print("-" * 53)

    rows = []
    for key, data in model_groups.items():
        avg_lat = statistics.mean(data["latencies"])
        avg_rel = statistics.mean(data["relevances"])
        rows.append((key, avg_lat, avg_rel))

    for key, avg_lat, avg_rel in sorted(rows, key=lambda x: (-x[2], x[1])):
        print(f"{key:<25} {avg_lat:>10.3f}s {avg_rel:>13.2%}")


def print_chunking_comparison(by_config: dict):
    """Compare paragraph vs fixed chunking."""
    print(f"\n{'='*80}")
    print("CHUNKING STRATEGY COMPARISON")
    print(f"{'='*80}")

    chunking_groups = {"paragraph": {"latencies": [], "relevances": []}, "fixed": {"latencies": [], "relevances": []}}
    for name, data in by_config.items():
        chunking = name.split("-")[-1]
        if chunking in chunking_groups:
            chunking_groups[chunking]["latencies"].extend(data["latencies"])
            chunking_groups[chunking]["relevances"].extend(data["relevances"])

    print(f"{'Strategy':<15} {'Avg Latency':>12} {'Avg Relevance':>14}")
    print("-" * 43)
    for strategy, data in chunking_groups.items():
        if data["latencies"]:
            avg_lat = statistics.mean(data["latencies"])
            avg_rel = statistics.mean(data["relevances"])
            print(f"{strategy:<15} {avg_lat:>10.3f}s {avg_rel:>13.2%}")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    results = load_results(path)
    print(f"Loaded {len(results)} result entries\n")

    by_config = aggregate_by_config(results)

    print_summary_table(by_config)
    print_top_k_breakdown(by_config)
    print_model_comparison(by_config)
    print_chunking_comparison(by_config)


if __name__ == "__main__":
    main()
