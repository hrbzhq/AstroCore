# AstroCore

English and Japanese README below. The repository contains a minimal, runnable research scaffold for extracting methods/parameters from Methods sections and generating reproducible analysis notebooks.

## English

AstroCore is a lightweight research scaffold that can:

- Parse Methods text (plain or PDF -> text) and extract common analysis methods and parameters (e.g., Welch, FFT, ICA, nperseg, window, bandpass, fs, data paths).
- Generate starter analysis code and Jupyter notebooks from extracted parameters (Welch PSD, FFT, ICA, MNE examples).
- Provide a web-based annotator for human-in-the-loop corrections (bulk edits, export Needs-Fix CSV, preview top-N problematic entries).
- Maintain an audit trail with automatic backups when saving annotated reports on the local annotator server.

Quick start (Windows PowerShell):

1. Open the project directory:

   cd "e:/tools/begin/AstroCore"

2. Run unit tests (uses standard library unittest):

   python -m unittest discover -s tests -v

3. Start the local annotator server (serves `web/annotator/` and accepts POST /save):

   python scripts/serve_annotator.py

Notes:

- Optional dependencies (install as needed): `PyMuPDF` for PDF parsing, `spacy` for improved NLP extraction, `mne` and `scikit-learn` for EEG/ICA examples.
- Fundraising pitch (draft): See `docs/fundraising_pitch_en.md` (this branch/PR includes the draft for review).
- A GitHub Actions workflow is included (`.github/workflows/ci.yml`) and runs unit tests on push and pull requests.

## Japanese (日本語)

AstroCore は、Methods セクションから解析手法やパラメータを抽出し、再現可能な解析ノートブックを生成するための軽量な研究用スキャフォールドです。

- Methods のテキスト（PDF をテキスト化したものも可）から Welch、FFT、ICA、nperseg、window、bandpass、fs、データパス等を抽出します。
- 抽出結果に基づいて Jupyter ノートブックや解析コードのスケルトンを自動生成します（Welch、FFT、ICA、MNE の例を含む）。
- Web ベースのアノテーターを提供し、人手による修正や一括操作、"Needs-Fix" CSV のエクスポート、上位 N 件のプレビューなどが可能です。
- アノテーターの保存時に自動バックアップを作成し、変更履歴を保持します。

簡単な開始手順 (Windows PowerShell):

1. プロジェクトディレクトリに移動:

   cd "e:/tools/begin/AstroCore"

2. 単体テストを実行:

   python -m unittest discover -s tests -v

3. ローカルアノテーターサーバーを起動:

   python scripts/serve_annotator.py

License, contribution guide, and more usage examples are available in the repository documentation.
# AstroCore — 工程化星形胶质细胞辅助系统研究（最小可运行脚手架）

本项目基于 `read01.txt` 的说明搭建了一个最小可运行的研究工程脚手架，目的在于：

- 捕获与解析研究说明文档（`read01.txt`）。
- 提供项目结构、简单的代码接口以便后续扩展（材料设计、监测方案、仿真与数据分析）。

包含内容：

- `src/astrocore/`：主要 Python 包，实现简单的文本解析与结构化摘要。
- `scripts/summarize_readme.py`：命令行脚本，读取 `read01.txt` 并输出结构化摘要（JSON）。
- `tests/test_parser.py`：基于 `unittest` 的基本单元测试，验证解析器能工作。
- `docs/materials_and_monitoring.md`：从 `read01.txt` 提取的关键要点摘要，作为初步文档。

快速开始（Windows PowerShell）：

1. 进入项目根目录：

   cd "e:/tools/begin/AstroCore"

2. 使用系统 Python 运行单元测试（本项目的测试仅使用标准库）：

   python -m unittest discover -v

3. 运行摘要脚本：

   python scripts/summarize_readme.py read01.txt

后续建议：

- 根据需要把 `src/astrocore` 拓展为数据分析/仿真模块（例如加入 NumPy、SciPy、nibabel、mne 等依赖）。
- 添加 CI（GitHub Actions）以在推送时自动运行测试。

CI 与 Notebook

- 我已添加一个 GitHub Actions CI 工作流（`.github/workflows/ci.yml`），在 push/PR 时运行测试。
- 一个占位 notebook 在 `notebooks/analysis_example.ipynb`，可用于后续数据分析和可视化示例。

PDF 支持

- 本项目现在支持从本地 PDF 提取文本以生成复现 notebook（需要安装 PyMuPDF）。
- 安装：

   pip install PyMuPDF

- 使用示例：

   python scripts/reproduce_from_papers.py path/to/paper.pdf out/notebook.ipynb

如果不安装 PyMuPDF，脚本会给出友好提示并建议你先将 PDF 转为纯文本后再执行。

NLP 参数提取（Methods 段解析）

- 项目添加了一个轻量级的参数抽取器 `src/astrocore/nlp_extractor.py`，用于启发式地从 Methods 段识别常见分析方法（Welch、FFT、ICA）和参数（如 `nperseg`、`window`、带通范围等）。
- 若安装 spaCy，可按需扩展为更强的语义解析器（非强制）。

代码生成器与分析示例

- 本项目现在包含更丰富的代码生成器 `src/astrocore/codegen.py`，可以基于 Methods 段自动生成下列分析代码骨架并嵌入生成的 notebook：
   - Welch PSD（已有）
   - FFT（新）
   - ICA（新）——优先使用 `mne` 的 ICA，否则回退到 `scikit-learn` 的 FastICA（运行时按需安装）
   - MNE 分析流水线示例（新）——高层次示例，展示如何在 notebook 中用 `mne` 进行滤波、分段和绘图（需要安装 `mne` 才能执行）

可选依赖

- 为获得上述全部功能，建议按需安装：
   - `PyMuPDF`：PDF 解析（pip install PyMuPDF）
   - `spacy`：改进的 NLP 抽取（pip install spacy）
   - `mne`：EEG/MEG 处理与 ICA 示例（pip install mne）
   - `scikit-learn`：作为 ICA 的回退实现（pip install scikit-learn）

运行测试

推荐使用项目根下的 Python 环境，然后运行：

```powershell
python -m unittest discover -s tests -v
```

其中 spaCy、mne 等可选依赖缺失时相关测试会被跳过或以回退实现为主，不会阻塞核心流程。


