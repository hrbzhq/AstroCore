#!/usr/bin/env python
"""Command-line utility: read a text file and print JSON summary."""
import sys
import json
from pathlib import Path
from astrocore.parser import summarize_to_json


def main():
    if len(sys.argv) < 2:
        print("Usage: summarize_readme.py <file>")
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    text = path.read_text(encoding="utf-8")
    summary = summarize_to_json(text)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
