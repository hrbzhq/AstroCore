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


