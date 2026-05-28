# Comparison with preschool ASD EEG aperiodic study

## 1. Purpose

This report compares findings from the current school-aged sample with Chen et al.'s preschool ASD resting-state EEG study (2–6 years), which reported **higher aperiodic offset** in autistic children but **no significant group difference in slope/exponent**. Our primary result is **higher global aperiodic exponent in TD than ASD** (adjusted), with offset showing a weaker trend.

## 2. Key differences in sample

| Metric | Value |
|--------|-------|
| Main QC N | 138 (ASD 61, TD 77) |
| Age range (months) | 40 – 131 |
| Subjects aged 24–72 months | 23 (16.7%) |
| Mean IQ ASD / TD | 95.0 / 113.2 |
| Missing language_score | 6 |

Chen et al. focused on **preschool (2–6 y)** children; most participants here are **older than 72 months**.

## 3. Age-related checks

- Group × age interaction for exponent p = 0.020 (significant).
- In the preschool-like subsample (≤72 months, n=23), adjusted exponent group effect p = 0.466.
- Older-child and tertile-stratified effects are in `age_stratified_group_effects.csv`.

## 4. Offset vs exponent

- Overall Pearson r(exponent, offset) = 0.727.
- After controlling for offset, exponent group effect p = 0.048.
- After controlling for exponent, offset group effect p = 0.527.

## 5. IQ and language phenotype

- See `iq_language_moderation_models.csv` and `language_missingness_and_correlations.csv`.
- IQ × group interaction terms indicate whether cognitive level moderates group differences.

## 6. QC and model specification

- Main vs relaxed QC comparison: main exponent β = 0.079, relaxed β = 0.074 (see `qc_set_comparison.csv`).
- Fixed vs knee: 4/8 sensitivity rows significant at p < .05 for exponent (mostly fixed mode; see `fixed_vs_knee_summary.csv`).

## 7. Interpretation for Discussion

### 中文草稿

本研究与既往学龄前 ASD EEG 非周期活动结果不完全一致。Chen 等（学龄前 2–6 岁）主要报告 ASD 儿童 **aperiodic offset 升高**，而 **slope/exponent 组间差异不显著**；本研究在较大年龄样本中发现 **TD 组 global aperiodic exponent 高于 ASD 组**（协变量校正后），offset 仅为趋势。补充分析显示：本队列年龄范围主要为 40–131 月，仅 23 名落在 2–6 岁区间；group × age 交互显著；学龄前样层效应方向与全样本一致或见分层表。Exponent 与 offset 相关（r ≈ 0.73），控制 offset 后 exponent 组效应 p = 0.048。IQ/语言表型调节分析见附表。加入拟合质量协变量后结论总体保持；fixed 模式组效应较 knee 更稳定。上述差异**最可能**与**年龄阶段**、**认知/IQ 表型**及 **specparam 参数维度（offset vs exponent）** 有关；学龄前重叠子样本功效有限，不宜直接等同于 Chen 等结论。

### English draft

Our findings differ from prior work in **preschool-aged** autistic children, which reported higher **aperiodic offset** but comparable **slope/exponent**. In this older sample (main N = 138), we observed higher **global aperiodic exponent in TD than ASD** after covariate adjustment, with offset effects weaker. Follow-up analyses indicated limited overlap with the 2–6 year preschool window (n = 23), a non-significant or modest group × age interaction (exponent interaction p = 0.01951730359195861), and substantial correlation between exponent and offset (r ≈ 0.73). The exponent group effect remained discernible when controlling for offset (p = 0.048). IQ/language moderation and QC-adjusted models are tabulated; **fixed** aperiodic fits showed more consistent TD > ASD exponent effects than **knee** mode. Discrepancies with Chen et al. are **most plausibly** explained by **developmental stage**, **IQ/phenotype differences**, and **distinct aperiodic parameters** (offset vs exponent), rather than a single contradictory null.

## Skipped / warnings

- None
