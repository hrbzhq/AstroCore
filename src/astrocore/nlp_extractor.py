"""NLP parameter extractor for Methods sections.

This module provides a lightweight, dependency-free heuristic extractor for
common analysis parameters (e.g., Welch nperseg, window, bandpass ranges,
filter types). If spaCy is available, an advanced API may be used later.
"""
import re
from typing import Dict, Any

# Optional spaCy support
_SPACY_NLP = None
_HAS_SPACY = False
try:
    import spacy
    try:
        # try load small English model; may raise if not installed
        _SPACY_NLP = spacy.load('en_core_web_sm')
        _HAS_SPACY = True
    except Exception:
        try:
            # fallback to blank English model (no pretrained NER)
            _SPACY_NLP = spacy.blank('en')
            _HAS_SPACY = True
        except Exception:
            _SPACY_NLP = None
            _HAS_SPACY = False
except Exception:
    _SPACY_NLP = None
    _HAS_SPACY = False

# If spaCy is available, try to add an EntityRuler with a few helpful patterns
_SPACY_RULER = None
if _HAS_SPACY and _SPACY_NLP is not None:
    try:
        from spacy.pipeline import EntityRuler
        ruler = EntityRuler(_SPACY_NLP, overwrite_ents=False)
        patterns = []
        # token patterns: fs 1000, sampling rate 1000 Hz, or bare 1000Hz
        patterns.append({
            'label': 'SAMPLING_RATE',
            'pattern': [{'LOWER': 'fs'}, {'IS_PUNCT': True, 'OP': '?'}, {'LIKE_NUM': True}]
        })
        patterns.append({
            'label': 'SAMPLING_RATE',
            'pattern': [{'LOWER': 'sampling'}, {'LOWER': 'rate'}, {'IS_PUNCT': True, 'OP': '?'}, {'LIKE_NUM': True, 'OP': '+'}]}
        )
        # numeric token with trailing 'hz' (tokenized as separate token or part)
        patterns.append({
            'label': 'SAMPLING_RATE',
            'pattern': [{'LIKE_NUM': True}, {'LOWER': 'hz'}]
        })
        # file path like C:\data\file.fif or /data/file.fif
        patterns.append({
            'label': 'DATA_PATH',
            'pattern': [{'TEXT': {'REGEX': r".*\\\\.*\\.(csv|mat|npy|fif|edf)$"}}]
        })
        patterns.append({
            'label': 'DATA_PATH',
            'pattern': [{'TEXT': {'REGEX': r".*/.*\\.(csv|mat|npy|fif|edf)$"}}]
        })
        ruler.add_patterns(patterns)
        _SPACY_NLP.add_pipe(ruler, name='entity_ruler', first=True)
        _SPACY_RULER = ruler
    except Exception:
        _SPACY_RULER = None


def compute_confidence(out: Dict[str, Any]) -> float:
    """Compute a simple heuristic confidence in [0,1] based on which fields were found.

    Rules (simple):
    - start at 0.0
    - +0.3 if fs present
    - +0.25 if data_path present
    - +0.2 if any method detected
    - +0.15 if bandpass present
    - +0.1 if any filters present
    - clamp to 1.0
    """
    score = 0.0
    if 'fs' in out and out.get('fs'):
        score += 0.3
    if 'data_path' in out and out.get('data_path'):
        score += 0.25
    if out.get('methods'):
        if isinstance(out['methods'], (list, tuple)) and len(out['methods'])>0:
            score += 0.2
    if out.get('bandpass'):
        score += 0.15
    if out.get('filters'):
        if isinstance(out['filters'], (list, tuple)) and len(out['filters'])>0:
            score += 0.1
    if score > 1.0:
        score = 1.0
    return round(score, 3)


def _freq_to_hz(s: str) -> float:
    s = str(s).strip().lower()
    # allow things like '1 khz' or '1kHz' or '1000Hz'
    s = s.replace(' ', '')
    if s.endswith('khz'):
        return float(re.sub(r'[^0-9\.]', '', s)) * 1000.0
    if s.endswith('mhz'):
        return float(re.sub(r'[^0-9\.]', '', s)) * 1e6
    # strip non-numeric
    return float(re.sub(r'[^0-9\.]', '', s))

def extract_parameters(text: str) -> Dict[str, Any]:
    """Extract common analysis methods and parameters from given text.

    Returns a dict with keys like 'methods', 'params', 'bandpass', 'filters'.
    This is heuristic and intended to be a best-effort extractor for prototyping.
    """
    out = {
        'methods': [],
        'params': {},
        'bandpass': None,
        'filters': [],
    }

    if not text:
        return out

    lowered = text
    # normalize unicode dashes to simple hyphen for range detection
    lowered = lowered.replace('\u2013', '-').replace('\u2014', '-')

    # If spaCy model is available, we can enhance detection using tokenization
    doc = None
    if _HAS_SPACY and _SPACY_NLP is not None:
        try:
            doc = _SPACY_NLP(text)
        except Exception:
            doc = None

    # If spaCy provided a doc, attempt to enrich extraction with entity/dependency cues
    if doc is not None:
        try:
            spacy_enrich_extraction(doc, out)
        except Exception:
            # ensure spaCy enrich is best-effort and doesn't break pipeline
            pass

    # Methods detection (Welch, FFT, ICA, Welch's method)
    # handle variations like "Welch", "Welch's method", "Welch method"
    if re.search(r"\bwelch(?:'s)?(?:\s+method)?\b", lowered, flags=re.IGNORECASE):
        out['methods'].append('Welch')
    if re.search(r'\bfft\b', lowered, flags=re.IGNORECASE):
        out['methods'].append('FFT')
    if re.search(r'\bica\b', lowered, flags=re.IGNORECASE):
        out['methods'].append('ICA')
    if re.search(r'\bmne\b', lowered, flags=re.IGNORECASE):
        out['methods'].append('MNE')

    # nperseg or nperseg=2048 or nperseg : 2048
    m = re.search(r'\bnperseg\b\s*[=:\s]?\s*(\d+)', text, flags=re.IGNORECASE)
    if m:
        out['params']['nperseg'] = int(m.group(1))
    else:
        # try spaCy-based numeric proximity detection (e.g., "nperseg 1024")
        if doc is not None:
            for i, token in enumerate(doc):
                if token.text.lower().startswith('nperseg') and i + 1 < len(doc) and doc[i+1].like_num:
                    try:
                        out['params']['nperseg'] = int(float(doc[i+1].text))
                        break
                    except Exception:
                        pass

    # window=\'hann\' or window=hann or window: hann
    # window may be specified as window=hann or window: 'hann'
    m2 = re.search(r"\bwindow\b\s*[=:\s]?\s*'?([A-Za-z0-9_\-]+)'?", text, flags=re.IGNORECASE)
    if m2:
        out['params']['window'] = m2.group(1)

    # nfft
    m3 = re.search(r'\bnfft\b\s*[=:\s]?\s*(\d+)', text, flags=re.IGNORECASE)
    if m3:
        out['params']['nfft'] = int(m3.group(1))

    # bandpass ranges like 1-40 Hz or 1 to 40 Hz
    # bandpass ranges like 1-40 Hz or 1 to 40 Hz; also allow parentheses
    # handle units like kHz, Hz, and unicode dashes

    m4 = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:-|to)\s*([0-9]+(?:\.[0-9]+)?)\s*(k?m?hz|hz)?', lowered, flags=re.IGNORECASE)
    if m4:
        g1 = m4.group(1)
        g2 = m4.group(2)
        unit = m4.group(3) or ''
        # if unit provided, apply to both sides; otherwise rely on numeric
        if unit:
            unit = unit.lower()
            if 'khz' in unit:
                out['bandpass'] = (float(g1) * 1000.0, float(g2) * 1000.0)
            elif 'mhz' in unit:
                out['bandpass'] = (float(g1) * 1e6, float(g2) * 1e6)
            else:
                out['bandpass'] = (float(g1), float(g2))
        else:
            out['bandpass'] = (float(g1), float(g2))
    else:
        if doc is not None:
            # try to find pattern like "1 to 40 Hz" using tokens
            for i, token in enumerate(doc[:-2]):
                if token.like_num and doc[i+1].text.lower() in ('to', '-') and doc[i+2].like_num:
                    # check following token for Hz
                    j = i + 3
                    if j < len(doc) and doc[j].text.lower().startswith('hz'):
                        try:
                            out['bandpass'] = (float(token.text), float(doc[i+2].text))
                            break
                        except Exception:
                            pass

    # lowpass / highpass
    m5 = re.search(r'low-?pass\s*(?:[:=]\s*)?(\d+(?:\.\d+)?)\s*Hz', text, flags=re.IGNORECASE)
    if m5:
        out['filters'].append({'type': 'lowpass', 'cutoff': float(m5.group(1))})
    m6 = re.search(r'high-?pass\s*(?:[:=]\s*)?(\d+(?:\.\d+)?)\s*Hz', text, flags=re.IGNORECASE)
    if m6:
        out['filters'].append({'type': 'highpass', 'cutoff': float(m6.group(1))})

    # filter design mention
    if re.search(r'butterworth|butter\b|fir\b|iir\b', text, flags=re.IGNORECASE):
        out['filters'].append({'type': 'design_hint', 'value': re.search(r'(butterworth|butter|fir|iir)', text, flags=re.IGNORECASE).group(1)})

    # data path: enhanced heuristics for file paths ending with common extensions
    # support windows paths, unix paths, quoted paths
    m_data = re.search(r"(?P<path>['\"]?([A-Za-z]:)?[\\/\w\-\.]+\.(?:csv|mat|npy|fif|edf)['\"]?)", text, flags=re.IGNORECASE)
    if m_data:
        p = m_data.group('path')
        # strip quotes
        out['data_path'] = p.strip("'\"")
    else:
        m_data2 = re.search(r"data\s*(?:file|set)?\s*(?:[:=\-])?\s*['\"]?(?P<p>[\w\-/\\\.]+)['\"]?", text, flags=re.IGNORECASE)
        if m_data2:
            out['data_path'] = m_data2.group('p')
        # spaCy-based detection: look for token that looks like a PATH (contains '/')
        if 'data_path' not in out and doc is not None:
            for token in doc:
                if '/' in token.text and any(ext in token.text.lower() for ext in ('.csv', '.mat', '.npy', '.fif', '.edf')):
                    out['data_path'] = token.text.strip("'\"")
                    break

    # sampling rate detection: e.g., fs=1000 or sampling rate 1000 Hz
    # sampling rate detection: e.g., fs=1000, fs=1 kHz, sampling rate 1000 Hz, 1000Hz
    m_fs = re.search(r"\bfs\b\s*[=:\s]?\s*([0-9]+(?:\.[0-9]+)?\s*(?:k?m?hz|hz)?)", lowered, flags=re.IGNORECASE)
    if m_fs:
        try:
            out['fs'] = _freq_to_hz(m_fs.group(1))
        except Exception:
            out['fs'] = float(re.sub(r'[^0-9\.]', '', m_fs.group(1)))
    else:
        m_fs2 = re.search(r"sampling rate\s*(?:is|was)?\s*([0-9]+(?:\.[0-9]+)?\s*(?:k?m?hz|hz)?)", lowered, flags=re.IGNORECASE)
        if m_fs2:
            try:
                out['fs'] = _freq_to_hz(m_fs2.group(1))
            except Exception:
                out['fs'] = float(re.sub(r'[^0-9\.]', '', m_fs2.group(1)))
        # spaCy fallback: look for token 'fs' followed by numeric token
        if 'fs' not in out and doc is not None:
            for i, token in enumerate(doc[:-1]):
                if token.text.lower() == 'fs' and doc[i+1].like_num:
                    try:
                        out['fs'] = float(doc[i+1].text)
                        break
                    except Exception:
                        pass

        # regex-based fallback: number + Hz with nearby sampling/downsample keywords
        if 'fs' not in out:
            m_numhz = re.search(r"(\d+(?:\.\d+)?)\s*hz", lowered, flags=re.IGNORECASE)
            if m_numhz:
                start, end = m_numhz.span()
                ctx = lowered[max(0, start - 40): min(len(lowered), end + 40)]
                if any(k in ctx for k in ('sampling', 'sampled', 'downsampl', 'fs', 'sampling rate')):
                    try:
                        out['fs'] = _freq_to_hz(m_numhz.group(0))
                    except Exception:
                        try:
                            out['fs'] = float(re.sub(r'[^0-9\.]', '', m_numhz.group(0)))
                        except Exception:
                            pass

    # Additional spaCy-driven numeric extraction: look for patterns like 'sampling frequency 1000 Hz' or bare numbers near keywords
    if 'fs' not in out and doc is not None:
        for i, token in enumerate(doc[:-2]):
            if token.like_num and doc[i+1].text.lower() in ('hz', 'hz.', 'hz,'):
                # look backwards for 'sampling' or 'fs' within a few tokens
                window = doc[max(0, i-4):i]
                if any(t.text.lower() in ('sampling', 'rate', 'frequency', 'fs') for t in window):
                    try:
                        out['fs'] = float(token.text)
                        break
                    except Exception:
                        pass
    # compute a small heuristic confidence score if not provided
    if 'confidence' not in out:
        out['confidence'] = compute_confidence(out)

    return out


def spacy_enrich_extraction(doc, out: Dict[str, Any]):
    """Use spaCy Doc to refine numeric/path/entity extraction.

    This is best-effort: it updates `out` in-place.
    """
    # If matcher available, try pattern matches first
    try:
        from spacy.matcher import Matcher
        matcher = Matcher(doc.vocab)
        # pattern: number + (hz|kHz|MHz)
        matcher.add('FREQ_HZ', [[{'LIKE_NUM': True}, {'LOWER': {'IN': ['hz','khz','mhz']}}]])
        # pattern: number + 'Hz' attached (token may be like '1000Hz')
        matcher.add('FREQ_ATTACHED', [[{'TEXT': {'REGEX': '^[0-9]+(\\.[0-9]+)?(k|m)?hz$'}}]])
        # pattern: windows path-like token containing backslash and a known extension
        matcher.add('PATH_WIN', [[{'TEXT': {'REGEX': r"^[A-Za-z]:\\\\.*\\.(csv|mat|npy|fif|edf)$"}}]])
        # pattern: unix path
        matcher.add('PATH_UNIX', [[{'TEXT': {'REGEX': r"^/.*/.*\\.(csv|mat|npy|fif|edf)$"}}]])
        matches = matcher(doc)
        for mid, start, end in matches:
            name = doc.vocab.strings[mid]
            span = doc[start:end]
            txt = span.text
            if name in ('FREQ_HZ','FREQ_ATTACHED'):
                try:
                    out['fs'] = _freq_to_hz(txt)
                except Exception:
                    pass
            if name in ('PATH_WIN','PATH_UNIX') and 'data_path' not in out:
                out['data_path'] = txt.strip('"\'')
    except Exception:
        pass
    # Entities: look for PATH-like tokens or quoted strings
    for ent in doc.ents:
        # numeric entities
        if ent.label_ in ('CARDINAL', 'QUANTITY', 'PERCENT') and ent.text:
            # look for keyword nearby and prefer unit-aware matches
            start = max(0, ent.start - 3)
            window = doc[start:ent.end + 3]
            txt = window.text.lower()
            if 'fs' in txt or 'sampling' in txt or 'frequency' in txt:
                # if unit present in window, extract unit-aware numeric
                m_unit = re.search(r'(\d+(?:\.\d+)?\s*(?:k?m?hz|hz))', txt)
                if m_unit:
                    try:
                        out['fs'] = _freq_to_hz(m_unit.group(1))
                    except Exception:
                        pass
                else:
                    # only set bare numeric if fs not already set (don't override unit-aware)
                    if 'fs' not in out:
                        try:
                            out['fs'] = float(ent.text)
                        except Exception:
                            pass
        # path-like patterns
        if '/' in ent.text or '\\' in ent.text:
            t = ent.text.strip("'\"")
            if any(t.lower().endswith(ext) for ext in ('.csv', '.mat', '.npy', '.fif', '.edf')):
                out['data_path'] = t

    # token-based proximity: find numeric tokens followed by 'hz' or preceded by 'fs'
    for i, token in enumerate(doc[:-1]):
        if token.like_num:
            nxt = doc[i+1]
            if nxt.text.lower().startswith('hz'):
                # check left context
                left = doc[max(0, i-4):i]
                if any(t.text.lower() in ('sampling', 'rate', 'frequency', 'fs') for t in left):
                    try:
                        out['fs'] = float(token.text)
                    except Exception:
                        pass
        if token.text.lower() == 'fs' and i + 1 < len(doc) and doc[i+1].like_num:
            try:
                out['fs'] = float(doc[i+1].text)
            except Exception:
                pass


    # end of spacy_enrich_extraction
    # fallback: search the raw text for paths if none found
    if 'data_path' not in out:
        txt = doc.text
        m = re.search(r"(?P<path>['\"]?([A-Za-z]:)?[\\/\w\-\.]+\.(?:csv|mat|npy|fif|edf)['\"]?)", txt, flags=re.IGNORECASE)
        if m:
            out['data_path'] = m.group('path').strip('"\'')
