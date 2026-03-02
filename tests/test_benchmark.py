"""Unit tests for benchmark infrastructure (no API keys needed)."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.config import (
    CONFIGS,
    QUERIES,
    TOP_K_VALUES,
    BenchmarkConfig,
    BenchmarkQuery,
    score_relevance,
)


class TestBenchmarkConfigs:
    def test_configs_not_empty(self):
        assert len(CONFIGS) > 0

    def test_all_configs_have_unique_names(self):
        names = [c.name for c in CONFIGS]
        assert len(names) == len(set(names)), f"Duplicate config names: {[n for n in names if names.count(n) > 1]}"

    def test_all_configs_have_unique_index_names(self):
        index_names = [c.index_name for c in CONFIGS]
        assert len(index_names) == len(set(index_names))

    def test_openai_configs_have_correct_provider(self):
        for c in CONFIGS:
            if c.embedding_model.startswith("text-embedding"):
                assert c.embedding_provider == "openai"
                assert not c.is_pinecone_integrated

    def test_pinecone_configs_have_correct_provider(self):
        for c in CONFIGS:
            if c.embedding_provider == "pinecone":
                assert c.is_pinecone_integrated
                assert c.pinecone_model is not None

    def test_index_names_are_valid(self):
        for c in CONFIGS:
            assert len(c.index_name) <= 45, f"Index name too long: {c.index_name}"
            assert c.index_name.replace("-", "").isalnum(), f"Invalid chars in: {c.index_name}"

    def test_chunking_strategies(self):
        strategies = {c.chunking_strategy for c in CONFIGS}
        assert "paragraph" in strategies
        assert "fixed" in strategies

    def test_expected_config_count(self):
        # small: 4 dims × 2 chunking = 8
        # large: 5 dims × 2 chunking = 10
        # e5: 1 dim × 2 chunking = 2
        # llama: 1 dim × 2 chunking = 2
        assert len(CONFIGS) == 22


class TestBenchmarkQueries:
    def test_queries_not_empty(self):
        assert len(QUERIES) >= 10

    def test_all_queries_have_descriptions(self):
        for q in QUERIES:
            assert q.description, f"Missing description for: {q.query[:40]}"

    def test_all_queries_have_expected_patterns(self):
        for q in QUERIES:
            assert q.expected_files or q.expected_chunks, \
                f"No expected patterns for: {q.query[:40]}"


class TestRelevanceScoring:
    def test_perfect_score(self):
        query = BenchmarkQuery(
            query="test",
            expected_files=["FOO", "BAR"],
            expected_chunks=[],
        )
        results = [
            {"file_name": "FOO.cbl", "name": "MAIN"},
            {"file_name": "BAR.cbl", "name": "INIT"},
        ]
        assert score_relevance(results, query) == 1.0

    def test_zero_score(self):
        query = BenchmarkQuery(
            query="test",
            expected_files=["FOO", "BAR"],
            expected_chunks=[],
        )
        results = [
            {"file_name": "COMPLETELY_DIFFERENT.cbl", "name": "NOPE"},
        ]
        assert score_relevance(results, query) == 0.0

    def test_partial_score(self):
        query = BenchmarkQuery(
            query="test",
            expected_files=["FOO", "BAR"],
            expected_chunks=[],
        )
        results = [
            {"file_name": "FOO.cbl", "name": "MAIN"},
            {"file_name": "OTHER.cbl", "name": "INIT"},
        ]
        assert score_relevance(results, query) == 0.5

    def test_chunk_name_matching(self):
        query = BenchmarkQuery(
            query="test",
            expected_files=[],
            expected_chunks=["EDIT", "VALID"],
        )
        results = [
            {"file_name": "X.cbl", "name": "EDIT-RECORD"},
            {"file_name": "Y.cbl", "name": "VALIDATE-INPUT"},
        ]
        assert score_relevance(results, query) == 1.0

    def test_empty_results(self):
        query = BenchmarkQuery(
            query="test",
            expected_files=["FOO"],
            expected_chunks=[],
        )
        assert score_relevance([], query) == 0.0

    def test_no_expectations(self):
        query = BenchmarkQuery(query="test", expected_files=[], expected_chunks=[])
        assert score_relevance([{"file_name": "A.cbl", "name": "B"}], query) == 1.0
        assert score_relevance([], query) == 0.0


class TestFixedChunker:
    def test_fixed_chunking_produces_chunks(self):
        from legacylens.chunker import chunk_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cbl", delete=False) as f:
            # Write ~100 lines of fake COBOL
            for i in range(100):
                f.write(f"       DISPLAY 'LINE {i:04d}'.\n")
            f.flush()

            chunks = chunk_file(f.name, strategy="fixed")
            assert len(chunks) >= 1
            assert all(c.chunk_type == "fixed" for c in chunks)
            os.unlink(f.name)

    def test_fixed_chunking_small_file(self):
        from legacylens.chunker import chunk_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpy", delete=False) as f:
            f.write("       01 RECORD-AREA.\n           05 FIELD-A PIC X(10).\n")
            f.flush()

            chunks = chunk_file(f.name, strategy="fixed")
            assert len(chunks) == 1
            os.unlink(f.name)

    def test_fixed_chunking_empty_file(self):
        from legacylens.chunker import chunk_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cbl", delete=False) as f:
            f.write("")
            f.flush()

            chunks = chunk_file(f.name, strategy="fixed")
            assert len(chunks) == 0
            os.unlink(f.name)

    def test_fixed_chunking_has_overlap(self):
        from legacylens.chunker import chunk_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cbl", delete=False) as f:
            # Write enough lines to guarantee multiple chunks
            for i in range(1000):
                f.write(f"       DISPLAY 'THIS IS A REASONABLY LONG LINE NUMBER {i:04d} WITH SOME CONTENT'.\n")
            f.flush()

            chunks = chunk_file(f.name, strategy="fixed")
            assert len(chunks) > 1, "Expected multiple chunks for large file"

            # Check overlap: last lines of chunk N should appear in chunk N+1
            if len(chunks) >= 2:
                c1_lines = set(chunks[0].content.splitlines()[-10:])
                c2_lines = set(chunks[1].content.splitlines()[:10])
                overlap = c1_lines & c2_lines
                assert len(overlap) > 0, "Expected overlap between consecutive chunks"

            os.unlink(f.name)

    def test_paragraph_strategy_still_works(self):
        from legacylens.chunker import chunk_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpy", delete=False) as f:
            f.write("       01 TEST-REC.\n           05 FIELD PIC X(10).\n")
            f.flush()

            chunks = chunk_file(f.name, strategy="paragraph")
            assert len(chunks) == 1
            assert chunks[0].chunk_type == "copybook"
            os.unlink(f.name)


class TestTopKValues:
    def test_top_k_values_defined(self):
        assert TOP_K_VALUES == [3, 5, 10, 20, 50]
