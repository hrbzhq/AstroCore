import unittest
from pathlib import Path
import importlib


class PDFSupportTests(unittest.TestCase):
    def test_pdf_fallback_importerror(self):
        # If PyMuPDF is not installed, calling pdf_to_text should raise ImportError
        rep = importlib.import_module('astrocore.replicator')
        try:
            # If fitz is available, skip this particular assertion
            import fitz  # type: ignore
            self.skipTest('PyMuPDF is installed in this environment; skipping ImportError test')
        except Exception:
            # create a temporary empty file so pdf_to_text proceeds to import check
            tmp = Path(__file__).resolve().parents[1] / 'data' / 'tmp_test_pdf.pdf'
            try:
                tmp.write_bytes(b'%PDF-1.4\n%EOF')
                with self.assertRaises(ImportError):
                    rep.pdf_to_text(tmp)
            finally:
                if tmp.exists():
                    tmp.unlink()

    def test_generate_notebook_pdf_monkeypatch(self):
        # Monkeypatch pdf_to_text to return known text and verify notebook generation
        rep = importlib.import_module('astrocore.replicator')
        # create a temporary fake pdf path
        tmp_pdf = Path(__file__).resolve().parents[1] / 'data' / 'dummy.pdf'
        # ensure file exists
        tmp_pdf.write_text('PDF_PLACEHOLDER')

        # monkeypatch the pdf_to_text
        original = getattr(rep, 'pdf_to_text', None)
        try:
            rep.pdf_to_text = lambda p: 'Title\n\nMethods\nmonkeypatched method text'
            out = tmp_pdf.with_suffix('.ipynb')
            if out.exists():
                out.unlink()
            rep.generate_notebook_from_paper_file(tmp_pdf, out)
            assert out.exists()
            txt = out.read_text(encoding='utf-8')
            assert 'Methods' in txt
            out.unlink()
        finally:
            if original is not None:
                rep.pdf_to_text = original
            if tmp_pdf.exists():
                tmp_pdf.unlink()


if __name__ == '__main__':
    unittest.main()
