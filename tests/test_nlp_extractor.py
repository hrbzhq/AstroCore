import sys
from pathlib import Path

# ensure src/ is on sys.path so tests can import the astrocore package
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import unittest
from astrocore.nlp_extractor import extract_parameters


class NLPExtractorTests(unittest.TestCase):
    def test_extract_welch_and_params(self):
        text = "We computed power spectral density using Welch's method with nperseg=2048, window=hann and a bandpass of 1-40 Hz."
        res = extract_parameters(text)
        self.assertIn('Welch', res['methods'])
        self.assertEqual(res['params'].get('nperseg'), 2048)
        self.assertEqual(res['params'].get('window').lower(), 'hann')
        self.assertEqual(res['bandpass'], (1.0, 40.0))


if __name__ == '__main__':
    unittest.main()
