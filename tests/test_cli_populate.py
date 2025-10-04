import sys
from pathlib import Path

# ensure src on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

import unittest
import subprocess
import json


class CLIPopulateTests(unittest.TestCase):
    def test_cli_populate_creates_code(self):
        paper = ROOT / 'data' / 'sample_paper.txt'
        out = ROOT / 'data' / 'sample_cli_populate.ipynb'
        if out.exists():
            out.unlink()
        # call the CLI script via python
        cmd = [sys.executable, str(ROOT / 'scripts' / 'reproduce_from_papers.py'), str(paper), str(out), '--populate-code']
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(out.exists())
        nb = json.loads(out.read_text(encoding='utf-8'))
        last = nb['cells'][-1]
        self.assertEqual(last['cell_type'], 'code')
        # should contain either placeholder or generated signal.welch
        self.assertTrue(any('signal.welch' in s for s in last['source']) or any('data' in s for s in last['source']))
        out.unlink()


if __name__ == '__main__':
    unittest.main()
