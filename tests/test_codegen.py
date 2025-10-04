import sys
from pathlib import Path

# ensure src/ is on sys.path so tests can import the astrocore package
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import unittest
from astrocore import nlp_extractor, codegen, replicator


class CodegenTests(unittest.TestCase):
    def test_generate_welch_code(self):
        text = "We computed power spectral density using Welch's method with nperseg=2048, window=hann."
        extraction = nlp_extractor.extract_parameters(text)
        code_lines = codegen.generate_code_from_extraction(extraction)
        joined = '\n'.join(code_lines)
        self.assertIn('signal.welch', joined)

    def test_replicator_populate_code(self):
        sections = {'Title': 'T', 'Methods': "Welch with nperseg=1024 window=hann"}
        nb = replicator.make_notebook_from_sections(sections, populate_code=True)
        # last cell is code
        last = nb['cells'][-1]
        self.assertEqual(last['cell_type'], 'code')
        self.assertIn('signal.welch', '\n'.join(last['source']))

    def test_fft_ica_mne_generators(self):
        # create a fake extraction dict mimicking nlp_extractor output
        extraction = {
            'methods': ['FFT', 'ICA', 'MNE'],
            'params': {},
            'bandpass': None,
        }
        code_lines = codegen.generate_code_from_extraction(extraction, data_path=None, fs=None)
        joined = '\n'.join(code_lines)
        # check for FFT marker
        self.assertIn('np.fft', joined)
        # check for ICA marker
        self.assertIn('ICA', joined)
        # check for MNE pipeline comment
        self.assertIn('mne', joined)


if __name__ == '__main__':
    unittest.main()
