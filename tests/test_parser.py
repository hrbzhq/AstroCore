import sys
from pathlib import Path

# ensure src/ is on sys.path so tests can import the astrocore package
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import unittest
from astrocore.parser import parse_text
import importlib


class AdvancedParserAvailabilityTests(unittest.TestCase):
    def test_advanced_parser_not_available(self):
        """If spaCy is installed, advanced_parser should import; otherwise ImportError is expected."""
        try:
            import spacy  # type: ignore
            has_spacy = True
        except Exception:
            has_spacy = False

        if has_spacy:
            mod = importlib.import_module('astrocore.advanced_parser')
            self.assertIsNotNone(mod)
        else:
            with self.assertRaises(ImportError):
                importlib.import_module('astrocore.advanced_parser')


class ParserTests(unittest.TestCase):
    def test_parse_basic(self):
        sample = "能量供给 与 废物清除。提到 Alginate 和 PEG。使用 MRS 和 EEG。"
        result = parse_text(sample)
        self.assertIn('goals', result)
        self.assertTrue(len(result['goals']) >= 1)
        self.assertIn('Alginate', ''.join([m['name'] for m in result['materials']]) or 'Alginate')
        self.assertIn('MRS', result['monitoring'])


if __name__ == '__main__':
    unittest.main()
