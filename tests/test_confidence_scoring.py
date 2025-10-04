import unittest
from pathlib import Path
import sys

# setup import path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from astrocore import nlp_extractor


class ConfidenceScoringTests(unittest.TestCase):
    def test_compute_confidence_examples(self):
        # empty -> 0.0
        self.assertAlmostEqual(nlp_extractor.compute_confidence({}), 0.0)
        # fs only -> 0.3
        self.assertAlmostEqual(nlp_extractor.compute_confidence({'fs': 1000}), 0.3)
        # fs + data_path -> 0.55
        self.assertAlmostEqual(nlp_extractor.compute_confidence({'fs': 1000, 'data_path': 'a.fif'}), 0.55)
        # all -> 1.0 (clamped)
        all_fields = {'fs':1,'data_path':'a.fif','methods':['Welch'],'bandpass':(1,40),'filters':[{'type':'lowpass','cutoff':40}]}
        self.assertAlmostEqual(nlp_extractor.compute_confidence(all_fields), 1.0)


if __name__ == '__main__':
    unittest.main()
