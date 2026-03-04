"""Tests for dependency-injected seams added for easier unit testing."""

from legacylens.ingest import IngestDependencies, ingest_codebase
from legacylens.models import CodeChunk
from legacylens.retriever import RetrieverDependencies, retrieve


def _chunk_for(path: str) -> CodeChunk:
    return CodeChunk(
        content="MOVE A TO B.",
        file_path=path,
        file_name="FOO.cbl",
        file_type="cbl",
        chunk_type="paragraph",
        name="1000-MAIN",
        start_line=10,
        end_line=20,
        preamble="File: FOO.cbl",
    )


class TestRetrieverDependencies:
    def test_pinecone_provider_uses_search_records_dependency(self):
        calls = {"search": 0, "query": 0}

        def search_records_fn(*_args, **_kwargs):
            calls["search"] += 1
            return [{
                "score": 0.9,
                "metadata": {
                    "content": "x",
                    "file_path": "/tmp/FOO.cbl",
                    "file_name": "FOO.cbl",
                    "file_type": "cbl",
                    "chunk_type": "paragraph",
                    "name": "1000-MAIN",
                    "start_line": 1,
                    "end_line": 2,
                },
            }]

        def query_vectors_fn(*_args, **_kwargs):
            calls["query"] += 1
            return []

        deps = RetrieverDependencies(
            search_records_fn=search_records_fn,
            query_vectors_fn=query_vectors_fn,
            get_query_embedding_fn=lambda _q: [0.1, 0.2],
        )
        results = retrieve("entry point", embedding_provider="pinecone", deps=deps)

        assert calls["search"] == 1
        assert calls["query"] == 0
        assert len(results) == 1
        assert results[0].file_name == "FOO.cbl"

    def test_openai_provider_uses_embedding_and_query_dependencies(self):
        calls = {"embed": 0, "query": 0}

        def query_vectors_fn(embedding, *_args, **_kwargs):
            calls["query"] += 1
            assert embedding == [0.42]
            return [{
                "score": 0.8,
                "metadata": {
                    "content": "y",
                    "file_path": "/tmp/BAR.cbl",
                    "file_name": "BAR.cbl",
                    "file_type": "cbl",
                    "chunk_type": "paragraph",
                    "name": "2000-WORK",
                    "start_line": 5,
                    "end_line": 9,
                },
            }]

        deps = RetrieverDependencies(
            search_records_fn=lambda *_args, **_kwargs: [],
            query_vectors_fn=query_vectors_fn,
            get_query_embedding_fn=lambda _q: calls.__setitem__("embed", calls["embed"] + 1) or [0.42],
        )
        results = retrieve("work", embedding_provider="openai", deps=deps)

        assert calls["embed"] == 1
        assert calls["query"] == 1
        assert results[0].file_name == "BAR.cbl"


class TestIngestDependencies:
    def test_pinecone_provider_uses_record_upsert_dependency(self, tmp_path):
        (tmp_path / "a.cbl").write_text("IDENTIFICATION DIVISION.")
        calls = {"chunk": 0, "record_upsert": 0, "chunk_upsert": 0, "embed": 0}
        report_lines = []

        def chunk_file_fn(path):
            calls["chunk"] += 1
            return [_chunk_for(path)]

        def upsert_records_fn(chunks, texts):
            calls["record_upsert"] += 1
            assert len(chunks) == 1
            assert len(texts) == 1
            return len(chunks)

        deps = IngestDependencies(
            chunk_file_fn=chunk_file_fn,
            upsert_records_fn=upsert_records_fn,
            upsert_chunks_fn=lambda *_args, **_kwargs: calls.__setitem__("chunk_upsert", calls["chunk_upsert"] + 1) or 0,
            get_embeddings_fn=lambda *_args, **_kwargs: calls.__setitem__("embed", calls["embed"] + 1) or [],
        )

        result = ingest_codebase(
            str(tmp_path),
            deps=deps,
            reporter=report_lines.append,
            embedding_provider="pinecone",
            pinecone_model="llama-text-embed-v2",
        )

        assert result["files"] == 1
        assert result["chunks"] == 1
        assert result["vectors"] == 1
        assert calls["chunk"] == 1
        assert calls["record_upsert"] == 1
        assert calls["chunk_upsert"] == 0
        assert calls["embed"] == 0
        assert any("Upserting to Pinecone" in line for line in report_lines)

    def test_openai_provider_uses_embedding_and_vector_upsert_dependencies(self, tmp_path):
        (tmp_path / "b.cbl").write_text("IDENTIFICATION DIVISION.")
        calls = {"embed": 0, "chunk_upsert": 0}

        def get_embeddings_fn(texts):
            calls["embed"] += 1
            assert len(texts) == 1
            return [[0.1, 0.2, 0.3]]

        def upsert_chunks_fn(chunks, embeddings):
            calls["chunk_upsert"] += 1
            assert len(chunks) == 1
            assert len(embeddings) == 1
            return 1

        deps = IngestDependencies(
            chunk_file_fn=lambda path: [_chunk_for(path)],
            upsert_records_fn=lambda *_args, **_kwargs: 0,
            upsert_chunks_fn=upsert_chunks_fn,
            get_embeddings_fn=get_embeddings_fn,
        )

        result = ingest_codebase(
            str(tmp_path),
            deps=deps,
            embedding_provider="openai",
            verbose=False,
        )

        assert result["vectors"] == 1
        assert calls["embed"] == 1
        assert calls["chunk_upsert"] == 1
