import unittest
from pathlib import Path
import sys

# setup import path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from astrocore import nlp_extractor


class SpaCyPatternsTests(unittest.TestCase):
    def test_freq_conversion(self):
        self.assertEqual(nlp_extractor._freq_to_hz('1 kHz'), 1000.0)
        self.assertEqual(nlp_extractor._freq_to_hz('2MHz'), 2e6)
    
    def test_spacy_enrich(self):
        # only run if spaCy actually available
        try:
            import spacy
        except Exception:
            self.skipTest('spaCy not installed')
        nlp = spacy.load('en_core_web_sm')
        text = "Sampling rate 1 kHz. Data saved at C:\\data\\subj1\\rec.fif"
        out = {'methods':[], 'params':{}, 'bandpass':None, 'filters':[]} 
        doc = nlp(text)
        nlp_extractor.spacy_enrich_extraction(doc, out)
        self.assertIn('fs', out)
        self.assertEqual(out['fs'], 1000.0)
        self.assertIn('data_path', out)


if __name__ == '__main__':
    unittest.main()
