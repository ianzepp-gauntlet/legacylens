"""Validation tests for LegacyLens retrieval quality.

These tests require a populated Pinecone index.
Run after ingestion: python scripts/ingest_carddemo.py
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()


needs_api_keys = pytest.mark.skipif(
    (
        os.environ.get("LEGACYLENS_RUN_LIVE_TESTS", "0") != "1"
        or not os.environ.get("OPENAI_API_KEY")
        or not os.environ.get("PINECONE_API_KEY")
    ),
    reason="Live retrieval tests disabled (set LEGACYLENS_RUN_LIVE_TESTS=1 with API keys)",
)


def _file_names(results):
    return [r.file_name for r in results]


def _chunk_names(results):
    return [r.name for r in results]


@needs_api_keys
class TestRetrieval:
    """Test that retrieval returns relevant chunks for known queries."""

    def test_main_entry_point(self):
        from legacylens.retriever import retrieve

        results = retrieve("Where is the main entry point of the CardDemo application?")
        files = _file_names(results)
        # Should find COMEN01C (main menu) or similar entry point
        assert any("COMEN01" in f or "COSGN00" in f for f in files), \
            f"Expected menu/sign-on program in results, got: {files}"

    def test_credit_card_update(self):
        from legacylens.retriever import retrieve

        results = retrieve("What does the COCRDUPC program do?")
        files = _file_names(results)
        assert any("COCRDUPC" in f for f in files), \
            f"Expected COCRDUPC in results, got: {files}"

    def test_file_io_operations(self):
        from legacylens.retriever import retrieve

        results = retrieve("Find all file I/O operations and VSAM file handling")
        # Should find batch programs that do file I/O
        files = _file_names(results)
        assert len(results) > 0, "Expected at least some results for file I/O query"

    def test_dependencies_of_cocrdupc(self):
        from legacylens.retriever import retrieve

        results = retrieve("What are the dependencies and COPY references of COCRDUPC?")
        files = _file_names(results)
        assert any("COCRDUPC" in f for f in files), \
            f"Expected COCRDUPC in results, got: {files}"

    def test_customer_record(self):
        from legacylens.retriever import retrieve

        results = retrieve("What functions modify the customer record?")
        # Should find customer-related programs or copybooks
        files = _file_names(results)
        assert any("CUS" in f.upper() for f in files), \
            f"Expected customer-related file in results, got: {files}"

    def test_credit_card_validation(self):
        from legacylens.retriever import retrieve

        results = retrieve("How are credit cards validated?")
        names = _chunk_names(results)
        # Should find edit paragraphs
        assert any("EDIT" in n.upper() for n in names), \
            f"Expected edit paragraph in results, got: {names}"


class TestChunking:
    """Test that the parser and chunker work correctly on actual files."""

    @pytest.fixture
    def carddemo_path(self):
        path = os.environ.get("CARDDEMO_PATH", "")
        if not path or not Path(path).is_dir():
            pytest.skip("CARDDEMO_PATH not set")
        return path

    def test_parse_cocrdupc(self, carddemo_path):
        from legacylens.parser import parse_cobol_file

        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        assert parsed.program_id == "COCRDUPC"
        assert len(parsed.divisions) >= 3
        assert len(parsed.paragraphs) > 10
        assert len(parsed.copy_references) > 3

    def test_parse_batch_program(self, carddemo_path):
        from legacylens.parser import parse_cobol_file

        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "CBACT01C.cbl"))
        assert parsed.program_id == "CBACT01C"
        assert parsed.has_sequence_numbers is True

    def test_chunk_cobol(self, carddemo_path):
        from legacylens.chunker import chunk_file

        chunks = chunk_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        assert len(chunks) > 5
        chunk_types = {c.chunk_type for c in chunks}
        assert "header" in chunk_types
        assert "paragraph" in chunk_types

    def test_chunk_copybook(self, carddemo_path):
        from legacylens.chunker import chunk_file

        chunks = chunk_file(os.path.join(carddemo_path, "cpy", "COCOM01Y.cpy"))
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "copybook"

    def test_chunk_bms(self, carddemo_path):
        from legacylens.chunker import chunk_file

        chunks = chunk_file(os.path.join(carddemo_path, "bms", "COCRDUP.bms"))
        assert len(chunks) >= 1

    def test_chunk_jcl(self, carddemo_path):
        from legacylens.chunker import chunk_file

        chunks = chunk_file(os.path.join(carddemo_path, "jcl", "ACCTFILE.jcl"))
        assert len(chunks) >= 1

    def test_all_files_parseable(self, carddemo_path):
        from legacylens.ingest import discover_files
        from legacylens.chunker import chunk_file

        files = discover_files(carddemo_path)
        errors = []
        total_chunks = 0
        for f in files:
            try:
                chunks = chunk_file(f)
                total_chunks += len(chunks)
            except Exception as e:
                errors.append((f, str(e)))

        assert not errors, f"Failed to parse {len(errors)} files: {errors}"
        assert total_chunks > 100, f"Expected >100 chunks, got {total_chunks}"
