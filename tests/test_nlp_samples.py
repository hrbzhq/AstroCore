import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import unittest
from astrocore.nlp_extractor import extract_parameters


class NLPRealWorldSamplesTests(unittest.TestCase):
    def test_sample_variations(self):
        samples = [
            ("We used Welch's method with nperseg=1024 and window='hann' and a bandpass of 1-40 Hz.",
             {'methods': ['Welch'], 'params': {'nperseg': 1024, 'window': 'hann'}, 'bandpass': (1.0, 40.0)}),

            ("Power spectra were computed (FFT) after bandpass filtering 0.5 to 30 Hz.",
             {'methods': ['FFT'], 'bandpass': (0.5, 30.0)}),

            ("Data were sampled at fs = 1 kHz and stored in data/subject1/session1.csv.",
             {'fs': 1000.0, 'data_path': 'data/subject1/session1.csv'}),

            ("We applied a 1–45 Hz band-pass (butterworth) prior to analysis.",
             {'bandpass': (1.0, 45.0)}),

            ("Sampling rate was 2048Hz and ICA was performed to remove artifacts.",
             {'fs': 2048.0, 'methods': ['ICA']}),

            ("Signals were downsampled to 250 Hz (sampling rate) and then Welch nperseg: 512.",
             {'fs': 250.0, 'params': {'nperseg': 512}}),

            ("EEG files at C:\\data\\subj.mat were loaded; filtering 0.1 to 100 Hz.",
             {'data_path': 'C:\\data\\subj.mat', 'bandpass': (0.1, 100.0)})
        ]

        for text, expect in samples:
            res = extract_parameters(text)
            # ensure expected keys exist where provided
            for k, v in expect.items():
                if k == 'methods':
                    for m in v:
                        self.assertIn(m, res.get('methods', []), msg=f"text: {text}")
                elif k == 'params':
                    for p_k, p_v in v.items():
                        self.assertEqual(res.get('params', {}).get(p_k), p_v, msg=f"text: {text}")
                elif k == 'bandpass':
                    self.assertIsNotNone(res.get('bandpass'), msg=f"text: {text}")
                    self.assertAlmostEqual(res.get('bandpass')[0], v[0])
                    self.assertAlmostEqual(res.get('bandpass')[1], v[1])
                elif k == 'fs':
                    self.assertAlmostEqual(res.get('fs'), v)
                elif k == 'data_path':
                    self.assertIn(v, res.get('data_path', ''), msg=f"text: {text}")


if __name__ == '__main__':
    unittest.main()
