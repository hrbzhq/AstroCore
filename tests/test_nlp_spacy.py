import unittest
import importlib


class SpaCyIntegrationTests(unittest.TestCase):
    def test_spacy_optional(self):
        try:
            import spacy  # type: ignore
        except Exception:
            self.skipTest('spaCy not installed; skipping spaCy integration test')

        # If spaCy is installed, ensure extractor can be called without error
        rep = importlib.import_module('astrocore.nlp_extractor')
        text = "We used Welch with nperseg 512 and sampling rate fs=250"
        out = rep.extract_parameters(text)
        self.assertIn('Welch', out.get('methods', []))


if __name__ == '__main__':
    unittest.main()
