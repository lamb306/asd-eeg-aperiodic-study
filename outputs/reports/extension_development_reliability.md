# Extension: Development interaction and split-half reliability

## 1. Age (development) interaction summary

**Cohort:** main QC-passed analysis set, *N* = 138.

**Models:**
- `global_exponent ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs`
- `global_offset ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs`

| Effect | Outcome | β | *p* |
|--------|---------|---|-----|
| Group × age | Exponent | 0.0033 | 0.020 |
| Group × age | Offset | 0.0037 | 0.021 |

**Caution:** Significant interactions in this **cross-sectional** sample indicate that adjusted group differences **vary with age**; they **do not** establish longitudinal developmental trajectories or causal maturational effects.

**Tables / figures:**
- `outputs/tables/extension/development_interaction_models.csv`
- `outputs/figures/extension/fig_development_interaction_exponent`
- `outputs/figures/extension/fig_development_interaction_offset`

---

## 2. Split-half reliability summary

Epochs were split into **odd** vs **even** halves per subject; each half was independently PSD-estimated (Welch) and fit with specparam (fixed aperiodic mode). Subject-level metrics were channel-averaged.

- **global_exponent**: Spearman ρ = 0.959 (p = 3.86e-76), SB(ρ) = 0.979, n = 138
- **global_offset**: Spearman ρ = 0.960 (p = 2.44e-77), SB(ρ) = 0.980, n = 138
- **alpha_pw**: Spearman ρ = 0.972 (p = 1.37e-87), SB(ρ) = 0.986, n = 138

**Tables / figures:**
- `outputs/tables/extension/split_half_subject_metrics.csv`
- `outputs/tables/extension/split_half_reliability.csv`
- `outputs/figures/extension/fig_split_half_reliability`

---

## 3. Results / Supplement — English short paragraph

**Development.** In the main cohort (*N* = 138), group × age_months interactions were significant for global aperiodic exponent (β = 0.0033, *p* = 0.020) and offset (β = 0.0037, *p* = 0.021), indicating that covariate-adjusted group differences varied across age in this cross-sectional sample. This pattern should not be interpreted as evidence for longitudinal developmental change.

**Reliability.** Split-half (odd vs even epochs) consistency was moderate-to-high for global exponent (ρ = 0.959), global offset (ρ = 0.960), and alpha peak power (ρ = 0.972), supporting stable within-subject aperiodic estimates under epoch subsampling.

---

## 4. 结果 / 补充材料 — 中文短段落

**年龄调节。** 在主分析 QC 队列（*N* = 138）中，global aperiodic exponent 与 offset 的 **group × age_months** 交互均显著（exponent 交互 *p* = 0.020；offset 交互 *p* = 0.021），提示协变量校正后的组间差异在本横断面样本中 **随年龄而变化**。需强调：该结果 **不能** 解释为纵向发育轨迹或因果性成熟效应。

**分半信度。** 将每名被试的 epochs 按奇偶分为两半并独立估计 PSD 与 specparam 后，global exponent、global offset 与 alpha peak power 的奇偶分半 Spearman 相关分别为 0.96、0.96 与 0.97（详见 split_half_reliability.csv），表明 aperiodic 指标在 epoch 子样本内具有可接受的内部一致性。
