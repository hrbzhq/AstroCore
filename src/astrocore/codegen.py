"""Simple code generator for common analysis methods.

Generates runnable Python code snippets (as list of source lines) given
extracted parameters from `nlp_extractor`.
"""
from typing import Dict, List, Optional


def _load_data_lines(data_path: Optional[str], fs: Optional[float]) -> List[str]:
    lines = ["import numpy as np"]
    if data_path:
        lines += [f"data = np.loadtxt(r'{data_path}')  # loaded from paper-detected path"]
    else:
        lines += ["# Load your timeseries into `data` (1D numpy array) and sampling rate `fs`", "# data = np.loadtxt('path/to/data.csv')  # example placeholder"]
    if fs:
        lines += [f"fs = {int(fs)}  # detected from paper text"]
    else:
        lines += ["# fs = 1000  # sampling rate (Hz)"]
    return lines


def generate_welch_code(params: Dict, data_path: Optional[str] = None, fs: Optional[float] = None) -> List[str]:
    nperseg = params.get('nperseg', 1024)
    window = params.get('window', 'hann')
    nfft = params.get('nfft', None)
    lines = [
        "# Auto-generated Welch PSD example",
        "from scipy import signal",
        "import matplotlib.pyplot as plt",
        "",
    ]
    lines = _load_data_lines(data_path, fs) + lines[1:]

    lines += [
        "",
        f"f, Pxx = signal.welch(data, fs=fs, nperseg={nperseg}, window='{window}'{', nfft='+str(nfft) if nfft else ''})",
        "plt.semilogy(f, Pxx)",
        "plt.xlim(0, 100)",
        "plt.xlabel('Frequency (Hz)')",
        "plt.ylabel('PSD')",
        "plt.show()",
    ]
    return lines


def generate_fft_code(params: Dict, data_path: Optional[str] = None, fs: Optional[float] = None) -> List[str]:
    lines = [
        "# Auto-generated FFT example",
        "import matplotlib.pyplot as plt",
        "",
    ]
    lines = _load_data_lines(data_path, fs) + lines[1:]
    lines += [
        "# compute real FFT and frequencies",
        "fft_vals = np.fft.rfft(data)",
        "freqs = np.fft.rfftfreq(data.size, 1.0/fs) if 'fs' in globals() else np.fft.rfftfreq(data.size, 1.0)",
        "plt.plot(freqs, np.abs(fft_vals))",
        "plt.xlim(0, 100)",
        "plt.xlabel('Frequency (Hz)')",
        "plt.ylabel('Amplitude')",
        "plt.show()",
    ]
    return lines


def generate_ica_code(params: Dict, data_path: Optional[str] = None, fs: Optional[float] = None) -> List[str]:
    """Generate ICA example code. Uses mne's ICA if available, otherwise falls back to sklearn's FastICA.

    The generated code attempts to import the preferred library but does not require it at test time.
    """
    lines = [
        "# Auto-generated ICA example",
        "# Expect multichannel data shaped (n_samples, n_channels)",
        "import numpy as np",
        "",
    ]
    if data_path:
        lines += [f"data = np.loadtxt(r'{data_path}')  # loaded from paper-detected path"]
    else:
        lines += ["# data = np.loadtxt('path/to/multichannel.csv')  # shape (n_samples, n_channels)"]

    lines += [
        "# Try MNE ICA first, fallback to sklearn FastICA",
        "try:",
        "    from mne.preprocessing import ICA",
        "    use_mne = True",
        "except Exception:",
        "    from sklearn.decomposition import FastICA as ICA",
        "    use_mne = False",
        "",
        "# If data is 1D, this is a placeholder; ensure multichannel input for ICA",
        "if data.ndim == 1:",
        "    # placeholder: reshape to (n_samples, 1) or load real multichannel data",
        "    data = data.reshape(-1, 1)",
        "",
        "ica = ICA(n_components=min(data.shape[1], 20))",
        "sources = ica.fit_transform(data)",
        "# use `ica`/`sources` for artifact removal or further analysis",
    ]
    return lines


def generate_mne_pipeline_code(params: Dict, data_path: Optional[str] = None, fs: Optional[float] = None) -> List[str]:
    lines = [
        "# Auto-generated MNE analysis pipeline (high-level)",
        "# Requires `mne` installed to run this cell",
        "import mne",
        "import numpy as np",
        "",
    ]
    if data_path:
        lines += [f"# Example: load raw data from a supported format; replace with actual loader for your data",
                  f"# raw = mne.io.read_raw_fif(r'{data_path}')  # example for .fif files"]
    else:
        lines += ["# raw = mne.io.read_raw_fif('path/to/file.fif')  # replace with actual file path"]

    lines += [
        "# Basic preprocessing",
        "# raw.load_data()",
        "# raw.filter(l_freq=1., h_freq=40.)",
        "# Set montage or channel info if needed: raw.set_montage('standard_1020')",
        "# Epoching example (requires events):",
        "# events = mne.find_events(raw)",
        "# epochs = mne.Epochs(raw, events, event_id=None, tmin=-0.2, tmax=0.5, baseline=(None, 0))",
        "# evoked = epochs.average()",
        "# evoked.plot()",
    ]
    return lines


def generate_bandpass_code(bandpass, filters):
    low, high = bandpass if bandpass else (None, None)
    lines = [
        "# Auto-generated bandpass filter example",
        "from scipy import signal",
        "",
        "# data: 1D numpy array; fs: sampling rate",
    ]
    if low and high:
        lines += [
            f"b, a = signal.butter(4, [ {low}/fs, {high}/fs ], btype='bandpass')",
            "filtered = signal.filtfilt(b, a, data)",
            "# plot or continue analysis on `filtered`",
        ]
    return lines


def generate_code_from_extraction(extraction: Dict, data_path: Optional[str] = None, fs: Optional[float] = None) -> List[str]:
    """Dispatch to specific code generators based on extracted methods.

    Returns a list of source lines suitable for a single code cell in a notebook.
    """
    methods = extraction.get('methods', [])
    params = extraction.get('params', {})
    bandpass = extraction.get('bandpass')
    code_lines: List[str] = []

    # Order: Welch, FFT, ICA, MNE pipeline
    if any('Welch' == m or 'welch' == m.lower() for m in methods):
        code_lines += generate_welch_code(params, data_path=data_path, fs=fs)

    if any('FFT' == m or 'fft' == m.lower() for m in methods):
        if code_lines:
            code_lines += ['\n']
        code_lines += generate_fft_code(params, data_path=data_path, fs=fs)

    if any('ICA' == m or 'ica' == m.lower() for m in methods):
        if code_lines:
            code_lines += ['\n']
        code_lines += generate_ica_code(params, data_path=data_path, fs=fs)

    if any('MNE' == m or 'mne' == m.lower() for m in methods):
        if code_lines:
            code_lines += ['\n']
        code_lines += generate_mne_pipeline_code(params, data_path=data_path, fs=fs)

    if bandpass:
        code_lines += ['\n'] + generate_bandpass_code(bandpass, extraction.get('filters', []))

    if not code_lines:
        code_lines = ["# No automatic code generated for the extracted methods. Fill manually."]
    return code_lines
