"""Unit tests for vectorstore operational paths with fake Pinecone index."""

from types import SimpleNamespace

import legacylens.vectorstore as vectorstore_mod
from legacylens.models import CodeChunk


def _chunk(**overrides):
    data = dict(
        content="MOVE A TO B.",
        file_path="/tmp/FOO.cbl",
        file_name="FOO.cbl",
        file_type="cbl",
        chunk_type="paragraph",
        name="1000-MAIN",
        start_line=1,
        end_line=9,
        preamble="File: FOO.cbl",
        comments="comment",
        copy_references=["COPY1"],
        calls_to=["PARA2"],
    )
    data.update(overrides)
    return CodeChunk(**data)


class _FakeIndex:
    def __init__(self):
        self.upsert_calls = []
        self.upsert_records_calls = []
        self.query_calls = []
        self.search_calls = []
        self.delete_calls = []

    def upsert(self, *, vectors, namespace):
        self.upsert_calls.append((vectors, namespace))

    def upsert_records(self, namespace, records):
        self.upsert_records_calls.append((namespace, records))

    def query(self, **kwargs):
        self.query_calls.append(kwargs)
        match = SimpleNamespace(id="id1", score=0.77, metadata={"content": "x"})
        return SimpleNamespace(matches=[match])

    def search_records(self, **kwargs):
        self.search_calls.append(kwargs)
        class Hit(dict):
            @property
            def fields(self):
                return {"content": "y"}

            @property
            def id(self):
                return "id2"

            @property
            def score(self):
                return 0.88

        return SimpleNamespace(result=SimpleNamespace(hits=[Hit(_id="id2", _score=0.88)]))

    def delete(self, **kwargs):
        self.delete_calls.append(kwargs)


class TestVectorstoreOperations:
    def test_upsert_chunks_builds_vectors(self):
        idx = _FakeIndex()
        cfg = SimpleNamespace(pinecone_namespace="ns")
        total = vectorstore_mod.upsert_chunks(
            [_chunk()],
            [[0.1, 0.2]],
            index=idx,
            settings_obj=cfg,
            batch_size=1,
        )
        assert total == 1
        vectors, ns = idx.upsert_calls[0]
        assert ns == "ns"
        assert vectors[0]["metadata"]["file_name"] == "FOO.cbl"

    def test_upsert_records_builds_records(self):
        idx = _FakeIndex()
        cfg = SimpleNamespace(pinecone_namespace="ns")
        total = vectorstore_mod.upsert_records(
            [_chunk()],
            ["embed text"],
            index=idx,
            settings_obj=cfg,
            batch_size=1,
        )
        assert total == 1
        ns, records = idx.upsert_records_calls[0]
        assert ns == "ns"
        assert records[0]["chunk_text"] == "embed text"
        assert records[0]["_id"]

    def test_query_vectors_uses_filter_and_top_k(self):
        idx = _FakeIndex()
        cfg = SimpleNamespace(top_k=5, pinecone_namespace="ns")
        out = vectorstore_mod.query_vectors(
            [0.1],
            file_type_filter="cbl",
            metadata_filters={"name": "MAIN"},
            index=idx,
            settings_obj=cfg,
        )
        assert out[0]["id"] == "id1"
        call = idx.query_calls[0]
        assert call["top_k"] == 5
        assert call["filter"]["file_type"]["$eq"] == "cbl"

    def test_search_records_uses_search_query(self):
        idx = _FakeIndex()
        cfg = SimpleNamespace(top_k=7, pinecone_namespace="ns")
        out = vectorstore_mod.search_records(
            "find main",
            index=idx,
            settings_obj=cfg,
            file_type_filter="cbl",
        )
        assert out[0]["id"] == "id2"
        call = idx.search_calls[0]
        assert call["namespace"] == "ns"

    def test_delete_namespace_ignores_not_found_errors(self):
        cfg = SimpleNamespace(pinecone_namespace="ns")

        class MissingIndex(_FakeIndex):
            def delete(self, **_kwargs):
                err = Exception("404 not found")
                raise err

        vectorstore_mod.delete_namespace(index=MissingIndex(), settings_obj=cfg)

    def test_delete_namespace_raises_other_errors(self):
        cfg = SimpleNamespace(pinecone_namespace="ns")

        class BadIndex(_FakeIndex):
            def delete(self, **_kwargs):
                raise RuntimeError("boom")

        try:
            vectorstore_mod.delete_namespace(index=BadIndex(), settings_obj=cfg)
            assert False, "expected exception"
        except RuntimeError as exc:
            assert "boom" in str(exc)
