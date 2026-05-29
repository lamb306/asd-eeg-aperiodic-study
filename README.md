# 自闭症谱系障碍儿童静息态 EEG 非周期性成分研究

基于功率谱参数化（specparam / FOOOF）的 ASD vs TD 比较分析流水线。

**代码仓库**（NC 叙事版论文相关脚本）：<https://github.com/lamb306/asd-eeg-aperiodic-study>  
**论文稿（NC）**：`outputs/reports/manuscript_NC_revised_zh_with_figures.docx`  
**脚本清单**：`scripts/README_NC_pipeline.md`  
**补充材料说明（v11 流水线参考）**：`outputs/reports/supplementary_materials_v11/`

## 研究问题

1. ASD 与 TD 儿童静息态 EEG 的 **aperiodic exponent** 和 **aperiodic offset** 是否存在组间差异？
2. 非周期性参数在不同脑区 ROI 的空间分布如何？
3. aperiodic 参数与 ADOS、SRS、IQ、语言能力等临床变量有何关联？
4. 传统频段功率与 specparam 校正后的周期峰功率有何不同？
5. 不同频率范围、QC 标准、specparam 参数下的结果是否稳健？

## 项目结构

```
asd_eeg_aperiodic_study/
├── config/                 # 配置文件
├── data/                   # 原始数据与被试表（不纳入版本控制的大数据）
├── derivatives/            # 中间与派生数据
├── scripts/                # 分析流水线（00–16）
├── src/                    # 可复用 Python 模块
├── notebooks/              # 探索性分析
├── outputs/                # 表格、图形、报告
├── requirements.txt
└── README.md
```

## 数据准备

1. 将原始 EEG 文件放入 `data/raw/`（或在 `participants.csv` 中指定完整/相对路径）。
2. 填写 `data/participants/participants.csv`（参见下方字段说明）。
3. 根据实际电极命名检查 `config/roi_channels.yaml`。
4. 按需修改 `config/config.yaml` 中的路径与参数。

### participants.csv 字段说明

| 字段 | 说明 |
|------|------|
| `subject_id` | 被试唯一 ID |
| `group` | `ASD` 或 `TD` |
| `age_months` | 月龄 |
| `sex` | `M` / `F` |
| `IQ_total` | 总智商 |
| `IQ_verbal` / `IQ_nonverbal` | 言语/非言语智商 |
| `ADOS_total` / `ADOS_SA` / `ADOS_RRB` | ADOS 分数（TD 可留空） |
| `SRS_total` | SRS 总分 |
| `CARS_total` / `ABC_total` | 其他量表（可选） |
| `language_score` | 语言能力评分 |
| `medication_status` | 用药情况 |
| `raw_EEG_file` | 原始 EEG 相对或绝对路径 |
| `EEG_usable_seconds` / `EEG_usable_epochs` | 可用数据量（可预处理自动填写） |
| `included_final` | `1` 纳入分析，`0` 排除 |
| `exclusion_reason` | 排除原因 |

## 安装依赖

```bash
cd asd_eeg_aperiodic_study
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## 运行顺序

所有脚本从**项目根目录**运行：

```bash
python scripts/00_check_environment.py
python scripts/01_prepare_participants.py
python scripts/02_preprocess_eeg.py
python scripts/03_compute_psd.py
python scripts/04_run_specparam.py
python scripts/05_specparam_qc.py
python scripts/06_compute_roi_metrics.py
python scripts/07_demographic_and_qc_stats.py
python scripts/08_main_group_analysis.py
python scripts/09_roi_mixed_model.py
python scripts/10_channel_level_analysis.py
python scripts/11_clinical_correlation.py
python scripts/12_periodic_peak_analysis.py
python scripts/13_traditional_band_power.py
python scripts/14_sensitivity_analysis.py
python scripts/15_make_figures.py
python scripts/16_generate_report_tables.py
python scripts/17_qc_and_sensitivity_followup.py   # 样本流失、IQ 稳健性、显著通道坐标
python scripts/19_plot_specparam_qc_review.py      # 单被试 specparam 拟合 QC 图
python scripts/23_iclabel_artifact_sensitivity.py --threshold 0.80 --overwrite
```

### NC 叙事版图与稿件（Figure 1–5 + Extended Data）

在完成主分析与扩展模块（规范模型、年龄敏感性、机器学习）后：

```bash
python scripts/90_normative_exponent_analysis.py
python scripts/91_spectral_maturation_joint_model.py
python scripts/92_nonlinear_age_sensitivity.py
python scripts/25_nested_cv_aperiodic_classifier.py   # 若尚未运行
python scripts/94_nc_figures_and_manuscript.py
```

输出：`outputs/figures/nc_manuscript/`、`outputs/reports/manuscript_NC_revised_zh_with_figures.docx`

### ICLabel 伪迹控制敏感性分析

回应审稿人关于眼动/肌电残留的质疑；使用 **mne-icalabel**（非 HAPPE/MARA）。输出写入 `derivatives/*/iclabel_cleaned/` 与 `outputs/tables/iclabel_sensitivity/`，**不修改**主分析 `derivatives/preprocessed/`、`epochs/`、`specparam/`、`stats/`。

```bash
pip install mne-icalabel
python scripts/23_iclabel_artifact_sensitivity.py --threshold 0.80 --overwrite
python scripts/23_iclabel_artifact_sensitivity.py --threshold 0.80 --threshold 0.70 --overwrite
python scripts/23_iclabel_artifact_sensitivity.py --subjects S001 T002 --threshold 0.80 --overwrite
```

## 主要输出文件

| 路径 | 内容 |
|------|------|
| `derivatives/preprocessed/*-raw.fif` | 清洗后连续数据 |
| `derivatives/epochs/*-epo.fif` | 分段数据 |
| `derivatives/qc/preproc_summary.csv` | 预处理 QC 汇总（全部成功预处理者） |
| `derivatives/participants_analysis.csv` | **分析队列**（epoch ≥ 60，供 03 及之后） |
| `derivatives/qc/participants_excluded_epochs.csv` | epoch 不足、不进入分析 |
| `derivatives/psd/*_psd.csv` | 通道 PSD |
| `derivatives/specparam/specparam_channel_results.csv` | 通道级 specparam |
| `derivatives/specparam/specparam_channel_results_qc.csv` | QC 后结果 |
| `derivatives/roi/specparam_subject_global.csv` | 被试 global/ROI 指标 |
| `derivatives/stats/*.csv` | 统计结果 |
| `outputs/tables/` | 表 1、表 2 等 |
| `outputs/figures/` | 论文用图（PNG + PDF） |
| `outputs/reports/analysis_summary.md` | 分析摘要 |

## 常见问题

**Q: 运行 02 报错「EEG 文件不存在」**  
A: 检查 `participants.csv` 中 `raw_EEG_file` 路径是否正确，文件是否已放入 `data/raw/`。

**Q: specparam 拟合失败**  
A: 确认已安装 `specparam`；检查 PSD 频率范围是否覆盖 1–40 Hz；查看 `derivatives/logs/`。

**Q: ROI 结果为 NaN**  
A: 电极名与 `roi_channels.yaml` 不一致；在预处理中统一通道命名，或更新 ROI 配置。

**Q: MixedLM 报错**  
A: 脚本会自动降级为 OLS，见日志 `derivatives/logs/roi_mixed_model.log`。

## 需要人工检查的事项

1. **坏导标记**：自动坏导检测仅为模板，建议结合 Raw 波形人工复核。
2. **ICA 成分**：默认自动排除可能不完整；推荐设置 `ica.manual_review: true` 或提供 `derivatives/preprocessed/ica_labels/{subject_id}_ica.json`。
3. **ADOS 列名**：`ADOS_communication` = Resting_info 的 Communication；`ADOS_SA` = Social；勿将 Communication 称作 RRB。
3. **电极 montage**：确认通道名与 `standard_1020` 兼容。
4. **陷波频率**：国内 50 Hz，北美可改为 60 Hz（`config.yaml` → `filter.notch_hz`）。
5. **临床变量缺失**：ASD 组 ADOS/SRS 缺失会在相关分析中自动跳过。

## 引用

- MNE-Python: https://mne.tools/
- specparam: https://specparam-tools.github.io/specparam/

## 许可证

仅供科研项目内部使用；请根据数据使用协议处理受试者数据。
