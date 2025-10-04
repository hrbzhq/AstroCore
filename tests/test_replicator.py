import unittest
from pathlib import Path
from astrocore.replicator import generate_notebook_from_paper_file


class ReplicatorTests(unittest.TestCase):
    def test_generate_notebook_from_text(self):
        root = Path(__file__).resolve().parents[1]
        paper = root / 'data' / 'sample_paper.txt'
        out = root / 'data' / 'sample_paper.ipynb'
        if out.exists():
            out.unlink()
        generate_notebook_from_paper_file(paper, out)
        self.assertTrue(out.exists())
        content = out.read_text(encoding='utf-8')
        self.assertIn('Methods', content)
        # check the sidecar extraction JSON exists and notebook metadata contains extraction
        sidecar = out.with_suffix('.extraction.json')
        self.assertTrue(sidecar.exists())
        import json
        ex = json.loads(sidecar.read_text(encoding='utf-8'))
        self.assertIsInstance(ex, dict)
        # notebook metadata
        nb = json.loads(content)
        self.assertIn('astrocore_extraction', nb)
        # cleanup
        out.unlink()
        sidecar.unlink()


if __name__ == '__main__':
    unittest.main()
