# `src/` 与 `config/` 依赖清单（v11 流水线）

复现论文结果时，除 `scripts/` 外须保留下列模块（路径相对于项目根目录）。

## config/

| 文件 | 用途 |
|------|------|
| `config/config.yaml` | 路径、滤波、分段、specparam、ICA 等全局参数 |
| `config/roi_channels.yaml` | HydroCel-64 五区 ROI 电极列表 |

## src/（按功能）

| 文件 | 主要用途 |
|------|----------|
| `src/__init__.py` | 包标识 |
| `src/config.py` | 加载 YAML、日志 |
| `src/io_utils.py` | 读写 CSV、participants |
| `src/eeg_preprocessing.py` | 02 预处理 |
| `src/psd_utils.py` | 03 PSD |
| `src/specparam_utils.py` | 04–05 specparam |
| `src/roi_utils.py` | 06 ROI 聚合 |
| `src/qc_utils.py` | QC 规则 |
| `src/stats_utils.py` | 07–12 回归与组比较 |
| `src/plotting_utils.py` | 通用作图 |
| `src/extension_analysis.py` | 19 年龄交互、split-half |
| `src/preschool_study_comparison.py` | 18 频段 / knee / 分层 |
| `src/iclabel_sensitivity.py` | 23 ICLabel 分支 |
| `src/paper_figures.py` | 07b、旧版图 |
| `src/paper_figures_v2.py` | 21 v2 论文图 |
| `src/consort_flowchart_paper.py` | 21 CONSORT 图 |
| `src/consort_flowchart.py` | 22 流程图（若使用） |

`25_nested_cv_aperiodic_classifier.py` 与 `28_plot_ml_publication_figures.py` 以 sklearn 为主，主要依赖 `outputs/tables/resting_features_locked.csv`（由 26 生成）。

## 数据与中间结果（运行后生成）

| 路径 | 说明 |
|------|------|
| `data/participants/participants.csv` | 被试元数据（需自备） |
| `derivatives/` | 预处理、PSD、specparam、stats |
| `outputs/tables/`, `outputs/figures/` | 论文表图 |

课程提交若无法提供原始 EEG，可仅提交脚本 + 已有 `derivatives/`/`outputs/` 统计结果以证明可复现性。
