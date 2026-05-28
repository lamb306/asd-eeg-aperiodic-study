# Methods + Results 合并稿（中文 · 与 paper_ready_v2 对齐）

**队列**：主分析 *N* = 138（ASD 61，TD 77）。  
**正文图**：`outputs/figures/paper_ready_v2/`（fig1–fig4）。  
**补充图**：`outputs/figures/extension/`、`compare_preschool_study/`、`qc_specparam_review/`。  
**需人工填写**：伦理批号、诊断流程、采集现场指令等（文中以【待补】标出）。

---

## Methods

### 2.1 被试与伦理【待补】

纳入 ASD 与典型发育（TD）儿童静息态 EEG。【待补：DSM-5 / ADOS 阈值、TD 排除标准、伦理委员会批号与知情同意。】

元数据见 `data/participants/participants.csv`。主分析在 epoch 与 specparam QC 后保留 138 人（见 `outputs/tables/sample_inclusion_flow.csv`）。

### 2.2 数据采集与预处理

- **系统**：EGI HydroCel GSN-64 1.0，NetStation `.mff`，原始 500 Hz，重采样至 250 Hz（`config/config.yaml`）。
- **条件**：睁眼静息约 5 min；参考最终为平均参考。
- **滤波**：0.5–45 Hz；50 Hz 陷波。
- **分段**：2 s 不重叠 epoch；峰峰值 > 500 µV 剔除。
- **ICA**：FastICA，`n_components = 30`（**非** 0.99）；`manual_review: false`，基于 EOG/肌电启发式自动剔除成分。主分析队列中约 43% 被试未剔除任何 ICA 成分。
- **最少 epoch**：≥ 60 个可用分段（约 120 s）进入 specparam；7 人因被试级拟合质量（无效通道比例 > 20%）排除 → **138 人**。

流水线脚本：`scripts/00`–`16`（核心分析）、`17`（稳健性/QC 随访）、`18`（学龄前文献对照）、`19`（年龄交互与 split-half）、`20`/`21`（论文图 v1/v2）。

### 2.3 功率谱与 specparam

- Welch PSD（1–40 Hz），被试内通道平均后拟合。
- **specparam**：fixed aperiodic 模式，1–40 Hz；被试级 global exponent/offset 为通道平均。
- 拟合 QC：通道 *R*² ≥ 0.90；被试无效通道比例 ≤ 20%（`fit_quality`）。

### 2.4 空间分析

- **ROI**：五区（frontal / central / temporal / parietal / occipital），`config/roi_channels.yaml`；**central 为参照**。
- **ROI 模型**：`exponent ~ group × roi + covariates + (1|subject)`，线性混合模型（`statsmodels` MixedLM，随机截距）。
- **通道**：64 通道分别 OLS；组间系数 FDR 校正（Benjamini–Hochberg，64 次检验）。

### 2.5 统计模型（主分析）

- **协变量**：age_months、sex、IQ_total、usable_epochs。
- **参照组**：ASD；`C(group)[T.TD]` = TD − ASD。
- **主效应**：OLS（`scripts/08`）。
- **稳健性**：嵌套 OLS（`scripts/17`）；频段与 fixed/knee 敏感性（`scripts/14`）。
- **周期峰**：alpha 中心频率、峰功率、带宽等（`scripts/12`）；正文 Fig 4 基于主分析 *n* = 138；历史 CSV 部分为 *n* = 145，以重跑或稿本说明为准。
- **临床（探索性）**：仅 ASD；ADOS 子分映射见 `clinical_model_n_and_variable_check.csv`（**Communication ≠ RRB**；`ADOS_RRB` 无数据）。
- **年龄交互**：`outcome ~ group × age_months + covariates`（`scripts/19`）。
- **Split-half**：奇偶 epoch 分半 → 独立 PSD → specparam（`scripts/19`）。

### 2.6 软件【待补版本号】

Python 3.x；MNE-Python、specparam、statsmodels、pandas、matplotlib 等（见 `requirements.txt`）。

---

## Results

### 3.1 样本与数据质量（Supplementary Figure：CONSORT 流程图）

168 人具备可分析数据 → 145 人 epoch ≥ 60 → **138 人**通过 specparam 被试级 QC（ASD 61，TD 77）。流程见 `outputs/figures/paper_ready_v2/supp_consort_flow_paper.png`（`python scripts/21_make_consort_flow_paper.py`）。

**Table 1**（主分析人口学）：见 `table1_main_cohort_draft_zh.md`。年龄无组间差异（*p* = 0.32）；IQ 与性别分布不同（均已在模型中校正）。

**Figure 1**（`fig1_psd_specparam_overview`）：  
- **A** 代表被试 specparam 拟合示意；  
- **B** 组平均 PSD（1–40 Hz，±1 SEM）。

---

### 3.2 主效应：global aperiodic exponent（Figure 2）

协变量校正后，TD 组 **global exponent** 高于 ASD（β = **0.079**，SE = 0.031，**p = 0.012**，95% CI [0.018, 0.140]，*n* = 138）。

未校正：ASD *M* = 1.69，TD *M* = 1.79（`global_exponent_descriptives.csv`）。较高 exponent 表示 1/f 斜率更陡；ASD 相对更平坦。

**Global offset** 呈 TD > ASD 趋势（β = 0.060，*p* = 0.095）（Fig 2B）。

**Figure 2C**：稳健性森林图——组效应方向均为 TD > ASD；主模型 + epoch 后 *p* = 0.012；加入平均 *R*² 后 β = 0.056，*p* = 0.030（`global_exponent_robustness_models.csv`）。

---

### 3.3 敏感性分析（Methods 2.5 / Supplement）

- **fixed** 模式：1–40、2–40、1–35、2–35 Hz 频段组效应一致（*p* ≈ 0.016–0.031）。
- **knee** 模式：方向相同，证据较弱（*p* ≈ 0.08–0.16）。
- 最少 epoch 阈值 30 vs 60：β ≈ 0.074，*p* ≈ 0.019。

---

### 3.4 年龄调节（Figure：extension；Supplement）

**group × age_months** 对 exponent（β_interaction = 0.0033，*p* = 0.020）与 offset（β = 0.0037，*p* = 0.021）均显著（`development_interaction_models.csv`；图 `fig_development_interaction_*`）。

**解释限制**：横断面交互仅表示组间差异随年龄变化，**不能**表述为纵向发育轨迹。

学龄前样层（≤ 72 月，*n* = 23）：exponent 组效应 *p* ≈ 0.47；> 72 月层 β ≈ 0.076，*p* ≈ 0.031（`compare_with_preschool_study_checks.md`）。

---

### 3.5 分半信度（Supplement）

奇偶 epoch split-half：Spearman ρ = 0.959（exponent）、0.960（offset）、0.972（alpha_pw）；Spearman-Brown > 0.97（`split_half_reliability.csv`；`fig_split_half_reliability`）。支持被试内 aperiodic 估计稳定性；**不能**替代跨日 test–retest。

---

### 3.6 空间分布（探索性 · Figure 3）

**ROI 混合模型**（*n*~obs = 687）：组别主效应 *p* = 0.44；**group × ROI 交互显著**（frontal / temporal / parietal / occipital vs central，交互 *p* 约 0.001–0.06）。

**Figure 3A**：各 ROI **边际** TD − ASD 对比（central 参照）。

**通道 FDR**：**E33、E36、E37、E38** 显著（顶–枕过渡 / Oz 邻近）；**Figure 3B** topomap。不作皮层来源推断。

---

### 3.7 周期峰（Figure 4A–B）

主分析队列下，alpha 峰功率（调整 *p* ≈ 0.68）、中心频率（*p* ≈ 0.26）等组别效应均不显著。组间差异主要由 **aperiodic exponent** 驱动，而非周期峰参数。

---

### 3.8 临床关联（探索性 · Figure 4C）

ASD *n* = 61。Global exponent 与 ADOS 总分、Communication 子分均无显著 OLS 关联。与 **ADOS Social（`ADOS_SA`）** 的 Spearman ρ = −0.229，*p* = 0.076（Fig 4C）。颞叶 ROI exponent 与语言分（*n* = 55）无显著关联。

---

## Discussion 要点（提纲）

1. **主发现**：学龄儿童样本中 TD > ASD 的 global exponent（1/f 更陡），与 Chen 等学龄前研究强调 **offset** 而非 slope 的模式形成对照（`supplementary_results_compare_preschool.md`）。
2. **机制假说（谨慎）**：更平坦 1/f 可能与兴奋/抑制平衡、网络时间常数或发育轨迹差异有关——需结合年龄交互与独立样本验证。
3. **年龄**：仅 16.7% 在 24–72 月；学龄前子样本未复现主效应，提示发育阶段与表型异质性。
4. **exponent–offset**：r ≈ 0.73；控制 offset 后 exponent 仍 *p* ≈ 0.048。
5. **局限**：ICA 无系统人工复核；IQ/性别/语言不均衡；横断面；SRS 仅 TD 有数据；无跨日重测。

---

## 图表对照表

| 正文 Figure | 文件 | 内容 |
|-------------|------|------|
| Fig 1 | `fig1_psd_specparam_overview` | PSD + specparam 示意 |
| Fig 2 | `fig2_main_aperiodic_effects` | exponent/offset + 稳健性 |
| Fig 3 | `fig3_spatial_distribution` | ROI 边际效应 + 通道 topomap |
| Fig 4 | `fig4_periodic_clinical_exploratory` | 周期峰 + ADOS SA 探索 |
| Supp | `extension/fig_development_interaction_*` | 年龄交互 |
| Supp | `extension/fig_split_half_reliability` | 分半信度 |
| Supp | `compare_preschool_study/*` | 与 Chen 学龄前对照 |
| Supp | `qc_specparam_review/` | 拟合 QC 代表图 |
| Supp | `supp_consort_flow_paper` | CONSORT 流程图（`scripts/21_make_consort_flow_paper.py`） |

**英文 caption 草稿**：`outputs/figures/paper_ready_v2/figure_captions.md`。

---

## 摘要句（中英文各一段 · 可直接改写入稿）

**中文**：在 138 名学龄儿童的静息态 EEG 中，specparam 显示典型发育组的全脑 aperiodic exponent 高于自闭症组（协变量校正后 *p* = 0.012），offset 仅呈趋势。组间差异随年龄变化（group×age *p* = 0.020），奇偶分半信度 > 0.95。空间上顶–枕通道 FDR 显著；周期峰参数无显著组效应。结果与学龄前文献中 offset 主导的模式不完全一致，提示非周期指标对发育阶段敏感。

**English**: In 138 school-aged children, resting-state specparam revealed higher global aperiodic exponent in TD than ASD (adjusted *p* = 0.012), with offset showing a weaker trend. Group differences varied with age (interaction *p* = 0.020), and split-half reliability exceeded ρ = 0.95. FDR-significant effects were localized to parieto-occipital channels; periodic peak parameters showed no significant group effects, contrasting with preschool reports emphasising aperiodic offset.
