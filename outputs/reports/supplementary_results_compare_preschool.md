# Supplementary Results: Comparison with Preschool ASD Aperiodic EEG Findings

**Source analysis:** `scripts/18_compare_with_preschool_study_checks.py`  
**Reference context:** Chen et al., *Molecular Autism* — resting-state aperiodic and periodic EEG in **preschool-aged** (2–6 years) autistic children; primary group effects reported for **aperiodic offset**, not **slope/exponent**.  
**Main analysis cohort (this study):** N = 138 (ASD = 61, TD = 77) after epoch ≥ 60 and specparam QC.  
**Data tables:** `outputs/tables/compare_preschool_study/`  
**Figures:** `outputs/figures/compare_preschool_study/`

---

## Supplementary Table Summaries

### Table S-C1. Age distribution by group (`age_distribution_by_group.csv`)

| Group | n | Mean age (mo) | SD | Median | Min | Max | n (24–72 mo) | % (24–72 mo) | n ≤ 72 mo | n > 72 mo |
|-------|---|---------------|-----|--------|-----|-----|--------------|--------------|-----------|-----------|
| ASD | 61 | 85.7 | 16.9 | 85.0 | 47.0 | 131.0 | 10 | 16.4% | 10 | 51 |
| TD | 77 | 88.8 | 19.6 | 90.0 | 40.0 | 130.0 | 13 | 16.9% | 13 | 64 |
| **Combined** | **138** | **~87** | — | — | **40** | **131** | **23** | **16.7%** | **23** | **115** |

**Note:** Chen et al. sampled **2–6 years (24–72 months)**. Only **23/138 (16.7%)** participants in the present cohort fall in that window; **83.3%** are older than 72 months.

---

### Table S-C2. Group × age interactions (`age_interaction_models.csv`)

Models: `{outcome} ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs` (n = 138).  
Covariates: sex, IQ_total, usable_epochs. TD vs ASD reference: ASD.

| Outcome | Term | β | SE | *t* | *p* | 95% CI |
|---------|------|---|-----|-----|-----|--------|
| **Global exponent** | C(group)[T.TD] | −0.202 | 0.123 | −1.64 | .102 | [−0.444, 0.041] |
| | **C(group)[T.TD]:age_months** | **0.00331** | **0.00140** | **2.36** | **.020** | **[0.00054, 0.00609]** |
| **Global offset** | C(group)[T.TD] | −0.258 | 0.140 | −1.84 | .068 | [−0.535, 0.019] |
| | **C(group)[T.TD]:age_months** | **0.00375** | **0.00160** | **2.34** | **.021** | **[0.00058, 0.00692]** |

**At mean age (centered model):** exponent group effect β = 0.088, *p* = .005; offset group effect β = 0.070, *p* = .049.

**Interpretation (cautious):** Significant interactions indicate that **adjusted group differences vary across age in this cross-sectional sample**. This does **not** demonstrate developmental trajectories or causal age effects.

---

### Table S-C3. Age-stratified group effects (`age_stratified_group_effects.csv`)

Models per stratum: `{outcome} ~ C(group) + C(sex) + IQ_total + usable_epochs`.  
β = adjusted TD − ASD; unadj. = raw mean difference.

#### Global aperiodic exponent

| Age stratum | n | ASD | TD | Unadj. Δ | β (adj.) | SE | *p* | 95% CI |
|-------------|---|-----|-----|----------|----------|-----|-----|--------|
| Preschool-like (≤ 72 mo) | 23 | 10 | 13 | +0.054 | +0.055 | 0.074 | .466 | [−0.100, 0.211] |
| Older child (> 72 mo) | 115 | 51 | 64 | +0.105 | +0.076 | 0.035 | **.031** | [0.007, 0.145] |
| Tertile 1 (youngest) | 46 | 23 | 23 | +0.032 | +0.036 | 0.048 | .463 | [−0.062, 0.133] |
| Tertile 2 (middle) | 46 | 23 | 23 | +0.069 | +0.029 | 0.064 | .657 | [−0.100, 0.157] |
| Tertile 3 (oldest) | 46 | 15 | 31 | +0.188 | +0.183 | 0.059 | **.003** | [0.065, 0.301] |

#### Global aperiodic offset

| Age stratum | n | ASD | TD | Unadj. Δ | β (adj.) | SE | *p* | 95% CI |
|-------------|---|-----|-----|----------|----------|-----|-----|--------|
| Preschool-like (≤ 72 mo) | 23 | 10 | 13 | +0.012 | +0.045 | 0.065 | .496 | [−0.092, 0.183] |
| Older child (> 72 mo) | 115 | 51 | 64 | +0.048 | +0.048 | 0.041 | .246 | [−0.033, 0.129] |
| Tertile 3 (oldest) | 46 | 15 | 31 | +0.126 | +0.168 | 0.076 | **.033** | [0.014, 0.322] |

**Note:** Preschool-like stratum **n = 23** is **not** adequate to replicate or refute preschool findings; formal underpowered flags were false (both groups *n* ≥ 10), but precision remains very limited.

---

### Table S-C4. Exponent–offset joint models (`exponent_offset_joint_models.csv`)

Covariates in all models: age_months, sex, IQ_total, usable_epochs (n = 138).  
Pearson *r* (exponent, offset): overall **0.73**, ASD **0.76**, TD **0.72** (all *p* < .001; `exponent_offset_correlation.csv`).

| Model | Outcome | C(group)[T.TD] β | SE | *p* | 95% CI |
|-------|---------|------------------|-----|-----|--------|
| Exponent only | global_exponent | **0.079** | 0.031 | **.012** | [0.018, 0.140] |
| Offset only | global_offset | 0.060 | 0.035 | .095 | [−0.011, 0.130] |
| Exponent | global_exponent | **0.037** | 0.018 | **.048** | [0.0003, 0.073] |
| **+ global_offset** | | | | | |
| Offset | global_offset | −0.014 | 0.021 | .527 | [−0.056, 0.029] |
| **+ global_exponent** | | | | | |

**Summary:** The TD > ASD **exponent** effect persists after controlling for offset (*p* = .048). The **offset** group effect is not significant after controlling for exponent (*p* = .527), consistent with partially shared variance and different aperiodic dimensions emphasized in prior preschool work (offset) vs. the present primary finding (exponent).

---

### Table S-C5. QC set comparison (`qc_set_comparison.csv`)

Model: `{outcome} ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs`.

| Analysis set | Outcome | n (ASD/TD) | β (TD − ASD) | SE | *p* | 95% CI |
|--------------|---------|------------|--------------|-----|-----|--------|
| Main QC (epoch ≥ 60, specparam QC pass) | Exponent | 138 (61/77) | **0.079** | 0.031 | **.012** | [0.018, 0.140] |
| Main QC | Offset | 138 | 0.060 | 0.035 | .095 | [−0.011, 0.130] |
| Relaxed (epoch ≥ 30, specparam available) | Exponent | 145 (65/80) | **0.074** | 0.031 | **.019** | [0.012, 0.137] |
| Relaxed | Offset | 145 | 0.045 | 0.036 | .212 | [−0.026, 0.116] |

Group effects are **stable** across QC stringency; conclusions are **not** driven by excluding low-epoch subjects alone.

---

### Table S-C6. Fixed vs knee sensitivity (`fixed_vs_knee_summary.csv`)

Model: `global_exponent ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs` (n = 145 per sensitivity run).

| Freq. range | Mode | β (TD − ASD) | *p* | 95% CI | *p* < .05 |
|-------------|------|--------------|-----|--------|-----------|
| 1.0–35.0 Hz | fixed | 0.073 | **.016** | [0.014, 0.132] | Yes |
| 1.0–35.0 Hz | knee | 0.098 | .127 | [−0.028, 0.224] | No |
| 1.0–40.0 Hz | fixed | 0.078 | **.022** | [0.012, 0.145] | Yes |
| 1.0–40.0 Hz | knee | 0.126 | .076 | [−0.013, 0.264] | No |
| 2.0–35.0 Hz | fixed | 0.084 | **.029** | [0.008, 0.159] | Yes |
| 2.0–35.0 Hz | knee | 0.113 | .163 | [−0.046, 0.271] | No |
| 2.0–40.0 Hz | fixed | 0.093 | **.031** | [0.009, 0.178] | Yes |
| 2.0–40.0 Hz | knee | 0.128 | .140 | [−0.043, 0.298] | No |

**Summary:** **Fixed** aperiodic mode yields significant TD > ASD exponent effects across frequency ranges; **knee** mode shows the **same direction** but weaker evidence (0/4 knee specifications *p* < .05). Specification choice modulates inference strength but does not reverse the pattern.

---

## Discussion Drafts

### 中文：为何本研究结果与既往学龄前 ASD aperiodic 研究不完全一致？

本研究的主要发现是：在协变量校正后，**TD 儿童的 global aperiodic exponent 高于 ASD 儿童**（主分析 *p* = .012），而 **global aperiodic offset 仅呈趋势**（*p* = .095）。这一模式与 Chen 等人在 **2–6 岁学龄前** ASD 样本中报告的结论 **并不完全一致**——该研究更突出 **aperiodic offset 的组间差异**，而 **slope/exponent 未见显著组间差异**。我们并不将上述关系表述为对既往研究的“否定”，而认为两者可能反映 **不同年龄阶段、不同 aperiodic 参数维度及样本表型** 下的合理差异。

**（1）年龄阶段与样本重叠有限。** 本研究主分析队列年龄约 **40–131 个月**，仅 **23/138（16.7%）** 参与者落在与 Chen 等 **2–6 岁（≤72 个月）** 相对应的时间窗内，且该学龄前重叠子层 **n = 23**，**不能视为对学龄前研究结论的充分复现或检验**。在该子层内，exponent 的校正组效应方向与全样本一致（β ≈ 0.055），但 **不显著**（*p* = .466）。相比之下，**>72 个月** 子层（*n* = 115）效应显著（β ≈ 0.076，*p* = .031）。横断面模型中，**group × age_months 对 exponent 与 offset 的交互均显著**（*p* ≈ .020–.021），提示组间差异 **随年龄而变化**；但需强调，**横断面交互不能证明发育轨迹或因果性年龄效应**，仅支持“当前样本中组效应可能具有年龄依赖性”。

**（2）Exponent 与 offset 是相关但可区分的维度。** Exponent 与 offset 在全样本中高度相关（Pearson *r* ≈ 0.73）。在控制 offset 后，exponent 的组效应仍显著（*p* = .048）；在控制 exponent 后，offset 的组效应不再显著（*p* = .527）。这与“既往研究主要报告 offset 差异、本研究主要报告 exponent 差异”在统计结构上可以并存，而不必解释为同一假设下的直接冲突。

**（3）认知/语言表型与 QC、模型设定。** TD 组 IQ 高于 ASD 组；IQ × group 交互对 exponent 不显著（见 `iq_language_moderation_models.csv`），提示组效应并非由简单的 IQ 主效应混杂单独驱动。纳入 specparam 拟合质量指标后，group 效应量级与方向总体稳定（`qc_adjusted_models.csv`）。**Fixed** aperiodic 模式下 exponent 组效应在多种频段设定下显著；**knee** 模式方向一致但显著性较弱（4/4 fixed vs 0/4 knee，*p* < .05），属于敏感性层面的差异而非结论反转。

**（4）对 Discussion 的建议表述。** 建议在正文中写明：本研究结果与 Chen 等学龄前样本的发现 **存在差异、尚不完全一致**；可能原因包括 **发育阶段不同**（学龄前重叠子样本小且效应不精确）、**aperiodic 参数侧重点不同**（offset vs exponent）、以及 **IQ/表型与 specparam 设定** 的修饰；学龄前子层结果应作为 **探索性、低功效** 补充，而非对既往研究的直接重复检验。

---

### English: Why do our findings differ from prior preschool ASD EEG aperiodic findings?

Our primary result is a covariate-adjusted **higher global aperiodic exponent in TD than ASD** (*p* = .012), with **global aperiodic offset** showing only a **trend** (*p* = .095). This pattern is **not fully consistent with** prior work in **preschool-aged (2–6 year)** autistic children (Chen et al., *Molecular Autism*), which emphasized **group differences in aperiodic offset** rather than **slope/exponent**. We frame this as **meaningful divergence across developmental context and aperiodic parameters**, not as a simple refutation of earlier findings.

**(1) Developmental sampling and limited preschool overlap.** In the main QC cohort (*N* = 138), ages spanned **40–131 months**, with only **23 participants (16.7%)** aged **24–72 months**, overlapping the preschool window targeted by Chen et al. This **preschool-like subsample (*n* = 23*)** is **too small and imprecise to constitute an adequate replication** of preschool findings. Within that stratum, the adjusted exponent effect was in the same direction as the full sample (β ≈ 0.055) but **non-significant** (*p* = .466), whereas the **older-than-72-months** stratum (*n* = 115) showed a significant effect (β ≈ 0.076, *p* = .031). In cross-sectional models, **group × age_months interactions were significant** for both exponent and offset (*p* ≈ .020–.021), indicating that **group effects vary with age in this sample**. Importantly, **cross-sectional interactions do not establish developmental trajectories** or causal age effects.

**(2) Distinct but correlated aperiodic dimensions.** Exponent and offset were strongly correlated (*r* ≈ 0.73). The exponent group effect remained significant when controlling for offset (*p* = .048), whereas the offset group effect was **not** significant when controlling for exponent (*p* = .527). Thus, emphasis on offset in preschool work and on exponent in the present study can **coexist statistically** without requiring a single contradictory null hypothesis.

**(3) Phenotype, QC, and model specification.** Group × IQ interactions were not significant for exponent. Adjusting for specparam QC metrics did not abolish group effects. **Fixed** aperiodic mode yielded significant TD > ASD exponent effects across frequency ranges (4/4 *p* < .05), whereas **knee** mode showed the **same direction** with weaker evidence (0/4 *p* < .05).

**(4) Suggested Discussion wording.** We recommend stating that findings **differ from / are not fully consistent with** preschool reports; plausible contributors include **developmental stage** (limited preschool overlap, low power), **parameter focus** (offset vs exponent), and **phenotypic and specparam choices**; preschool-stratum results should be labeled **exploratory**, not definitive replication tests.

---

## Supplementary Figure Captions

### Figure S-C1. Age distribution (`fig_age_distribution`)

**Caption (English):** Age distribution (months) in the main analysis cohort (*N* = 138), shown separately for ASD (*n* = 61) and TD (*n* = 77). The vertical dashed line marks **72 months (6 years)**, the upper bound of the preschool age range in Chen et al. Only **23 participants (16.7%)** fell within **24–72 months**; most participants were older. Histograms are scaled as density for visual comparison between groups.

**图注（中文）：** 主分析队列（*N* = 138）按 ASD（*n* = 61）与 TD（*n* = 77）分组的年龄（月）分布。虚线标示 **72 个月（6 岁）**，对应 Chen 等学龄前研究的上限。仅 **23 名（16.7%）** 处于 **24–72 个月**；多数被试年龄更大。直方图以密度显示以便组间比较。

**File:** `outputs/figures/compare_preschool_study/fig_age_distribution` (.png / .pdf / .svg)

---

### Figure S-C2. Group × age prediction (`fig_age_interaction_exponent`, `fig_age_interaction_offset`)

**Caption (English):** **Supplementary Figure S-C2a (exponent) / S-C2b (offset).** Observed participant data (points) and OLS model predictions (lines) with **95% confidence bands** from `{outcome} ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs` (*n* = 138). Other covariates were held at sample-typical values for prediction. Significant **group × age_months** interactions (*p* ≈ .020 for exponent; *p* ≈ .021 for offset) indicate that adjusted group differences **vary across age in this cross-sectional sample**; they **do not** imply verified developmental trajectories. ASD, blue; TD, orange.

**图注（中文）：** **附图 S-C2a（exponent）/ S-C2b（offset）。** 散点为被试观测值；实线及阴影为 `{outcome} ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs`（*n* = 138）的 OLS 预测及 **95% 置信带**（其余协变量取典型值）。**group × age_months** 交互显著（exponent *p* ≈ .020；offset *p* ≈ .021），提示本横断面样本中组效应 **随年龄变化**；**不能**据此推断发育轨迹。ASD 蓝色，TD 橙色。

**Files:** `fig_age_interaction_exponent`, `fig_age_interaction_offset`

---

### Figure S-C3. Age-stratified group effects (`fig_age_stratified_effects`)

**Caption (English):** Forest plot of **adjusted TD − ASD** coefficients (95% CI) for **global aperiodic exponent** (left panel) and **global aperiodic offset** (right panel) within age strata. Strata: preschool-like (≤ 72 months, *n* = 23), older child (> 72 months, *n* = 115), and age tertiles. Models: `{outcome} ~ C(group) + C(sex) + IQ_total + usable_epochs`. Asterisks (*) mark strata flagged when either group *n* < 10 (none here); the **preschool-like stratum remains low-*n* and should not be interpreted as a definitive replication of preschool findings**. Vertical line at zero.

**图注（中文）：** 各年龄层 **global aperiodic exponent**（左）与 **offset**（右）的校正 **TD − ASD** 系数森林图（95% CI）。分层包括学龄前样层（≤72 月，*n* = 23）、大龄儿童（>72 月，*n* = 115）及年龄三分位。模型：`{outcome} ~ C(group) + C(sex) + IQ_total + usable_epochs`。**学龄前样层 *n* = 23，不能作为对学龄前文献的充分复现。** 竖线为零效应。

**File:** `fig_age_stratified_effects`

---

### Figure S-C4. Fixed vs knee sensitivity (`fig_fixed_vs_knee_effects`)

**Caption (English):** Sensitivity forest plot of **TD − ASD** coefficients (95% CI) for **global aperiodic exponent** under **fixed** (circles) vs **knee** (squares) aperiodic modes across specparam frequency ranges (*n* = 145 per fit). All models included age_months, sex, IQ_total, and usable_epochs. **Fixed** mode yielded significant effects (*p* < .05) in all four ranges; **knee** mode showed the **same positive direction** but non-significant effects in this sample. Vertical line at zero. Knee fits are supplementary; primary inference used fixed mode.

**图注（中文）：** 不同频段下 **fixed**（圆）与 **knee**（方）aperiodic 模式的 **global exponent** **TD − ASD** 系数及 95% CI（每次拟合 *n* = 145）。模型均校正 age_months、sex、IQ_total、usable_epochs。**Fixed** 模式在四个频段均 *p* < .05；**knee** 方向一致但均未达显著。竖线为零。主分析采用 fixed；knee 为敏感性分析。

**File:** `fig_fixed_vs_knee_effects`

---

## Related Supplementary Materials (not tabulated above)

| Resource | Path |
|----------|------|
| Full follow-up report | `outputs/reports/compare_with_preschool_study_checks.md` |
| IQ / language moderation | `outputs/tables/compare_preschool_study/iq_language_moderation_models.csv` |
| QC-adjusted models | `outputs/tables/compare_preschool_study/qc_adjusted_models.csv` |
| Exponent–offset scatter | `outputs/figures/compare_preschool_study/fig_exponent_offset_scatter` |

---

*Generated for manuscript supplementary materials. Numerical values match `outputs/tables/compare_preschool_study/` as of the latest run of `18_compare_with_preschool_study_checks.py`.*
