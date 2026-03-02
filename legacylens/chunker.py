"""Syntax-aware chunking for COBOL, BMS, and JCL files.

Chunking strategy:
- COBOL (.cbl): header chunk, DATA DIVISION chunk(s), one chunk per paragraph
- Copybooks (.cpy): single chunk (most are 30-100 lines)
- BMS (.bms): split on DFHMSD/DFHMDI boundaries
- JCL (.jcl): split on //STEP or job boundaries

Each chunk gets a descriptive preamble prepended for better embeddings.
"""

import re
from pathlib import Path

from .models import CodeChunk
from .parser import ParsedFile, parse_cobol_file


MIN_PARAGRAPH_LINES = 5


def chunk_file(file_path: str) -> list[CodeChunk]:
    """Chunk a file based on its type."""
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if ext in ("cbl", "cob"):
        return _chunk_cobol(file_path)
    elif ext == "cpy":
        return _chunk_copybook(file_path)
    elif ext == "bms":
        return _chunk_bms(file_path)
    elif ext == "jcl":
        return _chunk_jcl(file_path)
    else:
        return _chunk_generic(file_path)


def _get_lines_text(lines: list[str], start: int, end: int) -> str:
    """Get text from a range of lines."""
    return "\n".join(lines[start:end])


def _build_preamble(
    file_name: str,
    program_id: str = "",
    layer: str = "",
    description: str = "",
    chunk_type: str = "",
    name: str = "",
    start_line: int = 0,
    end_line: int = 0,
    copy_refs: list[str] | None = None,
    calls_to: list[str] | None = None,
) -> str:
    """Build a descriptive preamble for a chunk."""
    parts = [f"File: {file_name}"]
    if program_id:
        desc_parts = [program_id]
        if layer:
            desc_parts.append(f"- {layer}")
        if description:
            desc_parts.append(f"- {description}")
        parts.append(f"Program: {' '.join(desc_parts)}")
    if chunk_type and name:
        parts.append(f"{chunk_type}: {name} (lines {start_line + 1}-{end_line})")
    if copy_refs:
        parts.append(f"References: {', '.join(f'COPY {r}' for r in copy_refs)}")
    if calls_to:
        parts.append(f"Calls: {', '.join(calls_to)}")
    return "\n".join(parts)


def _chunk_cobol(file_path: str) -> list[CodeChunk]:
    """Chunk a COBOL program file."""
    parsed = parse_cobol_file(file_path)
    chunks = []

    # Chunk 1: Header + IDENTIFICATION DIVISION
    id_div = next((d for d in parsed.divisions if d.name == "IDENTIFICATION"), None)
    env_div = next((d for d in parsed.divisions if d.name == "ENVIRONMENT"), None)
    header_end = env_div.start_line if env_div else (id_div.end_line if id_div else 30)
    header_text = _get_lines_text(parsed.lines, 0, header_end)

    preamble = _build_preamble(
        file_name=parsed.file_name,
        program_id=parsed.program_id,
        layer=parsed.program_layer,
        description=parsed.program_description,
        chunk_type="Section",
        name="Header and Identification",
        start_line=0,
        end_line=header_end,
        copy_refs=parsed.copy_references,
    )
    chunks.append(CodeChunk(
        content=header_text,
        file_path=parsed.file_path,
        file_name=parsed.file_name,
        file_type=parsed.file_type,
        chunk_type="header",
        name=f"{parsed.program_id or parsed.file_name} Header",
        start_line=1,
        end_line=header_end,
        preamble=preamble,
        parent_program=parsed.program_id,
        comments="\n".join(parsed.header_comments),
        copy_references=parsed.copy_references,
    ))

    # Chunk 2: DATA DIVISION (may be large - split at 01-level if >200 lines)
    data_div = next((d for d in parsed.divisions if d.name == "DATA"), None)
    proc_div = next((d for d in parsed.divisions if d.name == "PROCEDURE"), None)

    if data_div:
        data_end = proc_div.start_line if proc_div else data_div.end_line
        data_lines_count = data_end - data_div.start_line

        if data_lines_count > 200:
            # Split at 01-level boundaries
            level_01_pattern = re.compile(r"^\s+01\s+", re.IGNORECASE)
            boundaries = [data_div.start_line]
            for i in range(data_div.start_line + 1, data_end):
                if i < len(parsed.lines) and level_01_pattern.match(parsed.lines[i]):
                    boundaries.append(i)
            boundaries.append(data_end)

            for idx in range(len(boundaries) - 1):
                seg_start = boundaries[idx]
                seg_end = boundaries[idx + 1]
                text = _get_lines_text(parsed.lines, seg_start, seg_end)
                # Get the 01-level name if possible
                seg_name = "DATA DIVISION"
                if seg_start < len(parsed.lines):
                    m = re.search(r"01\s+([A-Z0-9-]+)", parsed.lines[seg_start], re.IGNORECASE)
                    if m:
                        seg_name = m.group(1).upper()

                preamble = _build_preamble(
                    file_name=parsed.file_name,
                    program_id=parsed.program_id,
                    layer=parsed.program_layer,
                    description=parsed.program_description,
                    chunk_type="Data",
                    name=seg_name,
                    start_line=seg_start,
                    end_line=seg_end,
                )
                chunks.append(CodeChunk(
                    content=text,
                    file_path=parsed.file_path,
                    file_name=parsed.file_name,
                    file_type=parsed.file_type,
                    chunk_type="data_division",
                    name=seg_name,
                    start_line=seg_start + 1,
                    end_line=seg_end,
                    preamble=preamble,
                    parent_program=parsed.program_id,
                    copy_references=parsed.copy_references,
                ))
        else:
            text = _get_lines_text(parsed.lines, data_div.start_line, data_end)
            preamble = _build_preamble(
                file_name=parsed.file_name,
                program_id=parsed.program_id,
                layer=parsed.program_layer,
                description=parsed.program_description,
                chunk_type="Section",
                name="DATA DIVISION",
                start_line=data_div.start_line,
                end_line=data_end,
            )
            chunks.append(CodeChunk(
                content=text,
                file_path=parsed.file_path,
                file_name=parsed.file_name,
                file_type=parsed.file_type,
                chunk_type="data_division",
                name="DATA DIVISION",
                start_line=data_div.start_line + 1,
                end_line=data_end,
                preamble=preamble,
                parent_program=parsed.program_id,
                copy_references=parsed.copy_references,
            ))

    # Chunk 3-N: Each PROCEDURE DIVISION paragraph
    # Merge short paragraphs (<5 lines) with predecessor
    merged_paragraphs = []
    for para in parsed.paragraphs:
        para_len = para.end_line - para.start_line
        if para_len < MIN_PARAGRAPH_LINES and merged_paragraphs:
            # Merge with previous
            prev = merged_paragraphs[-1]
            prev["end_line"] = para.end_line
            prev["names"].append(para.name)
            prev["perform_targets"].extend(para.perform_targets)
            prev["external_calls"].extend(para.external_calls)
            prev["comments"].extend(para.comments)
        else:
            merged_paragraphs.append({
                "names": [para.name],
                "start_line": para.start_line,
                "end_line": para.end_line,
                "comments": list(para.comments),
                "perform_targets": list(para.perform_targets),
                "external_calls": list(para.external_calls),
            })

    for mp in merged_paragraphs:
        text = _get_lines_text(parsed.lines, mp["start_line"], mp["end_line"])
        name = ", ".join(mp["names"])
        calls = sorted(
            set([f"PERFORM {target}" for target in mp["perform_targets"]] + mp["external_calls"])
        )
        preamble = _build_preamble(
            file_name=parsed.file_name,
            program_id=parsed.program_id,
            layer=parsed.program_layer,
            description=parsed.program_description,
            chunk_type="Paragraph",
            name=name,
            start_line=mp["start_line"],
            end_line=mp["end_line"],
            copy_refs=parsed.copy_references,
            calls_to=calls,
        )
        chunks.append(CodeChunk(
            content=text,
            file_path=parsed.file_path,
            file_name=parsed.file_name,
            file_type=parsed.file_type,
            chunk_type="paragraph",
            name=name,
            start_line=mp["start_line"] + 1,
            end_line=mp["end_line"],
            preamble=preamble,
            parent_program=parsed.program_id,
            comments="\n".join(mp["comments"]),
            copy_references=parsed.copy_references,
            calls_to=calls,
        ))

    return chunks


def _chunk_copybook(file_path: str) -> list[CodeChunk]:
    """Chunk a copybook file (usually single chunk)."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Extract header comments
    comments = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("*"):
            comments.append(stripped.lstrip("*").strip())
        elif not stripped:
            if comments:
                break
        else:
            break

    preamble = _build_preamble(
        file_name=path.name,
        chunk_type="Copybook",
        name=path.stem.upper(),
        start_line=0,
        end_line=len(lines),
    )

    return [CodeChunk(
        content=text,
        file_path=str(file_path),
        file_name=path.name,
        file_type="cpy",
        chunk_type="copybook",
        name=path.stem.upper(),
        start_line=1,
        end_line=len(lines),
        preamble=preamble,
        comments="\n".join(comments),
    )]


def _chunk_bms(file_path: str) -> list[CodeChunk]:
    """Chunk a BMS map file on DFHMSD/DFHMDI boundaries."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Find DFHMSD/DFHMDI boundaries (mapset and map definitions)
    boundaries = []
    map_pattern = re.compile(r"^(\w+)\s+DFHM(?:SD|DI)\b", re.IGNORECASE)
    for i, line in enumerate(lines):
        m = map_pattern.match(line)
        if m:
            boundaries.append((i, m.group(1).upper()))

    if not boundaries:
        # No maps found, return as single chunk
        preamble = _build_preamble(
            file_name=path.name,
            chunk_type="BMS Map",
            name=path.stem.upper(),
            start_line=0,
            end_line=len(lines),
        )
        return [CodeChunk(
            content=text,
            file_path=str(file_path),
            file_name=path.name,
            file_type="bms",
            chunk_type="bms_map",
            name=path.stem.upper(),
            start_line=1,
            end_line=len(lines),
            preamble=preamble,
        )]

    chunks = []
    for idx, (start, name) in enumerate(boundaries):
        end = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        chunk_text = "\n".join(lines[start:end])
        preamble = _build_preamble(
            file_name=path.name,
            chunk_type="BMS Map",
            name=name,
            start_line=start,
            end_line=end,
        )
        chunks.append(CodeChunk(
            content=chunk_text,
            file_path=str(file_path),
            file_name=path.name,
            file_type="bms",
            chunk_type="bms_map",
            name=name,
            start_line=start + 1,
            end_line=end,
            preamble=preamble,
        ))

    # Include header if first boundary isn't at line 0
    if boundaries[0][0] > 0:
        header_text = "\n".join(lines[:boundaries[0][0]])
        preamble = _build_preamble(
            file_name=path.name,
            chunk_type="BMS Header",
            name=path.stem.upper(),
            start_line=0,
            end_line=boundaries[0][0],
        )
        chunks.insert(0, CodeChunk(
            content=header_text,
            file_path=str(file_path),
            file_name=path.name,
            file_type="bms",
            chunk_type="bms_map",
            name=f"{path.stem.upper()} Header",
            start_line=1,
            end_line=boundaries[0][0],
            preamble=preamble,
        ))

    return chunks


def _chunk_jcl(file_path: str) -> list[CodeChunk]:
    """Chunk a JCL file on step boundaries."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Find step boundaries
    step_pattern = re.compile(r"^//(\w+)\s+EXEC\s+", re.IGNORECASE)
    boundaries = []
    for i, line in enumerate(lines):
        m = step_pattern.match(line)
        if m:
            boundaries.append((i, m.group(1).upper()))

    if not boundaries:
        preamble = _build_preamble(
            file_name=path.name,
            chunk_type="JCL Job",
            name=path.stem.upper(),
            start_line=0,
            end_line=len(lines),
        )
        return [CodeChunk(
            content=text,
            file_path=str(file_path),
            file_name=path.name,
            file_type="jcl",
            chunk_type="jcl_step",
            name=path.stem.upper(),
            start_line=1,
            end_line=len(lines),
            preamble=preamble,
        )]

    chunks = []

    # Header (job card + comments before first step)
    if boundaries[0][0] > 0:
        header_text = "\n".join(lines[:boundaries[0][0]])
        preamble = _build_preamble(
            file_name=path.name,
            chunk_type="JCL Header",
            name=path.stem.upper(),
            start_line=0,
            end_line=boundaries[0][0],
        )
        chunks.append(CodeChunk(
            content=header_text,
            file_path=str(file_path),
            file_name=path.name,
            file_type="jcl",
            chunk_type="jcl_step",
            name=f"{path.stem.upper()} Header",
            start_line=1,
            end_line=boundaries[0][0],
            preamble=preamble,
        ))

    for idx, (start, name) in enumerate(boundaries):
        end = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        chunk_text = "\n".join(lines[start:end])
        preamble = _build_preamble(
            file_name=path.name,
            chunk_type="JCL Step",
            name=name,
            start_line=start,
            end_line=end,
        )
        chunks.append(CodeChunk(
            content=chunk_text,
            file_path=str(file_path),
            file_name=path.name,
            file_type="jcl",
            chunk_type="jcl_step",
            name=name,
            start_line=start + 1,
            end_line=end,
            preamble=preamble,
        ))

    return chunks


def _chunk_generic(file_path: str) -> list[CodeChunk]:
    """Fallback chunker for unknown file types."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    preamble = _build_preamble(
        file_name=path.name,
        chunk_type="File",
        name=path.stem.upper(),
        start_line=0,
        end_line=len(lines),
    )
    return [CodeChunk(
        content=text,
        file_path=str(file_path),
        file_name=path.name,
        file_type=path.suffix.lower().lstrip("."),
        chunk_type="file",
        name=path.stem.upper(),
        start_line=1,
        end_line=len(lines),
        preamble=preamble,
    )]
