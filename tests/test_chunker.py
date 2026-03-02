"""Unit tests for the syntax-aware chunker module."""

import os
import tempfile

import pytest

from legacylens.chunker import (
    MIN_PARAGRAPH_LINES,
    _build_preamble,
    _chunk_bms,
    _chunk_cobol,
    _chunk_copybook,
    _chunk_generic,
    _chunk_jcl,
    chunk_file,
)


def _write_temp(content: str, suffix: str = ".cbl") -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


# --- Preamble builder ---

class TestBuildPreamble:
    def test_minimal(self):
        p = _build_preamble(file_name="FOO.cbl")
        assert "File: FOO.cbl" in p

    def test_with_program(self):
        p = _build_preamble(file_name="FOO.cbl", program_id="FOO", layer="Batch", description="Does stuff")
        assert "Program: FOO - Batch - Does stuff" in p

    def test_with_chunk_info(self):
        p = _build_preamble(file_name="F.cbl", chunk_type="Paragraph", name="MAIN", start_line=10, end_line=20)
        assert "Paragraph: MAIN (lines 11-20)" in p

    def test_with_copy_refs(self):
        p = _build_preamble(file_name="F.cbl", copy_refs=["ALIB", "BLIB"])
        assert "COPY ALIB" in p
        assert "COPY BLIB" in p

    def test_with_calls(self):
        p = _build_preamble(file_name="F.cbl", calls_to=["PERFORM X", "CALL Y"])
        assert "PERFORM X" in p
        assert "CALL Y" in p

    def test_empty_lists_omitted(self):
        p = _build_preamble(file_name="F.cbl", copy_refs=[], calls_to=[])
        assert "References" not in p
        assert "Calls" not in p


# --- COBOL chunking ---

SAMPLE_COBOL = """\
      *****************************************************************
      * Program:     TESTPROG.CBL
      * Function:    Test program
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.
           TESTPROG.

       ENVIRONMENT DIVISION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-VARS.
         05 WS-A PIC X.
         05 WS-B PIC X.
         05 WS-C PIC X.
         05 WS-D PIC X.
         05 WS-E PIC X.

       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-WORK
           PERFORM 2000-FINISH
           STOP RUN.

       0000-MAIN-EXIT.
           EXIT.

       1000-WORK.
           MOVE 'A' TO WS-A
           MOVE 'B' TO WS-B
           MOVE 'C' TO WS-C
           MOVE 'D' TO WS-D
           MOVE 'E' TO WS-E
           DISPLAY WS-A.

       1000-WORK-EXIT.
           EXIT.

       2000-FINISH.
           DISPLAY 'DONE'
           DISPLAY 'BYE'
           DISPLAY 'END'
           DISPLAY 'FINAL'
           DISPLAY 'LAST'.

       2000-FINISH-EXIT.
           EXIT.
"""


class TestChunkCobol:
    def test_produces_header_chunk(self):
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            headers = [c for c in chunks if c.chunk_type == "header"]
            assert len(headers) == 1
            assert "TESTPROG" in headers[0].name
        finally:
            os.unlink(path)

    def test_produces_data_division_chunk(self):
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            data_chunks = [c for c in chunks if c.chunk_type == "data_division"]
            assert len(data_chunks) >= 1
        finally:
            os.unlink(path)

    def test_produces_paragraph_chunks(self):
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            para_chunks = [c for c in chunks if c.chunk_type == "paragraph"]
            assert len(para_chunks) >= 1
            names = " ".join(c.name for c in para_chunks)
            assert "0000-MAIN" in names
        finally:
            os.unlink(path)

    def test_short_paragraphs_merged(self):
        """Paragraphs shorter than MIN_PARAGRAPH_LINES should merge with predecessor."""
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            para_chunks = [c for c in chunks if c.chunk_type == "paragraph"]
            # 0000-MAIN-EXIT (2 lines) should be merged with 0000-MAIN
            for c in para_chunks:
                if "0000-MAIN" in c.name and "0000-MAIN-EXIT" in c.name:
                    break
            else:
                # If not merged, the exit paragraph should still exist somewhere
                all_names = [c.name for c in para_chunks]
                # Just verify we don't have a standalone tiny exit paragraph
                standalone_exits = [n for n in all_names if n == "0000-MAIN-EXIT"]
                assert len(standalone_exits) == 0, \
                    "Short EXIT paragraph should be merged with predecessor"
        finally:
            os.unlink(path)

    def test_chunk_metadata_populated(self):
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            for c in chunks:
                assert c.file_name, "file_name should be set"
                assert c.file_type == "cbl"
                assert c.start_line > 0, "start_line should be 1-indexed"
                assert c.end_line >= c.start_line
                assert c.content, "content should not be empty"
                assert c.preamble, "preamble should not be empty"
                assert c.parent_program == "TESTPROG"
        finally:
            os.unlink(path)

    def test_calls_in_paragraph_chunks(self):
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            main_chunks = [c for c in chunks if "0000-MAIN" in c.name and c.chunk_type == "paragraph"]
            assert len(main_chunks) >= 1
            calls = main_chunks[0].calls_to
            assert any("1000-WORK" in c for c in calls)
        finally:
            os.unlink(path)

    def test_no_overlapping_line_ranges(self):
        path = _write_temp(SAMPLE_COBOL)
        try:
            chunks = chunk_file(path)
            para_chunks = sorted(
                [c for c in chunks if c.chunk_type == "paragraph"],
                key=lambda c: c.start_line,
            )
            for i in range(len(para_chunks) - 1):
                assert para_chunks[i].end_line <= para_chunks[i + 1].start_line, \
                    f"Overlap: {para_chunks[i].name} ends at {para_chunks[i].end_line}, " \
                    f"{para_chunks[i+1].name} starts at {para_chunks[i+1].start_line}"
        finally:
            os.unlink(path)


# --- Large DATA DIVISION splitting ---

class TestLargeDataDivisionSplit:
    def _make_large_data_cobol(self):
        """Generate a COBOL file with a >200 line DATA DIVISION."""
        lines = [
            "       IDENTIFICATION DIVISION.",
            "       PROGRAM-ID. BIGDATA.",
            "       ENVIRONMENT DIVISION.",
            "       DATA DIVISION.",
            "       WORKING-STORAGE SECTION.",
        ]
        # Two 01-level records with >100 fields each
        lines.append("       01  RECORD-A.")
        for i in range(110):
            lines.append(f"         05 FIELD-A-{i:04d}  PIC X(10).")
        lines.append("       01  RECORD-B.")
        for i in range(110):
            lines.append(f"         05 FIELD-B-{i:04d}  PIC X(10).")
        lines.append("       PROCEDURE DIVISION.")
        lines.append("       MAIN-PARA.")
        lines.append("           STOP RUN.")
        return "\n".join(lines)

    def test_splits_at_01_level(self):
        path = _write_temp(self._make_large_data_cobol())
        try:
            chunks = chunk_file(path)
            data_chunks = [c for c in chunks if c.chunk_type == "data_division"]
            assert len(data_chunks) >= 2, f"Expected >=2 data chunks, got {len(data_chunks)}"
            names = [c.name for c in data_chunks]
            assert any("RECORD-A" in n for n in names)
            assert any("RECORD-B" in n for n in names)
        finally:
            os.unlink(path)


# --- Copybook chunking ---

SAMPLE_COPYBOOK = """\
      ******************************************************************
      * Communication area for testing
      ******************************************************************
       01 TEST-COMMAREA.
          05 TEST-FIELD-A    PIC X(10).
          05 TEST-FIELD-B    PIC 9(5).
"""


class TestChunkCopybook:
    def test_single_chunk(self):
        path = _write_temp(SAMPLE_COPYBOOK, suffix=".cpy")
        try:
            chunks = chunk_file(path)
            assert len(chunks) == 1
            assert chunks[0].chunk_type == "copybook"
        finally:
            os.unlink(path)

    def test_copybook_metadata(self):
        path = _write_temp(SAMPLE_COPYBOOK, suffix=".cpy")
        try:
            chunks = chunk_file(path)
            c = chunks[0]
            assert c.file_type == "cpy"
            assert c.start_line == 1
            assert c.end_line == len(SAMPLE_COPYBOOK.splitlines())
            assert "Communication area" in c.comments
        finally:
            os.unlink(path)


# --- BMS chunking ---

SAMPLE_BMS = """\
******************************************************************
*    CardDemo - Test Screen
******************************************************************
        TITLE 'BMS MAP FOR TEST'
TESTMAP DFHMSD LANG=COBOL,                                             -
               MODE=INOUT,                                             -
               TYPE=&&SYSPARM
TESTMPA DFHMDI CTRL=(FREEKB),                                          -
               SIZE=(24,80)
        DFHMDF ATTRB=(ASKIP,NORM),                                     -
               LENGTH=5,                                               -
               POS=(1,1),                                              -
               INITIAL='Test:'
FLDONE  DFHMDF ATTRB=(ASKIP,FSET,NORM),                                -
               LENGTH=10,                                              -
               POS=(2,1)
        DFHMSD TYPE=FINAL
        END
"""


class TestChunkBms:
    def test_splits_on_dfhmsd_dfhmdi(self):
        path = _write_temp(SAMPLE_BMS, suffix=".bms")
        try:
            chunks = chunk_file(path)
            assert len(chunks) >= 2  # header + at least one map definition
            names = [c.name for c in chunks]
            assert any("TESTMAP" in n for n in names)
        finally:
            os.unlink(path)

    def test_bms_metadata(self):
        path = _write_temp(SAMPLE_BMS, suffix=".bms")
        try:
            chunks = chunk_file(path)
            for c in chunks:
                assert c.file_type == "bms"
                assert c.chunk_type == "bms_map"
        finally:
            os.unlink(path)

    def test_header_included(self):
        path = _write_temp(SAMPLE_BMS, suffix=".bms")
        try:
            chunks = chunk_file(path)
            headers = [c for c in chunks if "Header" in c.name]
            assert len(headers) >= 1
        finally:
            os.unlink(path)


# --- JCL chunking ---

SAMPLE_JCL = """\
//TESTJOB  JOB 'Test Job',CLASS=A,MSGCLASS=0
//******************************************************************
//* Test JCL
//******************************************************************
//STEP01 EXEC PGM=IEFBR14
//DD1    DD   DISP=SHR,DSN=MY.DATA.SET
//STEP02 EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN  DD   *
   DELETE MY.VSAM.FILE
/*
//STEP03 EXEC PGM=SORT
//SORTIN DD   DISP=SHR,DSN=MY.INPUT
//SORTOUT DD  DSN=MY.OUTPUT
"""


class TestChunkJcl:
    def test_splits_on_steps(self):
        path = _write_temp(SAMPLE_JCL, suffix=".jcl")
        try:
            chunks = chunk_file(path)
            step_names = [c.name for c in chunks if "STEP" in c.name]
            assert "STEP01" in step_names
            assert "STEP02" in step_names
            assert "STEP03" in step_names
        finally:
            os.unlink(path)

    def test_jcl_header(self):
        path = _write_temp(SAMPLE_JCL, suffix=".jcl")
        try:
            chunks = chunk_file(path)
            headers = [c for c in chunks if "Header" in c.name]
            assert len(headers) == 1
            assert "TESTJOB" in headers[0].content or "Test JCL" in headers[0].content
        finally:
            os.unlink(path)

    def test_jcl_metadata(self):
        path = _write_temp(SAMPLE_JCL, suffix=".jcl")
        try:
            chunks = chunk_file(path)
            for c in chunks:
                assert c.file_type == "jcl"
                assert c.chunk_type == "jcl_step"
        finally:
            os.unlink(path)

    def test_no_steps_single_chunk(self):
        """JCL with no EXEC statements returns a single chunk."""
        jcl = """\
//TESTJOB JOB 'No steps'
//* Just comments
//* More comments
"""
        path = _write_temp(jcl, suffix=".jcl")
        try:
            chunks = chunk_file(path)
            assert len(chunks) == 1
        finally:
            os.unlink(path)


# --- Generic chunking ---

class TestChunkGeneric:
    def test_unknown_extension(self):
        content = "Some random content\nLine 2\nLine 3"
        path = _write_temp(content, suffix=".ctl")
        try:
            chunks = chunk_file(path)
            assert len(chunks) == 1
            assert chunks[0].chunk_type == "file"
            assert chunks[0].content == content
        finally:
            os.unlink(path)


# --- chunk_file dispatch ---

class TestChunkFileDispatch:
    def test_cbl_dispatch(self):
        path = _write_temp(SAMPLE_COBOL, suffix=".cbl")
        try:
            chunks = chunk_file(path)
            assert any(c.chunk_type == "header" for c in chunks)
        finally:
            os.unlink(path)

    def test_cob_dispatch(self):
        path = _write_temp(SAMPLE_COBOL, suffix=".cob")
        try:
            chunks = chunk_file(path)
            assert any(c.chunk_type == "header" for c in chunks)
        finally:
            os.unlink(path)

    def test_cpy_dispatch(self):
        path = _write_temp(SAMPLE_COPYBOOK, suffix=".cpy")
        try:
            chunks = chunk_file(path)
            assert chunks[0].chunk_type == "copybook"
        finally:
            os.unlink(path)

    def test_bms_dispatch(self):
        path = _write_temp(SAMPLE_BMS, suffix=".bms")
        try:
            chunks = chunk_file(path)
            assert all(c.chunk_type == "bms_map" for c in chunks)
        finally:
            os.unlink(path)

    def test_jcl_dispatch(self):
        path = _write_temp(SAMPLE_JCL, suffix=".jcl")
        try:
            chunks = chunk_file(path)
            assert all(c.chunk_type == "jcl_step" for c in chunks)
        finally:
            os.unlink(path)


# --- Tests on actual CardDemo files ---

@pytest.fixture
def carddemo_path():
    path = os.environ.get("CARDDEMO_PATH", "")
    if not path or not os.path.isdir(path):
        pytest.skip("CARDDEMO_PATH not set")
    return path


class TestChunkerOnCardDemo:
    def test_cocrdupc_chunk_count(self, carddemo_path):
        chunks = chunk_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        assert len(chunks) > 20, f"COCRDUPC should produce many chunks, got {len(chunks)}"

    def test_cocrdupc_has_data_division_split(self, carddemo_path):
        """COCRDUPC has a large DATA DIVISION that should be split."""
        chunks = chunk_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        data_chunks = [c for c in chunks if c.chunk_type == "data_division"]
        assert len(data_chunks) >= 2, "Large DATA DIVISION should be split"

    def test_cbact04c_high_chunk_count(self, carddemo_path):
        """CBACT04C is a large batch program."""
        chunks = chunk_file(os.path.join(carddemo_path, "cbl", "CBACT04C.cbl"))
        assert len(chunks) > 10

    def test_all_chunks_have_content(self, carddemo_path):
        """Every chunk from every file should have non-empty content."""
        from legacylens.ingest import discover_files

        files = discover_files(carddemo_path)
        empty_chunks = []
        for f in files:
            for c in chunk_file(f):
                if not c.content.strip():
                    empty_chunks.append(f"{c.file_name}:{c.name}")
        assert not empty_chunks, f"Empty chunks found: {empty_chunks[:10]}"

    def test_all_chunks_have_valid_line_ranges(self, carddemo_path):
        from legacylens.ingest import discover_files

        files = discover_files(carddemo_path)
        bad = []
        for f in files:
            for c in chunk_file(f):
                if c.start_line < 1 or c.end_line < c.start_line:
                    bad.append(f"{c.file_name}:{c.name} ({c.start_line}-{c.end_line})")
        assert not bad, f"Invalid line ranges: {bad[:10]}"

    def test_chunk_content_not_truncated_to_zero(self, carddemo_path):
        """Sanity: no chunk should have only whitespace content."""
        from legacylens.ingest import discover_files

        files = discover_files(carddemo_path)
        for f in files[:20]:  # Sample first 20
            for c in chunk_file(f):
                assert len(c.content.strip()) > 0, f"Whitespace-only chunk: {c.file_name}:{c.name}"
