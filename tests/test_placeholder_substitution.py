import sys
from pathlib import Path

# ensure src is on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

import unittest
from astrocore import nlp_extractor, replicator


class PlaceholderSubstitutionTests(unittest.TestCase):
    def test_data_path_and_fs_injection(self):
        methods = "We used Welch with nperseg=1024, window=hann. Data stored in data/sample.csv and sampling rate fs=500"
        sections = {'Title': 'T', 'Methods': methods}
        nb = replicator.make_notebook_from_sections(sections, populate_code=True)
        code = '\n'.join(nb['cells'][-1]['source'])
        self.assertIn("data = np.loadtxt(r'data/sample.csv')", code)
        self.assertIn('fs = 500', code)


if __name__ == '__main__':
    unittest.main()
