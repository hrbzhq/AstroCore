"""A small replicator agent: parse paper text and generate a reproduction notebook template.

This is a heuristic, offline tool that reads a text file (or plain text string),
extracts common sections (Abstract, Introduction, Methods, Results, Discussion),
and writes a Jupyter notebook with Markdown cells for those sections and a
placeholder code cell for reproduction steps.
"""
from pathlib import Path
import re
import json
from typing import Dict, List
from astrocore import nlp_extractor, codegen


SECTION_ORDER = ["Title", "Abstract", "Introduction", "Methods", "Materials", "Results", "Discussion", "Conclusion", "References"]


def read_text_file(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    return text


def extract_sections_from_text(text: str) -> Dict[str, str]:
    """Heuristically extract major sections from a paper text.

    Returns a dict mapping section name to content.
    """
    sections: Dict[str, List[str]] = {}
    # Normalize headings: lines that are all caps or start with a common word
    lines = text.splitlines()

    current = "Title"
    sections[current] = []
    heading_re = re.compile(r"^(?:\s*)(Abstract|Introduction|Methods|Materials|Results|Discussion|Conclusion|References)\s*$", re.IGNORECASE)

    for ln in lines:
        m = heading_re.match(ln.strip())
        if m:
            current = m.group(1).title()
            sections[current] = []
        else:
            sections.setdefault(current, []).append(ln)

    # Join
    out = {}
    for k, v in sections.items():
        # Trim leading/trailing blank lines
        s = "\n".join(v).strip()
        if s:
            out[k] = s

    return out


def make_notebook_from_sections(sections: Dict[str, str], populate_code: bool = False, extraction: Dict = None) -> Dict:
    """Return a nbformat-compatible dict representing a notebook.

    Notebook will contain markdown cells for each known section (in SECTION_ORDER),
    then a code cell with reproduction placeholders.
    """
    cells = []

    # Title cell
    title = sections.get("Title", "Paper Reproduction")
    cells.append({
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [f"# {title}\n"]
    })

    for sec in SECTION_ORDER[1:]:
        if sec in sections:
            cells.append({
                "cell_type": "markdown",
                "metadata": {"language": "markdown"},
                "source": [f"## {sec}\n", sections[sec]]
            })

    # precompute extraction if not provided
    if extraction is None:
        extraction = nlp_extractor.extract_parameters(sections.get('Methods', ''))

    # Add a code cell: either placeholder or auto-generated from Methods
    if populate_code and 'Methods' in sections:
        # pass detected data_path and fs into code generation where applicable
        data_path = extraction.get('data_path')
        fs = extraction.get('fs')
        code_lines = codegen.generate_code_from_extraction(extraction, data_path=data_path, fs=fs)
        # replace placeholders in code lines if data_path or fs provided
        # codegen currently supports embedding data_path and fs directly for Welch
        # so regenerate welch portion with explicit args when present
        if 'Welch' in extraction.get('methods', []):
            welch_lines = codegen.generate_welch_code(extraction.get('params', {}), data_path=data_path, fs=fs)
            # replace first occurrence of 'signal.welch' block with welch_lines
            # simple strategy: if any line contains 'signal.welch', replace whole code_lines with welch_lines + rest
            if any('signal.welch' in l for l in code_lines):
                # append bandpass code if present
                tail = []
                if extraction.get('bandpass'):
                    tail = ['\n'] + codegen.generate_bandpass_code(extraction.get('bandpass'), extraction.get('filters', []))
                code_lines = welch_lines + tail
    else:
        code_lines = [
            "# Reproduction steps - fill in code to reproduce key analyses from the paper\n",
            "# 1) Load data\n",
            "# 2) Preprocess\n",
            "# 3) Run core analysis\n",
            "# 4) Visualize / compare to reported results\n",
            "\n",
            "print('Replace this cell with code to reproduce the paper results')\n"
        ]

    cells.append({
        "cell_type": "code",
        "metadata": {"language": "python"},
        "source": code_lines
    })

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"}
        },
        # embed the structured extraction to help auditing / review of generated code
        "astrocore_extraction": extraction,
        "nbformat": 4,
        "nbformat_minor": 5
    }
    return nb


def write_notebook(nb: Dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_notebook_from_paper_file(paper_path: Path, out_path: Path, populate_code: bool = False) -> Path:
    """High-level helper: read paper text and generate notebook file.

    If the input is a PDF, this function will raise a NotImplementedError and
    suggest installing PyMuPDF or converting PDF to text externally.
    """
    p = Path(paper_path)
    if p.suffix.lower() == ".pdf":
        # attempt to extract text from PDF using PyMuPDF (fitz)
        text = pdf_to_text(p)
    else:
        text = read_text_file(p)
    secs = extract_sections_from_text(text)
    extraction = nlp_extractor.extract_parameters(secs.get('Methods', ''))
    nb = make_notebook_from_sections(secs, populate_code=populate_code, extraction=extraction)
    write_notebook(nb, out_path)
    # also write a sidecar JSON with the structured extraction for auditing
    sidecar = out_path.with_suffix('.extraction.json')
    sidecar.write_text(json.dumps(extraction, ensure_ascii=False, indent=2), encoding='utf-8')
    return out_path


def pdf_to_text(path: Path) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz).

    Raises ImportError if PyMuPDF is not installed. Raises FileNotFoundError
    if the PDF path does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise ImportError("PyMuPDF not available; install with 'pip install PyMuPDF' to enable PDF parsing")

    doc = fitz.open(str(p))
    parts = []
    for page in doc:
        parts.append(page.get_text())
    return "\n".join(parts)
