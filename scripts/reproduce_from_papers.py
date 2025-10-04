#!/usr/bin/env python
"""Command-line wrapper to generate reproduction notebooks from paper text files."""
import sys
from pathlib import Path

# Ensure local src/ is on sys.path so the script works when invoked directly
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from astrocore.replicator import generate_notebook_from_paper_file


def main(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Generate reproduction notebook from paper text or PDF')
    parser.add_argument('paper', help='Path to paper text (.txt) or PDF (.pdf)')
    parser.add_argument('out', help='Output notebook path (.ipynb)')
    parser.add_argument('--populate-code', action='store_true', help='Auto-populate code cell from Methods via NLP extraction')
    parser.add_argument('--dump-extraction-only', action='store_true', help='Only extract structured parameters and write a sidecar JSON without generating a notebook')
    args = parser.parse_args(argv[1:])

    paper = Path(args.paper)
    out = Path(args.out)
    if not paper.exists():
        print(f"Paper file not found: {paper}")
        return 2

    from astrocore import nlp_extractor
    from astrocore.replicator import generate_notebook_from_paper_file

    if args.dump_extraction_only:
        text = None
        if paper.suffix.lower() == '.pdf':
            try:
                from astrocore.replicator import pdf_to_text
                text = pdf_to_text(paper)
            except Exception as e:
                print(str(e))
                return 2
        else:
            text = paper.read_text(encoding='utf-8')
        extraction = nlp_extractor.extract_parameters(text)
        sidecar = out.with_suffix('.extraction.json')
        sidecar.write_text(__import__('json').dumps(extraction, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Extraction written to: {sidecar}")
        return 0

    generate_notebook_from_paper_file(paper, out, populate_code=args.populate_code)
    print(f"Notebook written to: {out}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
