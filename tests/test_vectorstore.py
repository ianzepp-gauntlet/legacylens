"""Unit tests for vectorstore and models."""

import hashlib

from legacylens.models import CodeChunk, QueryResult
from legacylens.vectorstore import METADATA_CONTENT_LIMIT, make_vector_id


class TestMakeVectorId:
    def _chunk(self, **overrides):
        defaults = dict(
            content="x",
            file_path="/a/b/FOO.cbl",
            file_name="FOO.cbl",
            file_type="cbl",
            chunk_type="paragraph",
            name="MAIN",
            start_line=10,
            end_line=20,
        )
        defaults.update(overrides)
        return CodeChunk(**defaults)

    def test_format(self):
        c = self._chunk()
        vid = make_vector_id(c)
        assert vid.startswith("FOO.cbl:")
        assert vid.endswith(":10-20")

    def test_deterministic(self):
        c = self._chunk()
        assert make_vector_id(c) == make_vector_id(c)

    def test_different_paths_different_ids(self):
        c1 = self._chunk(file_path="/a/FOO.cbl")
        c2 = self._chunk(file_path="/b/FOO.cbl")
        assert make_vector_id(c1) != make_vector_id(c2)

    def test_different_lines_different_ids(self):
        c1 = self._chunk(start_line=10, end_line=20)
        c2 = self._chunk(start_line=30, end_line=40)
        assert make_vector_id(c1) != make_vector_id(c2)

    def test_same_file_same_lines_same_id(self):
        c1 = self._chunk()
        c2 = self._chunk()
        assert make_vector_id(c1) == make_vector_id(c2)


class TestCodeChunkDefaults:
    def test_defaults(self):
        c = CodeChunk(
            content="x", file_path="p", file_name="f",
            file_type="cbl", chunk_type="header", name="n",
            start_line=1, end_line=2,
        )
        assert c.preamble == ""
        assert c.parent_program == ""
        assert c.comments == ""
        assert c.copy_references == []
        assert c.calls_to == []

    def test_lists_are_independent(self):
        c1 = CodeChunk(
            content="x", file_path="p", file_name="f",
            file_type="cbl", chunk_type="header", name="n",
            start_line=1, end_line=2,
        )
        c2 = CodeChunk(
            content="x", file_path="p", file_name="f",
            file_type="cbl", chunk_type="header", name="n",
            start_line=1, end_line=2,
        )
        c1.copy_references.append("FOO")
        assert c2.copy_references == []


class TestQueryResultDefaults:
    def test_defaults(self):
        r = QueryResult(
            content="x", file_path="p", file_name="f",
            file_type="cbl", chunk_type="header", name="n",
            start_line=1, end_line=2, score=0.9,
        )
        assert r.preamble == ""
        assert r.comments == ""
        assert r.copy_references == []
        assert r.calls_to == []


class TestMetadataContentLimit:
    def test_limit_is_reasonable(self):
        assert METADATA_CONTENT_LIMIT == 10000
        assert METADATA_CONTENT_LIMIT < 40000  # Pinecone 40KB limit
