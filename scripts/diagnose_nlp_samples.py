import sys
from pathlib import Path
# ensure local src/ is on sys.path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from astrocore.nlp_extractor import extract_parameters
import json
import argparse
import csv

BUILTIN_SAMPLES = [
    "We used Welch's method with nperseg=1024 and window='hann' and a bandpass of 1-40 Hz.",
    "Power spectra were computed (FFT) after bandpass filtering 0.5 to 30 Hz.",
    "Data were sampled at fs = 1 kHz and stored in data/subject1/session1.csv.",
    "We applied a 145 Hz band-pass (butterworth) prior to analysis.",
    "Sampling rate was 2048Hz and ICA was performed to remove artifacts.",
    "Signals were downsampled to 250 Hz (sampling rate) and then Welch nperseg: 512.",
    "EEG files at C:\\data\\subj.mat were loaded; filtering 0.1 to 100 Hz."
]


def run(samples, out_path: str = 'diagnose_report.json', fmt: str = 'json'):
    rows = []
    for s in samples:
        res = extract_parameters(s)
        rows.append({'text': s, 'extraction': res})

    if fmt == 'json':
        Path(out_path).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        # CSV: flatten extraction to JSON string in a column
        with open(out_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'extraction'])
            writer.writeheader()
            for r in rows:
                writer.writerow({'text': r['text'], 'extraction': json.dumps(r['extraction'], ensure_ascii=False)})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', help='Optional file with one sample per line')
    parser.add_argument('--out', default='diagnose_report.json', help='Output report path')
    parser.add_argument('--format', default='json', choices=['json', 'csv'], help='Output format')
    args = parser.parse_args(argv)

    samples = BUILTIN_SAMPLES
    if args.infile:
        samples = [l.strip() for l in Path(args.infile).read_text(encoding='utf-8').splitlines() if l.strip()]

    rows = run(samples, out_path=args.out, fmt=args.format)
    print(f'Wrote {len(rows)} entries to {args.out}')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
