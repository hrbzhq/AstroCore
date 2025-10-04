"""Optional advanced parser using spaCy if available, otherwise raises ImportError.

This module attempts to provide a richer NLP-based extraction. It's
optional: if spaCy is not installed, callers should fall back to the
heuristic parser in parser.py.
"""
from typing import Dict

try:
    import spacy
except Exception as e:
    raise ImportError("spaCy not available; install spacy to use advanced_parser")


def parse_text_advanced(text: str) -> Dict:
    """Perform named-entity-like extraction using spaCy.

    Returns a dict similar to parser.parse_text but with possibly richer
    extracted fields.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    # Very small proof-of-concept: extract ORG/PRODUCT-like tokens as materials
    materials = []
    for ent in doc.ents:
        if ent.label_ in ("PRODUCT", "ORG", "NORP"):
            materials.append(ent.text)

    return {"materials": materials}
