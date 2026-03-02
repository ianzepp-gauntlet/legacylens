"""COBOL file structure parser.

Handles two format variants in CardDemo:
- With sequence numbers: cols 1-6 are digits (e.g., 000100)
- Without sequence numbers: cols 1-6 are spaces

Extracts: header comments, program ID, divisions, paragraphs,
COPY references, PERFORM targets, and external program calls.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Paragraph:
    name: str
    start_line: int
    end_line: int = 0
    comments: list[str] = field(default_factory=list)
    perform_targets: list[str] = field(default_factory=list)
    external_calls: list[str] = field(default_factory=list)


@dataclass
class Division:
    name: str
    start_line: int
    end_line: int = 0


@dataclass
class ParsedFile:
    file_path: str
    file_name: str
    file_type: str
    has_sequence_numbers: bool
    header_comments: list[str] = field(default_factory=list)
    program_id: str = ""
    program_description: str = ""
    program_layer: str = ""
    divisions: list[Division] = field(default_factory=list)
    paragraphs: list[Paragraph] = field(default_factory=list)
    copy_references: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)


def detect_sequence_numbers(raw_lines: list[str]) -> bool:
    """Check if file uses sequence numbers in columns 1-6."""
    for line in raw_lines[:30]:
        if len(line) >= 7 and line[:6].strip():
            if re.match(r"^\d{6}", line):
                return True
            return False
    return False


def strip_sequence_numbers(line: str, has_seq: bool) -> str:
    """Remove sequence numbers from a line, returning the COBOL content."""
    if has_seq and len(line) >= 6 and re.match(r"^\d{6}", line):
        return line[6:]
    return line


def is_comment_line(cobol_line: str) -> bool:
    """Check if a COBOL line is a comment (col 7 = '*')."""
    if len(cobol_line) >= 2:
        return cobol_line[0] == "*" or (len(cobol_line) >= 7 and cobol_line[6] == "*")
    return False


def parse_cobol_file(file_path: str) -> ParsedFile:
    """Parse a COBOL source file and extract structural information."""
    path = Path(file_path)
    raw_text = path.read_text(encoding="utf-8", errors="replace")
    raw_lines = raw_text.splitlines()

    has_seq = detect_sequence_numbers(raw_lines)

    # Strip sequence numbers to get normalized COBOL lines
    lines = [strip_sequence_numbers(line, has_seq) for line in raw_lines]

    file_type = path.suffix.lower().lstrip(".")
    if file_type in ("cbl", "cob"):
        file_type = "cbl"
    elif file_type == "cpy":
        file_type = "cpy"

    parsed = ParsedFile(
        file_path=str(file_path),
        file_name=path.name,
        file_type=file_type,
        has_sequence_numbers=has_seq,
        lines=lines,
        raw_lines=raw_lines,
    )

    _extract_header_comments(parsed)
    _extract_program_id(parsed)
    _extract_divisions(parsed)
    _extract_paragraphs(parsed)
    _extract_copy_references(parsed)

    return parsed


def _extract_header_comments(parsed: ParsedFile):
    """Extract the header comment block at the top of the file."""
    comments = []
    for line in parsed.lines:
        stripped = line.strip()
        if stripped.startswith("*"):
            text = stripped.lstrip("*").strip()
            comments.append(text)
        elif not stripped:
            if comments:
                break
            continue
        else:
            break
    parsed.header_comments = comments

    # Extract program description from header
    for c in comments:
        m = re.match(r"(?:Program|PROGRAM)\s*:?\s*(.+)", c)
        if m:
            continue  # Skip the program name line
        m = re.match(r"(?:Function|FUNCTION)\s*:?\s*(.+)", c)
        if m:
            parsed.program_description = m.group(1).strip().rstrip("*").strip()
        m = re.match(r"(?:Layer|LAYER)\s*:?\s*(.+)", c)
        if m:
            parsed.program_layer = m.group(1).strip().rstrip("*").strip()
        m = re.match(r"(?:Type|TYPE)\s*:?\s*(.+)", c)
        if m and not parsed.program_layer:
            parsed.program_layer = m.group(1).strip().rstrip("*").strip()


def _extract_program_id(parsed: ParsedFile):
    """Extract the PROGRAM-ID from the source."""
    for i, line in enumerate(parsed.lines):
        if "PROGRAM-ID" in line.upper():
            # Program ID might be on same line or next line
            m = re.search(r"PROGRAM-ID\.?\s+(\w+)", line, re.IGNORECASE)
            if m:
                parsed.program_id = m.group(1).upper()
            elif i + 1 < len(parsed.lines):
                next_line = parsed.lines[i + 1].strip().rstrip(".")
                parsed.program_id = next_line.strip().upper()
            break


def _extract_divisions(parsed: ParsedFile):
    """Find DIVISION boundaries."""
    divisions = []
    div_pattern = re.compile(
        r"^\s+(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION",
        re.IGNORECASE,
    )
    for i, line in enumerate(parsed.lines):
        m = div_pattern.match(line)
        if m:
            div_name = m.group(1).upper()
            if divisions:
                divisions[-1].end_line = i  # 0-indexed exclusive
            divisions.append(Division(name=div_name, start_line=i))

    if divisions:
        divisions[-1].end_line = len(parsed.lines)
    parsed.divisions = divisions


def _extract_paragraphs(parsed: ParsedFile):
    """Extract paragraphs from the PROCEDURE DIVISION."""
    proc_div = None
    for d in parsed.divisions:
        if d.name == "PROCEDURE":
            proc_div = d
            break
    if not proc_div:
        return

    paragraphs = []
    # COBOL paragraph: starts in col 8-11 (area A), is a name followed by a period
    para_pattern = re.compile(r"^       ([A-Z0-9][A-Z0-9-]*)\.\s*$", re.IGNORECASE)

    for i in range(proc_div.start_line + 1, proc_div.end_line):
        line = parsed.lines[i] if i < len(parsed.lines) else ""
        m = para_pattern.match(line)
        if m:
            para_name = m.group(1).upper()
            # Collect preceding comment lines
            comments = []
            j = i - 1
            while j >= proc_div.start_line:
                prev = parsed.lines[j].strip()
                if prev.startswith("*"):
                    comments.insert(0, prev.lstrip("*").strip())
                    j -= 1
                elif not prev:
                    j -= 1
                else:
                    break

            if paragraphs:
                paragraphs[-1].end_line = i

            paragraphs.append(Paragraph(
                name=para_name,
                start_line=i,
                comments=comments,
            ))

    if paragraphs:
        paragraphs[-1].end_line = proc_div.end_line

    # Extract PERFORM targets and external call targets for each paragraph
    perform_pattern = re.compile(r"PERFORM\s+([A-Z0-9][A-Z0-9-]*)", re.IGNORECASE)
    call_pattern = re.compile(r"\bCALL\s+['\"]?([A-Z0-9][A-Z0-9-]*)['\"]?", re.IGNORECASE)
    cics_link_pattern = re.compile(
        r"\bEXEC\s+CICS\s+(?:LINK|XCTL)\s+PROGRAM\s*\(\s*['\"]?([A-Z0-9][A-Z0-9-]*)['\"]?",
        re.IGNORECASE,
    )
    for para in paragraphs:
        targets = set()
        external_calls = set()
        for i in range(para.start_line, min(para.end_line, len(parsed.lines))):
            line = parsed.lines[i]
            for m in perform_pattern.finditer(line):
                target = m.group(1).upper()
                if target not in ("UNTIL", "VARYING", "WITH", "THRU", "THROUGH", "TIMES"):
                    targets.add(target)
            for m in call_pattern.finditer(line):
                external_calls.add(f"CALL {m.group(1).upper()}")
            for m in cics_link_pattern.finditer(line):
                external_calls.add(f"CICS {m.group(1).upper()}")
        para.perform_targets = sorted(targets)
        para.external_calls = sorted(external_calls)

    parsed.paragraphs = paragraphs


def _extract_copy_references(parsed: ParsedFile):
    """Extract COPY and EXEC SQL INCLUDE references."""
    refs = []
    copy_pattern = re.compile(r"\bCOPY\s+([A-Z0-9]+)", re.IGNORECASE)
    sql_include_pattern = re.compile(
        r"\bEXEC\s+SQL\s+INCLUDE\s+([A-Z0-9][A-Z0-9-]*)",
        re.IGNORECASE,
    )
    for line in parsed.lines:
        if line.strip().startswith("*"):
            continue
        for m in copy_pattern.finditer(line):
            ref = m.group(1).upper()
            if ref not in refs:
                refs.append(ref)
        for m in sql_include_pattern.finditer(line):
            ref = f"SQL:{m.group(1).upper()}"
            if ref not in refs:
                refs.append(ref)
    parsed.copy_references = refs
