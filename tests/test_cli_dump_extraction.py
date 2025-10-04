import sys
import subprocess
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

class CLIDumpExtractionTests(unittest.TestCase):
    def test_dump_extraction_only(self):
        paper = ROOT / 'data' / 'sample_paper.txt'
        out = ROOT / 'data' / 'sample_cli_dump.ipynb'
        if out.exists():
            out.unlink()
        sidecar = out.with_suffix('.extraction.json')
        if sidecar.exists():
            sidecar.unlink()

        cmd = [sys.executable, str(ROOT / 'scripts' / 'reproduce_from_papers.py'), str(paper), str(out), '--dump-extraction-only']
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(sidecar.exists())
        import json
        ex = json.loads(sidecar.read_text(encoding='utf-8'))
        self.assertIsInstance(ex, dict)
        # cleanup
        sidecar.unlink()

if __name__ == '__main__':
    unittest.main()
