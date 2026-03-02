"""Offline regression tests for core parsing/chunking/index contracts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legacylens.chunker import chunk_file
from legacylens.ingest import discover_files
from legacylens.models import CodeChunk
from legacylens.parser import parse_cobol_file
from legacylens.vectorstore import make_vector_id


def test_make_vector_id_uses_path_and_line_range():
    chunk_a = CodeChunk(
        content="A",
        file_path="/repo/a/COMMON.cbl",
        file_name="COMMON.cbl",
        file_type="cbl",
        chunk_type="paragraph",
        name="PARA-A",
        start_line=10,
        end_line=20,
    )
    chunk_b = CodeChunk(
        content="B",
        file_path="/repo/b/COMMON.cbl",
        file_name="COMMON.cbl",
        file_type="cbl",
        chunk_type="paragraph",
        name="PARA-B",
        start_line=10,
        end_line=20,
    )

    assert make_vector_id(chunk_a) != make_vector_id(chunk_b)


def test_parser_extracts_sql_include_and_external_calls(tmp_path):
    source = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. TESTPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           COPY COCOM01Y.
           EXEC SQL INCLUDE SQLCA END-EXEC.
       PROCEDURE DIVISION.
       MAIN-PARA.
           CALL 'PROG1'.
           EXEC CICS LINK PROGRAM('PROG2') END-EXEC.
           GOBACK.
"""
    file_path = tmp_path / "TESTPROG.cbl"
    file_path.write_text(source, encoding="utf-8")

    parsed = parse_cobol_file(str(file_path))
    assert "COCOM01Y" in parsed.copy_references
    assert "SQL:SQLCA" in parsed.copy_references
    assert parsed.paragraphs
    assert "CALL PROG1" in parsed.paragraphs[0].external_calls
    assert "CICS PROG2" in parsed.paragraphs[0].external_calls


def test_chunk_bms_splits_on_dfhmsd_and_dfhmdi(tmp_path):
    source = """\
MYMAP    DFHMSD TYPE=MAP
MAP01    DFHMDI SIZE=(24,80)
  FIELD1 DFHMDF POS=(1,1),LENGTH=10
"""
    file_path = tmp_path / "TESTMAP.bms"
    file_path.write_text(source, encoding="utf-8")

    chunks = chunk_file(str(file_path))
    names = [chunk.name for chunk in chunks]
    assert "MYMAP" in names
    assert "MAP01" in names


def test_discover_files_includes_carddemo_control_artifacts(tmp_path):
    (tmp_path / "A.cbl").write_text("x", encoding="utf-8")
    (tmp_path / "B.dcl").write_text("x", encoding="utf-8")
    (tmp_path / "C.txt").write_text("x", encoding="utf-8")

    files = discover_files(str(tmp_path))
    file_names = {Path(path).name for path in files}
    assert "A.cbl" in file_names
    assert "B.dcl" in file_names
    assert "C.txt" not in file_names
