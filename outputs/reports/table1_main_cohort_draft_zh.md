# 表 1 草稿（主分析队列 · N = 138）

**纳入标准**：与脚本 08–11 一致——可用 epoch ≥ 60、通过 specparam 被试级 QC（`low_quality_subject` 排除）。  
**样本**：ASD *n* = 61，TD *n* = 77。  
**数据文件**：`outputs/tables/table1_main_cohort_descriptive.csv`、`table1_main_cohort_comparison.csv`；被试列表 `main_cohort_subject_list.csv`。

> **注意**：原 `table1_demographics_*.csv` 基于全样本 *N* = 168；正文 Table 1 请使用本表，勿混用。

---

## 表 1. 人口学与临床特征（主分析队列）

| 变量 | ASD (*n* = 61) | TD (*n* = 77) | 组间检验 *p* |
|------|----------------|---------------|--------------|
| **年龄（月）** | 85.7 ± 16.9（中位 85） | 88.8 ± 19.6（中位 90） | 0.319 |
| **IQ 总分** | 95.0 ± 15.2 | 113.2 ± 14.6 | **< 0.001** |
| **性别（女/男）** | 5 / 56 | 28 / 49 | **< 0.001**† |
| ADOS 总分‡ | 14.1 ± 3.1 | — | — |
| ADOS Social（`ADOS_SA`）‡ | 9.3 ± 2.0 | — | — |
| ADOS Communication‡ | 4.9 ± 1.3 | — | — |
| 语言分数（ToMI）§ | 12.7 ± 3.1 (*n* = 55) | 18.0 ± 1.7 | **< 0.001** |

† 卡方检验；ASD 组以男性为主，两组性别分布不均衡。主分析模型均校正性别。  
‡ 仅 ASD；来自 Resting_info（ADOS-2 / Social / Communication）。  
§ `language_score` 映射 ToMI_Total；ASD 缺失 6 例。

**正文可写一句**：两组年龄无显著差异（*p* = 0.32）；TD 组 IQ 显著高于 ASD（*p* < 0.001），所有组间模型均将 IQ_total 作为协变量。性别分布不均衡（*p* < 0.001），已在回归中校正。

---

## 表 2 补充（EEG / specparam 质量 · 同队列）

见 `outputs/tables/table2_main_cohort_eeg_qc.csv`。

| 变量 | ASD | TD | *p* |
|------|-----|-----|-----|
| 可用 epoch 数 | 120.3 ± … | 127.1 ± … | 0.152 |
| 可用记录时长（s） | 240.7 | 254.3 | 0.152 |
| 坏导数量 | 1.25 | 1.32 | 0.426 |
| 平均拟合 *R*² | 0.983 | 0.987 | **0.006** |
| 无效通道比例 | 0.057 | 0.039 | **0.045** |

**正文可写一句**：两组可用 epoch 数无显著差异；ASD 组平均 *R*²略低、无效通道比例略高（探索性，主效应模型已校正可用 epoch 数，稳健性模型另含 *R*² 与坏导数）。

---

## Word/LaTeX 粘贴用（紧凑版）

**Table 1.** Demographic and clinical characteristics of the main analysis cohort (*N* = 138; ASD = 61, TD = 77). Values are mean ± SD unless noted. Age did not differ between groups (*p* = 0.32). TD showed higher IQ (*p* < 0.001) and a higher proportion of males (*p* < 0.001; chi-square). ADOS scores are reported for ASD only. Language scores (ToMI) differed between groups (*p* < 0.001). All group comparisons of EEG outcomes adjusted for age, sex, IQ_total, and usable epochs.
