"""Unit tests for the COBOL parser module."""

import os
import tempfile

import pytest

from legacylens.parser import (
    ParsedFile,
    detect_sequence_numbers,
    is_comment_line,
    parse_cobol_file,
    strip_sequence_numbers,
)


# --- Helper to write temp COBOL files ---

def _write_temp(content: str, suffix: str = ".cbl") -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


# --- Sequence number detection ---

class TestSequenceNumberDetection:
    def test_detects_sequence_numbers(self):
        lines = ["000100       IDENTIFICATION DIVISION.", "000200       PROGRAM-ID. FOO."]
        assert detect_sequence_numbers(lines) is True

    def test_detects_no_sequence_numbers(self):
        lines = ["      *Comment line", "       IDENTIFICATION DIVISION."]
        assert detect_sequence_numbers(lines) is False

    def test_empty_file(self):
        assert detect_sequence_numbers([]) is False

    def test_blank_lines_before_content(self):
        lines = ["", "", "      *Comment", "       IDENTIFICATION DIVISION."]
        assert detect_sequence_numbers(lines) is False

    def test_mixed_lines_uses_first_nonblank(self):
        lines = ["", "000100       IDENTIFICATION DIVISION."]
        assert detect_sequence_numbers(lines) is True


class TestStripSequenceNumbers:
    def test_strips_when_present(self):
        assert strip_sequence_numbers("000100       IDENTIFICATION DIVISION.", True) == \
            "       IDENTIFICATION DIVISION."

    def test_no_strip_when_absent(self):
        line = "       IDENTIFICATION DIVISION."
        assert strip_sequence_numbers(line, False) == line

    def test_short_line(self):
        assert strip_sequence_numbers("ABC", True) == "ABC"

    def test_non_numeric_prefix_not_stripped(self):
        line = "ABCDEF       IDENTIFICATION DIVISION."
        assert strip_sequence_numbers(line, True) == line


class TestIsCommentLine:
    def test_asterisk_col7(self):
        assert is_comment_line("      * This is a comment") is True

    def test_asterisk_col1(self):
        assert is_comment_line("* Comment") is True

    def test_not_comment(self):
        assert is_comment_line("       MOVE A TO B.") is False

    def test_empty_line(self):
        assert is_comment_line("") is False

    def test_short_line(self):
        assert is_comment_line("X") is False


# --- Full file parsing (synthetic) ---

SAMPLE_COBOL_NO_SEQ = """\
      *****************************************************************
      * Program:     TESTPROG.CBL
      * Layer:       Business logic
      * Function:    Test program for unit tests
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.
           TESTPROG.
       DATE-WRITTEN.
           March 2026.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-VARS.
         05 WS-NAME                PIC X(30).
         05 WS-COUNT               PIC 9(5).

       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-INIT
           PERFORM 2000-PROCESS
           STOP RUN.

       0000-MAIN-EXIT.
           EXIT.

       1000-INIT.
           MOVE SPACES TO WS-NAME
           MOVE ZEROS TO WS-COUNT.

       1000-INIT-EXIT.
           EXIT.

       2000-PROCESS.
           COPY SOMELIB.
           DISPLAY 'HELLO'.

       2000-PROCESS-EXIT.
           EXIT.
"""

SAMPLE_COBOL_WITH_SEQ = """\
000100*****************************************************************
000200* PROGRAM     : SEQPROG.CBL
000300* Application : TestApp
000400* Type        : BATCH COBOL Program
000500* FUNCTION    : Test batch program
000600*****************************************************************
000700 IDENTIFICATION DIVISION.
000800 PROGRAM-ID.    SEQPROG.
000900 AUTHOR.        TEST.
001000
001100 ENVIRONMENT DIVISION.
001200
001300 DATA DIVISION.
001400 WORKING-STORAGE SECTION.
001500 01  WS-DATA           PIC X(10).
001600
001700 PROCEDURE DIVISION.
001800 MAIN-PARA.
001900     DISPLAY 'HELLO'.
002000     STOP RUN.
002100 MAIN-PARA-EXIT.
002200     EXIT.
"""


class TestParseCobolFile:
    def test_parse_no_sequence_numbers(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            assert parsed.has_sequence_numbers is False
            assert parsed.program_id == "TESTPROG"
            assert parsed.program_layer == "Business logic"
            assert parsed.program_description == "Test program for unit tests"
        finally:
            os.unlink(path)

    def test_parse_with_sequence_numbers(self):
        path = _write_temp(SAMPLE_COBOL_WITH_SEQ)
        try:
            parsed = parse_cobol_file(path)
            assert parsed.has_sequence_numbers is True
            assert parsed.program_id == "SEQPROG"
            assert parsed.program_layer == "BATCH COBOL Program"
            assert parsed.program_description == "Test batch program"
        finally:
            os.unlink(path)

    def test_divisions_extracted(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            div_names = [d.name for d in parsed.divisions]
            assert "IDENTIFICATION" in div_names
            assert "ENVIRONMENT" in div_names
            assert "DATA" in div_names
            assert "PROCEDURE" in div_names
        finally:
            os.unlink(path)

    def test_division_ordering(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            starts = [d.start_line for d in parsed.divisions]
            assert starts == sorted(starts), "Divisions should be in file order"
        finally:
            os.unlink(path)

    def test_division_boundaries_non_overlapping(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            for i in range(len(parsed.divisions) - 1):
                assert parsed.divisions[i].end_line == parsed.divisions[i + 1].start_line
        finally:
            os.unlink(path)

    def test_paragraphs_extracted(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            names = [p.name for p in parsed.paragraphs]
            assert "0000-MAIN" in names
            assert "1000-INIT" in names
            assert "2000-PROCESS" in names
        finally:
            os.unlink(path)

    def test_paragraph_boundaries(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            for p in parsed.paragraphs:
                assert p.start_line < p.end_line, f"{p.name} has invalid boundaries"
            # Non-overlapping
            for i in range(len(parsed.paragraphs) - 1):
                assert parsed.paragraphs[i].end_line == parsed.paragraphs[i + 1].start_line
        finally:
            os.unlink(path)

    def test_perform_targets(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            main_para = next(p for p in parsed.paragraphs if p.name == "0000-MAIN")
            assert "1000-INIT" in main_para.perform_targets
            assert "2000-PROCESS" in main_para.perform_targets
        finally:
            os.unlink(path)

    def test_copy_references(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            assert "SOMELIB" in parsed.copy_references
        finally:
            os.unlink(path)

    def test_header_comments(self):
        path = _write_temp(SAMPLE_COBOL_NO_SEQ)
        try:
            parsed = parse_cobol_file(path)
            assert len(parsed.header_comments) > 0
            full_text = " ".join(parsed.header_comments)
            assert "TESTPROG" in full_text
        finally:
            os.unlink(path)


# --- External call detection ---

SAMPLE_WITH_CALLS = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLTEST.

       ENVIRONMENT DIVISION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-X PIC X.

       PROCEDURE DIVISION.
       MAIN-PARA.
           CALL 'SUBPROG1'
           EXEC CICS LINK PROGRAM('SUBPROG2')
               END-EXEC
           PERFORM DO-STUFF
           STOP RUN.
       DO-STUFF.
           DISPLAY 'OK'.
"""


class TestExternalCalls:
    def test_call_statement_detected(self):
        path = _write_temp(SAMPLE_WITH_CALLS)
        try:
            parsed = parse_cobol_file(path)
            main_para = next(p for p in parsed.paragraphs if p.name == "MAIN-PARA")
            assert "CALL SUBPROG1" in main_para.external_calls
        finally:
            os.unlink(path)

    def test_cics_link_detected(self):
        path = _write_temp(SAMPLE_WITH_CALLS)
        try:
            parsed = parse_cobol_file(path)
            main_para = next(p for p in parsed.paragraphs if p.name == "MAIN-PARA")
            assert "CICS SUBPROG2" in main_para.external_calls
        finally:
            os.unlink(path)

    def test_perform_not_in_external_calls(self):
        path = _write_temp(SAMPLE_WITH_CALLS)
        try:
            parsed = parse_cobol_file(path)
            main_para = next(p for p in parsed.paragraphs if p.name == "MAIN-PARA")
            assert all("DO-STUFF" not in ec for ec in main_para.external_calls)
            assert "DO-STUFF" in main_para.perform_targets
        finally:
            os.unlink(path)


# --- Edge cases ---

class TestParserEdgeCases:
    def test_no_procedure_division(self):
        """Copybook-like file with no PROCEDURE DIVISION."""
        src = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. NOPROC.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-X PIC X.
"""
        path = _write_temp(src)
        try:
            parsed = parse_cobol_file(path)
            assert parsed.program_id == "NOPROC"
            assert len(parsed.paragraphs) == 0
        finally:
            os.unlink(path)

    def test_program_id_on_same_line(self):
        src = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INLINE.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       PROCEDURE DIVISION.
       MAIN-PARA.
           STOP RUN.
"""
        path = _write_temp(src)
        try:
            parsed = parse_cobol_file(path)
            assert parsed.program_id == "INLINE"
        finally:
            os.unlink(path)

    def test_comment_in_copy_not_extracted(self):
        """COPY in a comment line should not be extracted."""
        src = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMTTEST.
      * COPY NOTREAL.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       COPY REALCOPY.
       PROCEDURE DIVISION.
       MAIN-PARA.
           STOP RUN.
"""
        path = _write_temp(src)
        try:
            parsed = parse_cobol_file(path)
            assert "REALCOPY" in parsed.copy_references
            assert "NOTREAL" not in parsed.copy_references
        finally:
            os.unlink(path)

    def test_empty_file(self):
        path = _write_temp("")
        try:
            parsed = parse_cobol_file(path)
            assert parsed.program_id == ""
            assert len(parsed.divisions) == 0
            assert len(parsed.paragraphs) == 0
        finally:
            os.unlink(path)


# --- Tests on actual CardDemo files ---

@pytest.fixture
def carddemo_path():
    path = os.environ.get("CARDDEMO_PATH", "")
    if not path or not os.path.isdir(path):
        pytest.skip("CARDDEMO_PATH not set")
    return path


class TestParserOnCardDemo:
    def test_cocrdupc_header_metadata(self, carddemo_path):
        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        assert parsed.program_id == "COCRDUPC"
        assert "Business logic" in parsed.program_layer
        assert "credit card" in parsed.program_description.lower()

    def test_cocrdupc_all_paragraphs_have_boundaries(self, carddemo_path):
        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        for p in parsed.paragraphs:
            assert p.end_line > p.start_line, f"{p.name} has invalid range"

    def test_cocrdupc_known_paragraphs(self, carddemo_path):
        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        names = {p.name for p in parsed.paragraphs}
        assert "0000-MAIN" in names
        assert "1200-EDIT-MAP-INPUTS" in names
        assert "1220-EDIT-CARD" in names

    def test_cocrdupc_copy_refs_known(self, carddemo_path):
        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "COCRDUPC.cbl"))
        assert "CVCRD01Y" in parsed.copy_references
        assert "COCOM01Y" in parsed.copy_references
        assert "DFHAID" in parsed.copy_references

    def test_cbact01c_seq_numbers(self, carddemo_path):
        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "CBACT01C.cbl"))
        assert parsed.has_sequence_numbers is True
        assert parsed.program_id == "CBACT01C"

    def test_comen01c_is_menu(self, carddemo_path):
        parsed = parse_cobol_file(os.path.join(carddemo_path, "cbl", "COMEN01C.cbl"))
        assert parsed.program_id == "COMEN01C"
        assert len(parsed.paragraphs) > 0

    def test_all_programs_have_program_id(self, carddemo_path):
        """Every .cbl file should yield a program ID."""
        cbl_dir = os.path.join(carddemo_path, "cbl")
        if not os.path.isdir(cbl_dir):
            pytest.skip("No cbl directory")
        for fname in os.listdir(cbl_dir):
            if fname.lower().endswith((".cbl", ".cob")):
                parsed = parse_cobol_file(os.path.join(cbl_dir, fname))
                assert parsed.program_id, f"{fname} has no program_id"

    def test_all_programs_have_divisions(self, carddemo_path):
        """Every .cbl file should have at least IDENTIFICATION + one other division."""
        cbl_dir = os.path.join(carddemo_path, "cbl")
        if not os.path.isdir(cbl_dir):
            pytest.skip("No cbl directory")
        for fname in os.listdir(cbl_dir):
            if fname.lower().endswith((".cbl", ".cob")):
                parsed = parse_cobol_file(os.path.join(cbl_dir, fname))
                assert len(parsed.divisions) >= 2, f"{fname} has only {len(parsed.divisions)} divisions"
