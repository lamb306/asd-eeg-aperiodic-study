# 学龄儿童静息态 EEG 非周期 1/f 参数的组间差异：一项基于 specparam 的横断面研究

> **稿件状态**：中文初稿 v1（基于项目流水线已完成的分析与图表；2026-05-20）  
> **主分析队列**：*N* = 138（ASD 61，TD 77）  
> **数据与脚本**：`config/config.yaml`；`scripts/00`–`21`；结果表见 `outputs/tables/`、`derivatives/stats/`

---

## 摘要

**背景**  
静息态脑电功率谱中的非周期（aperiodic）1/f 成分反映神经兴奋–抑制平衡与时间常数等生理特征，近年与自闭症谱系障碍（ASD）相关研究增多。谱参数化（specparam）可将 1/f 背景与周期振荡峰分离。既往部分学龄前样本报告 ASD 组 aperiodic offset 升高而 exponent（斜率）组间差异不显著；学龄儿童样本、严格质量控制下的 exponent 组效应及其稳定性尚待系统报告。

**方法**  
采用 EGI HydroCel-64 通道静息态睁眼 EEG（[待补充：采集场所、指令、伦理批号]）。经标准预处理、ICA 自动伪迹剔除与 2 s 分段后，对可用 epoch ≥ 60 的被试进行 Welch PSD 与 specparam（fixed aperiodic，1–40 Hz）拟合。主分析在 specparam 被试级 QC 后纳入 138 人。以 global aperiodic exponent 为主要结局，global offset 为次要结局；协变量包括年龄、性别、IQ 及可用 epoch 数。补充分析包括 ROI/通道空间分布、周期峰参数、年龄×组别交互、奇偶 epoch 分半信度及与学龄前文献对照的探索性分析。

**结果**  
协变量校正后，典型发育（TD）组 global exponent 高于 ASD 组（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]；未校正：ASD *M* = 1.69，*SD* = 0.14；TD *M* = 1.79，*SD* = 0.14）。Global offset 呈 TD > ASD 趋势（β = 0.060，*p* = 0.095）。fixed 模式多频段敏感性分析方向一致（*p* = 0.016–0.031）；knee 模式方向相同但证据较弱（*p* ≈ 0.08–0.16）。组别×年龄对 exponent（β = 0.0033，*p* = 0.020）与 offset（β = 0.0037，*p* = 0.021）交互显著。64 通道 FDR 校正后 E33、E36、E37、E38 显著（TD > ASD），分布于顶–枕部 HydroCel-64 电极位置。周期峰参数组间主效应均不显著（所有 group *p* > 0.24）。ASD 内临床关联未达显著（ADOS 社交子分 OLS *p* = 0.057，Spearman *p* = 0.076）。奇偶分半 Spearman ρ：global exponent 0.959（SB = 0.979），global offset 0.960（SB = 0.980），alpha 峰功率 0.972（SB = 0.986）。

**结论**  
本队列中学龄儿童 ASD 与 TD 的静息态 1/f 背景差异主要体现在 exponent（斜率更平坦）而非周期 alpha 峰；效应在协变量与多频段敏感性分析中方向稳定，但受 IQ 与性别组间不均衡、横断面设计及空间探索性分析等限制。组间差异随年龄变化，不宜直接解释为纵向发育效应。

**关键词**  
[待补充]；静息态脑电；非周期成分；specparam；自闭症；1/f 噪声；exponent

---

## 引言

静息态 EEG 功率谱在宽频段上常呈现 1/f 型非周期衰减，其斜率（exponent）与截距（offset）反映不同的神经生理过程。与传统频段功率或单一 alpha 峰指标相比，specparam 等谱分解方法可将非周期背景与周期振荡分离，有助于减少周期成分对组间比较的混杂。

自闭症谱系障碍的静息态 EEG 研究历史上关注频带功率、连接性与熵等指标；关于非周期参数的报告相对较新。已有学龄前样本研究发现，ASD 儿童 aperiodic offset 可能升高，而 exponent 组间差异不显著，提示不同发育阶段或指标维度上的效应可能并不一致。然而，针对学龄儿童、在统一预处理与拟合 QC 标准下的 exponent 主效应、空间分布、协变量稳健性以及测量信度的综合报告仍相对有限。

本研究利用 EGI HydroCel-64 静息态睁眼 EEG 数据，在预设流水线（预处理、ICA、分段、PSD、specparam、QC）基础上，以 global aperiodic exponent 为主要结局，系统检验 ASD 与 TD 的组间差异，并报告 offset、空间分布、周期峰参数、年龄交互、分半信度及临床探索性关联。研究目的为：（1）在协变量校正后评估组间 exponent 差异；（2）检验结果对模型设定与频段的稳健性；（3）描述空间分布探索性模式；（4）区分非周期与周期峰贡献；（5）评估 epoch 分半一致性。本文不旨在建立临床诊断工具，亦不对皮层源定位作推断。

---

## 方法

### 研究设计与伦理

本研究为横断面观察性设计，比较 ASD 与 TD 儿童的静息态 EEG 非周期参数。[待补充：研究机构名称]。[待补充：伦理委员会全称及批准号]。[待补充：知情同意程序（儿童/监护人）]。

### 被试

**纳入与分组**  
[待补充：ASD 诊断标准（如 DSM-5）、诊断工具（如 ADOS-2 阈值）、评估者资质]。[待补充：TD 组纳入与排除标准（发育史、共病、家族史等）]。[待补充：年龄纳入范围及招募渠道]。

元数据来自 `data/participants/participants.csv`。具备可分析静息态 EEG 及配套人口学/临床变量的初始样本共 **168** 人（ASD 80，TD 88）。

**样本流失与主分析队列**  
经预处理后，**145** 人达到可用 epoch ≥ 60（2 s 分段）；**23** 人因可用 epoch < 60 排除（145 人：ASD 65，TD 80）。另有 **7** 人因 specparam 被试级 QC 未通过（无效通道比例 > 20%）排除，主分析 **138** 人（ASD 61，TD 77）。流程见图 S1（`outputs/figures/paper_ready_v2/supp_consort_flow_paper.png`；`outputs/tables/sample_inclusion_flow.csv`）。

**人口学与临床特征（主分析队列）**  
两组年龄（月）无显著差异（ASD 85.7 ± 16.9，TD 88.8 ± 19.6，*p* = 0.319）。TD 组 IQ 总分高于 ASD（95.0 ± 15.2 vs 113.2 ± 14.6，*p* < 0.001）。性别分布不均衡（ASD 女/男 56/5，TD 49/28，*p* = 0.0003），所有组间模型均校正性别与 IQ。ADOS 与语言分数仅 ASD 有临床意义（见 `outputs/tables/table1_main_cohort_*.csv`；`clinical_model_n_and_variable_check.csv`）。`ADOS_communication` 对应 Resting_info 的 Communication 子分，**非** ADOS RRB 域；`ADOS_RRB` 在本数据中无有效值。

### EEG 采集

[待补充：实验室环境、静息指导语、屏幕/玩具、阻抗标准、记录时长现场执行细节]。

依据 `config/config.yaml` 已记录参数：EGI HydroCel GSN-64 1.0；NetStation `.mff` 格式；原始采样率 500 Hz；记录时长约 300 s；**睁眼静息**；原始参考 Cz（VREF）；保留头皮电极 E1–E64。

### 预处理

使用 MNE-Python 流水线（`scripts/01`–`04`）：重采样至 250 Hz；0.5–45 Hz 带通；50 Hz 陷波；平均参考；2 s 不重叠 epoch；峰峰值振幅 > 500 µV 的 epoch 剔除。

**ICA**  
FastICA，`n_components = 30`；`manual_review = false`，采用基于 EOG/肌电特征的自动成分剔除。**未进行系统性的逐被试人工 ICA 复核**（见局限）。主分析队列中约 43% 被试 ICA 剔除成分为 0。

### 功率谱与 specparam

**PSD**  
Welch 方法，1–40 Hz（`scripts/05`–`06`）；被试内各通道 PSD 用于后续拟合。

**specparam 拟合**（`scripts/06`）  
- 模式：**fixed** aperiodic（主分析）；敏感性分析含 **knee** 模式（`scripts/14`）。  
- 拟合频段：1–40 Hz（主分析）；敏感性含 2–40、1–35、2–35 Hz。  
- 峰宽、最大峰数等见 `config/config.yaml`。  
- 被试级 **global exponent / offset**：通过 QC 的通道上 exponent/offset 的算术平均。

**拟合与纳入 QC**  
- 通道级：拟合 *R*² ≥ 0.90；exponent 在预设生理范围内。  
- 被试级：无效通道比例 ≤ 20% 纳入主分析；否则标记为 `low_quality_subject` 并排除。  
- 主分析队列两组平均拟合 *R*² 均 > 0.98（ASD 略低于 TD，*p* = 0.006；已作稳健性检验）。

### 结局指标

| 类型 | 指标 |
|------|------|
| 主要 | 被试级 global aperiodic exponent |
| 次要 | 被试级 global aperiodic offset |
| 探索性 | ROI/通道 exponent；周期峰（alpha_cf、alpha_pw、alpha_bw 等）；临床关联 |

### 空间分析

**ROI**  
按 `config/roi_channels.yaml` 将 64 电极分为 frontal、central（参照）、temporal、parietal、occipital 五区。

**ROI 混合模型**（`scripts/09`）  
`exponent ~ C(group) × C(roi) + age_months + C(sex) + IQ_total + usable_epochs + (1|subject)`，线性混合模型（MixedLM），被试随机截距；报告组别主效应、交互效应及相对 central 的边际 TD−ASD 对比（Figure 3A）。

**通道水平**（`scripts/10`）  
64 个通道分别拟合与主分析相同协变量的 OLS；对组间系数进行 Benjamini–Hochberg FDR 校正（64 次检验）。Topomap **仅表示电极位置的系数分布，不作皮层源定位推断**。

### 统计检验

**主分析**（`scripts/08`）  
`global_exponent ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs`（OLS）；参照组为 ASD，`C(group)[T.TD]` 表示 TD 相对 ASD 的增量。`global_offset` 采用相同模型。显著性水平 α = 0.05（双侧）。

**稳健性**（`scripts/17`）  
嵌套模型：仅组别；+ 年龄/性别；+ IQ；+ 可用 epoch（主模型）；+ 平均拟合 *R*²；+ 坏导数量。

**敏感性**（`scripts/14`）  
不同拟合频段、fixed/knee 模式、最少 epoch 阈值（30 vs 60）。

**周期峰**（`scripts/12`）  
`alpha_cf`、`alpha_pw`、`alpha_bw` 及 theta/beta 峰功率等，模型协变量同主分析；正文 Figure 4 基于主分析 *n* = 138。

**年龄交互**（`scripts/19`）  
`outcome ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs`。

**分半信度**（`scripts/19`）  
每名被试 epoch 按奇偶分为两半，独立估计 PSD 与 specparam，计算被试级指标的 Spearman 相关及 Spearman–Brown 校正。**该程序评估单次记录内的 epoch 子样本一致性，不是跨日 test–retest 重测信度。**

**临床探索**（`scripts/11`）  
仅 ASD（*n* = 61）；OLS 与 Spearman 相关 global exponent 与 ADOS 总分、`ADOS_SA`（Social）、`ADOS_communication`、颞叶 ROI exponent 与 `language_score`（*n* = 55）。

### 软件

Python 3；MNE-Python ≥ 1.6；specparam ≥ 2.0.0rc6；statsmodels ≥ 0.14；pandas、SciPy、matplotlib 等（`requirements.txt`）。[待补充：各库具体版本号与运行环境记录]。

---

## 结果

### 样本与数据质量

初始可分析样本 168 人（ASD 80，TD 88）。epoch ≥ 60 后 145 人（ASD 65，TD 80）；specparam QC 后主分析 138 人（ASD 61，TD 77）（补充图 S1）。

主分析队列年龄范围约 40–131 月（`compare_with_preschool_study_checks.md`）。组平均 PSD 与代表被试 specparam 拟合见图 1。肉眼 QC 见 `outputs/figures/qc_specparam_review/`。

### 主要结局：global aperiodic exponent

协变量校正后，TD 组 global exponent 高于 ASD（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]，*n* = 138）（图 2A；`derivatives/stats/main_group_analysis.csv`）。

未校正描述统计：ASD *M* = 1.69，*SD* = 0.14；TD *M* = 1.79，*SD* = 0.14（`global_exponent_descriptives.csv`）。

### 次要结局：global aperiodic offset

TD 组 offset 高于 ASD 的趋势（β = 0.060，*p* = 0.095，*n* = 138）（图 2B）。

### 稳健性与敏感性

**协变量嵌套模型**（图 2C；`global_exponent_robustness_models.csv`）：各模型 TD > ASD 方向一致；仅组别 β = 0.096，*p* < 0.001；主模型（+ epoch）β = 0.079，*p* = 0.012；+ 平均 *R*² 后 β = 0.056，*p* = 0.030；+ 坏导 β = 0.081，*p* = 0.011。主分析队列无 IQ < 70 被试。

**频段与 aperiodic 模式**（`sensitivity_analysis_final.csv`）：fixed 模式下 1–40、2–40、1–35、2–35 Hz 组效应 *p* = 0.016–0.031；knee 模式方向一致，*p* ≈ 0.08–0.16。最少 epoch 阈值 30 与 60 时 β ≈ 0.074，*p* ≈ 0.019。

### 年龄×组别交互

`group × age_months` 对 global exponent（β = 0.0033，*p* = 0.020）与 global offset（β = 0.0037，*p* = 0.021）均显著（*n* = 138；`development_interaction_models.csv`；补充图：年龄交互）。

≤ 72 月龄亚组 *n* = 23（16.7%），该层 exponent 组效应 *p* ≈ 0.47；> 72 月龄层 β ≈ 0.076，*p* ≈ 0.031（探索性分层，`scripts/18`）。

### 分半信度

奇偶 epoch 分半（*n* = 138）：global exponent Spearman ρ = 0.959，SB = 0.979；global offset ρ = 0.960，SB = 0.980；alpha 峰功率（alpha_pw）ρ = 0.972，SB = 0.986（`split_half_reliability.csv`；补充图：分半信度）。

### 空间分布（探索性）

**ROI 混合模型**（*n*~obs = 687）：组别主效应 *p* = 0.44；组别×ROI 交互显著（frontal、temporal、parietal、occipital 相对 central，交互项 *p* 约 0.001–0.06）（`roi_mixed_model.csv`；图 3A 为边际 TD−ASD 效应）。

**通道 FDR**：E33、E36、E37、E38 在 FDR *q* < 0.05 下显著，方向均为 TD > ASD（`significant_channels_fdr.csv`；图 3B）。按 HydroCel-64 布局，上述电极位于顶–枕过渡及枕区附近。**Topomap 仅反映电极水平效应，不作皮层源定位推断。**

### 周期峰参数

在主分析队列（*n* = 138）中，alpha 峰功率（协变量校正 group *p* ≈ 0.68）、alpha 中心频率（*p* ≈ 0.26）等周期峰指标组间差异均不显著。`periodic_peak_analysis.csv` 中所有 group 项 *p* > 0.24。theta、beta 峰功率组间主效应亦不显著（图 4A–B）。

### 临床关联（探索性；仅 ASD）

* n* = 61。Global exponent 与 ADOS 总分（OLS *p* = 0.188；Spearman *p* = 0.143）、`ADOS_communication`（OLS *p* = 0.257）均无显著关联。  
* `ADOS_SA`（Social 子分）与 global exponent：OLS *p* = 0.057；Spearman ρ = −0.229，*p* = 0.076（图 4C）。  
* 颞叶 ROI exponent 与 `language_score`（*n* = 55）：OLS *p* = 0.319。  
* 上述分析均为探索性，未校正多重比较。

---

## 讨论

### 主要发现概括

本研究在 specparam QC 后的 138 名学龄儿童样本中，发现协变量校正后 TD 组 global aperiodic exponent 高于 ASD 组，提示 ASD 静息态 1/f 背景相对**更平坦**（高频相对低频衰减更缓）。该效应在协变量嵌套模型与 fixed 模式多频段敏感性分析中方向一致；global offset 仅呈较弱趋势。周期峰参数未见显著组间差异，支持组间差异主要由**非周期 exponent** 而非 alpha 周期成分驱动的分解结果。

### 与 exponent 和 offset 文献的关系

项目内探索性对照显示，global exponent 与 offset 相关约 *r* = 0.73；控制 offset 后 exponent 组效应仍 *p* ≈ 0.048，而控制 exponent 后 offset 组效应不显著（`scripts/18`）。这与既往部分学龄前样本强调 **offset** 升高而 **exponent** 不显著的报告并不完全一致，但本样本年龄范围更广（约 40–131 月），且仅约 16.7% 被试落在 24–72 月学龄前区间，学龄前亚组内 exponent 组效应不显著（*p* ≈ 0.47）。因此，不宜简单断言“矛盾”，更审慎的表述是：**非周期指标的表现可能随发育阶段与样本年龄结构而变化**。[待补充：Chen 等学龄前研究的完整文献信息]

### 年龄交互的含义

组别×年龄交互显著，提示在控制协变量后，组间 exponent/offset 差异的幅度随年龄而变化。必须强调：本研究为**横断面**设计，该交互**不能**解释为个体纵向发育轨迹或成熟因果效应，亦不能替代纵向追踪数据。

### 空间探索性结果

ROI 交互与顶–枕通道 FDR 显著均属探索性，且基于电极空间布局。后部效应可能与视觉–注意网络、alpha 相关头皮活动或参考/容积传导等因素有关；**在没有源定位与多模态证据的情况下，不应将 E37 等电极位置直接表述为“枕叶皮层异常”**。

### 临床关联

ASD 子样本内未见 exponent 与 ADOS 总分或 Communication 的显著关联；Social 子分仅呈趋势。考虑到样本量、探索性分析及临床测量与 EEG 指标的时间对齐局限，**不能**据此否定生物学关联，亦**不能**声称 exponent 可作为症状严重程度生物标志物。

### 信度

奇偶分半相关高，说明在单次记录内 epoch 子样本上 aperiodic 估计较稳定。需再次明确：该指标**不是**跨日 test–retest 重测信度，对外部推广至不同日、不同状态记录时应谨慎。

### 方法学优势与不足

优势包括：预注册式流水线文档、统一 specparam QC、主效应稳健性与敏感性报告、周期与非周期分离。  
不足见下节。

---

## 局限

1. **横断面设计**：无法推断发育因果；年龄交互仅反映组间差异随年龄的变化模式。  
2. **组间协变量不均衡**：TD 组 IQ 显著高于 ASD（*p* < 0.001），虽已纳入协变量，残余混杂仍可能存在；主分析无 IQ < 70 被试，结论不能推广至智力显著受损亚群。  
3. **性别分布不均衡**：ASD 组男性比例远低于 TD，虽已校正，残余影响不能排除。  
4. **ICA 与伪迹**：自动 ICA，无系统人工复核；约半数被试未剔除任何 ICA 成分，伪迹控制可能不足。  
5. **诊断与临床数据**：[待补充：诊断流程细节]；`ADOS_communication` 非标准 RRB；SRS 等变量在 ASD 中缺失，无法检验。  
6. **采集信息缺失**：[待补充：环境、指令、药物、共病、睡眠与行为状态]。  
7. **空间推断**：电极 topomap 与 ROI 不能用于皮层源定位。  
8. **多重比较**：通道 FDR、临床探索性分析等需按探索性解读。  
9. **重测信度**：无跨日 test–retest。  
10. **因果与机制**：EEG 1/f 与兴奋–抑制平衡的关系为间接推断，需实验与动物模型验证。

---

## 结论

在通过严格 epoch 与 specparam QC 的 138 名学龄儿童静息态 EEG 样本中，TD 组 global aperiodic exponent 显著高于 ASD 组，ASD 表现为更平坦的 1/f 背景；global offset 仅呈趋势。效应在 fixed 模式多频段敏感性分析中方向一致，奇偶 epoch 分半信度高。组间差异随年龄变化，周期峰参数未见显著组间差异，后部电极探索性显著。结果支持在学龄阶段进一步区分非周期 exponent 与 offset，并在年龄匹配、协变量均衡的独立样本中复现；**不宜**将本研究单一指标用于临床诊断，**不宜**将横断面年龄交互表述为发育轨迹，**不宜**将电极水平效应解释为皮层源异常。

---

## 图表清单

### 正文图（`outputs/figures/paper_ready_v2/`）

| 编号 | 文件名 | 内容 |
|------|--------|------|
| 图 1 | `fig1_psd_specparam_overview` | A：代表被试 PSD 与 specparam 拟合；B：组平均 PSD（±1 SEM） |
| 图 2 | `fig2_main_aperiodic_effects` | A：global exponent；B：global offset；C：稳健性森林图 |
| 图 3 | `fig3_spatial_distribution` | A：ROI 边际 TD−ASD；B：通道 topomap（FDR 显著 E33/E36/E37/E38） |
| 图 4 | `fig4_periodic_clinical_exploratory` | A–B：alpha 峰功率/中心频率；C：ASD 内 exponent vs ADOS_SA |

### 补充图

| 编号 | 路径 | 内容 |
|------|------|------|
| 图 S1 | `supp_consort_flow_paper` | CONSORT 样本纳入流程 |
| 图 S2 | `extension/fig_development_interaction_exponent` | 年龄×组别（exponent） |
| 图 S3 | `extension/fig_development_interaction_offset` | 年龄×组别（offset） |
| 图 S4 | `extension/fig_split_half_reliability` | 奇偶分半信度 |
| 图 S5+ | `compare_preschool_study/` | 与学龄前文献对照（分层、offset–exponent 等） |
| 图 S6+ | `qc_specparam_review/` | specparam 拟合 QC 示例 |

### 表

| 编号 | 文件 | 内容 |
|------|------|------|
| 表 1 | `table1_main_cohort_descriptive.csv` 等 | 主分析队列人口学/临床（*N* = 138） |
| 表 2 | `table2_main_cohort_eeg_qc.csv` | EEG/specparam 质量组间比较 |
| 表 S1 | `sample_inclusion_flow.csv` | 各阶段样本量 |
| 表 S2 | `global_exponent_robustness_models.csv` | 稳健性模型系数 |
| 表 S3 | `sensitivity_analysis_final.csv` | 频段/模式敏感性 |
| 表 S4 | `development_interaction_models.csv` | 年龄交互模型 |
| 表 S5 | `split_half_reliability.csv` | 分半信度 |
| 表 S6 | `significant_channels_fdr.csv` | FDR 显著通道 |
| 表 S7 | `roi_mixed_model.csv` | ROI 混合模型（节选） |

**图注草稿**：`figure_captions.md`（英文）、`supp_consort_flow_caption.md`。

---

## 附录：尚需人工补充的信息清单

撰写与投稿前，请由作者补充或核对下列条目（文中已标 [待补充] 者）：

| 类别 | 待补充内容 |
|------|------------|
| **伦理与法律** | 伦理委员会全称、批准号、知情同意类型与日期 |
| **诊断与招募** | ASD/TD 诊断标准与工具、评估者、排除标准、招募时间与地点 |
| **采集** | 实验室环境、指导语、注视点、阻抗阈值、是否允许药物/共病记录 |
| **人口学** | 种族/民族、 handedness、共病、家族史（若未录入 participants） |
| **临床** | ADOS 模块版本、校准分、评估与 EEG 间隔；ToMI 工具全称与常模 |
| **文献** | Chen 等学龄前研究及关键 1/f–ASD 文献的完整引用 |
| **作者与基金** | 作者单位、ORCID、资助项目、利益冲突、数据可用性声明 |
| **软件版本** | 运行环境中 MNE/specparam/statsmodels 的精确版本号 |
| **投稿元数据** | 中文/英文题目定稿、关键词、Running title、目标期刊格式 |
| **图表终稿** | 补充图编号与正文引用一致性；Table 1 排版入 Word/LaTeX |
| **可选分析** | 若审稿要求：按 138 人重跑 `periodic_peak_analysis` 与全样本 Table 1 对照说明 |

---

*本稿由项目分析输出自动整理，统计数以 `derivatives/stats/` 与 `outputs/tables/` 为准。修改结论前请重新运行对应脚本核对。*
