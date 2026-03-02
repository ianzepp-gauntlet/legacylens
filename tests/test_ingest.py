"""Unit tests for the ingestion module."""

import os
import tempfile

import pytest

from legacylens.ingest import SUPPORTED_EXTENSIONS, discover_files


class TestDiscoverFiles:
    def test_finds_cbl_files(self, tmp_path):
        (tmp_path / "prog.cbl").write_text("x")
        (tmp_path / "prog.py").write_text("x")
        files = discover_files(str(tmp_path))
        assert len(files) == 1
        assert files[0].endswith("prog.cbl")

    def test_finds_all_supported_extensions(self, tmp_path):
        for ext in SUPPORTED_EXTENSIONS:
            (tmp_path / f"file{ext}").write_text("x")
        (tmp_path / "file.txt").write_text("x")
        (tmp_path / "file.py").write_text("x")
        files = discover_files(str(tmp_path))
        assert len(files) == len(SUPPORTED_EXTENSIONS)

    def test_case_insensitive(self, tmp_path):
        (tmp_path / "PROG.CBL").write_text("x")
        (tmp_path / "copy.CPY").write_text("x")
        files = discover_files(str(tmp_path))
        assert len(files) == 2

    def test_recursive(self, tmp_path):
        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (tmp_path / "a.cbl").write_text("x")
        (sub / "b.cbl").write_text("x")
        files = discover_files(str(tmp_path))
        assert len(files) == 2

    def test_returns_sorted(self, tmp_path):
        (tmp_path / "z.cbl").write_text("x")
        (tmp_path / "a.cbl").write_text("x")
        (tmp_path / "m.cpy").write_text("x")
        files = discover_files(str(tmp_path))
        assert files == sorted(files)

    def test_empty_directory(self, tmp_path):
        files = discover_files(str(tmp_path))
        assert files == []

    def test_no_supported_files(self, tmp_path):
        (tmp_path / "readme.txt").write_text("x")
        (tmp_path / "main.py").write_text("x")
        files = discover_files(str(tmp_path))
        assert files == []


class TestSupportedExtensions:
    def test_cobol_extensions(self):
        assert ".cbl" in SUPPORTED_EXTENSIONS
        assert ".cob" in SUPPORTED_EXTENSIONS
        assert ".cpy" in SUPPORTED_EXTENSIONS

    def test_mainframe_extensions(self):
        assert ".bms" in SUPPORTED_EXTENSIONS
        assert ".jcl" in SUPPORTED_EXTENSIONS

    def test_database_extensions(self):
        assert ".dcl" in SUPPORTED_EXTENSIONS
        assert ".ddl" in SUPPORTED_EXTENSIONS

    def test_ims_extensions(self):
        assert ".dbd" in SUPPORTED_EXTENSIONS
        assert ".psb" in SUPPORTED_EXTENSIONS


class TestDiscoverOnCardDemo:
    @pytest.fixture
    def carddemo_path(self):
        path = os.environ.get("CARDDEMO_PATH", "")
        if not path or not os.path.isdir(path):
            pytest.skip("CARDDEMO_PATH not set")
        return path

    def test_finds_substantial_files(self, carddemo_path):
        files = discover_files(carddemo_path)
        assert len(files) > 100, f"Expected >100 files, got {len(files)}"

    def test_includes_cbl_and_cpy(self, carddemo_path):
        files = discover_files(carddemo_path)
        exts = {os.path.splitext(f)[1].lower() for f in files}
        assert ".cbl" in exts
        assert ".cpy" in exts

    def test_includes_bms_and_jcl(self, carddemo_path):
        files = discover_files(carddemo_path)
        exts = {os.path.splitext(f)[1].lower() for f in files}
        assert ".bms" in exts
        assert ".jcl" in exts
