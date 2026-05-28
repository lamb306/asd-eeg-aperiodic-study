# 自闭症谱系障碍儿童静息态 EEG 非周期性成分异常及其年龄依赖性：基于功率谱参数化的研究

---

## 摘要

**背景：** 静息态 EEG 功率谱同时包含周期性振荡与非周期性 1/f 背景活动。传统频段功率分析难以区分周期峰与宽频非周期变化，可能混淆组间比较的解释（Donoghue et al., 2020; Neo et al., 2023）。功率谱参数化（specparam/FOOOF）可将神经功率谱建模为非周期背景与周期峰之和（Donoghue et al., 2020）。

**目的：** 比较 ASD 与典型发育（TD）儿童静息态 EEG 的非周期与周期谱参数，重点检验 global aperiodic exponent 的组间差异、空间分布、年龄依赖性、临床关联及记录内稳定性。

**方法：** 纳入 168 名具静息态睁眼 EEG 及元数据的儿童（ASD 80，TD 88）。经预处理、最少可用 epoch 标准与 specparam 拟合质量控制后，138 名进入主分析（ASD 61，TD 77）。采用 EGI HydroCel-64 采集；Welch 估计 1–40 Hz PSD；specparam fixed 模式参数化。主模型控制年龄、性别、IQ_total 与可用 epoch 数。并进行稳健性、敏感性、ROI/通道探索、周期峰、临床相关、年龄交互与奇偶 epoch 分半信度分析。

**结果：** 协变量校正后，TD 组 global aperiodic exponent 高于 ASD（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]）。未校正：ASD *M* = 1.69（*SD* = 0.14），TD *M* = 1.79（*SD* = 0.14）。Global offset 呈 TD > ASD 趋势（β = 0.060，*p* = 0.095）。fixed 模式多频段敏感性方向一致（*p* = 0.016–0.031）；knee 模式方向一致但证据较弱（*p* ≈ 0.08–0.16）。group × age 对 exponent（β = 0.0033，*p* = 0.020）与 offset（β = 0.0037，*p* = 0.021）交互显著。FDR 校正后 E33、E36、E37、E38 显著（TD > ASD），位于顶–枕部 HydroCel-64 通道。周期峰参数组间主效应均不显著（所有 group *p* > 0.24）。ASD 内临床关联未达显著（ADOS 社交子分 OLS *p* ≈ 0.057；Spearman *p* ≈ 0.076）。奇偶分半 Spearman ρ：exponent 0.959（SB = 0.979），offset 0.960（SB = 0.980），alpha_pw 0.972（SB = 0.986）。

**结论：** ASD 儿童静息态 global aperiodic exponent 低于 TD，提示非周期背景相对更平坦；效应在多种协变量与质量控制下较稳健，并显示年龄依赖性。相比周期峰，aperiodic exponent 可能更敏感地反映本队列静息态组间差异。结果需在独立样本与纵向设计中进一步验证。

**关键词：** 自闭症谱系障碍；静息态 EEG；非周期成分；aperiodic exponent；specparam；功率谱参数化；儿童；神经发育

---

## 1. 引言

自闭症谱系障碍（autism spectrum disorder, ASD）以社会沟通困难与限制性、重复性行为为核心特征，其神经生理机制高度异质（Liang & Mody, 2022）。静息态 EEG 具有无创、时间分辨率高、对儿童友好等特点，常用于发育障碍的脑功能研究（Liang & Mody, 2022; Neo et al., 2023）。与任务态相比，静息态范式对儿童配合要求较低，更适合年龄跨度较大、临床异质性较高的样本（Neo et al., 2023）。

传统 EEG 研究多关注 theta、alpha、beta 等预定义频段功率。然而，频段功率既反映周期振荡峰，也受宽频非周期 1/f 背景影响；频段变化可能来自振荡增强，也可能来自整体斜率或偏移改变（Donoghue et al., 2020）。因此，仅依赖传统频段功率可能混淆周期与非周期成分，使解释不明确（Donoghue et al., 2020; Neo et al., 2023）。系统综述与 meta 分析提示，ASD 静息态 EEG 在相对 alpha、gamma 等频段存在效应，但结论异质且多基于传统频段指标，未系统分离非周期成分（Neo et al., 2023）。

Donoghue et al.（2020）提出的 specparam（原 FOOOF）将功率谱分解为**非周期背景**（aperiodic exponent、offset）与**周期峰**（中心频率、峰功率、带宽等），无需预先固定单一频段边界即可分别估计两类成分。其中，exponent 描述功率随频率升高的衰减陡峭程度；较高 exponent 表示频谱斜率更陡，较低 exponent 表示相对更平坦。offset 反映宽频功率背景水平。文献中常讨论 aperiodic 指标与神经群体活动、时间常数或兴奋–抑制（E/I）状态**可能相关**，但头皮 EEG 上的解释受年龄、状态、参考、伪迹与模型设定等多因素影响，**不能**简单等同于单一机制（Gao et al., 2017; Donoghue et al., 2020）。

ASD 非周期 EEG 既往结果并不一致。Manyukhina et al.（2022）在 MEG 研究报告，伴低于平均智商的 ASD 儿童表现为更平坦的 aperiodic 谱斜率，作者将其与 E/I 平衡偏移相联系，但需注意该研究为 **MEG** 且存在智商亚组效应。Chen et al.（2026）在 2–6 岁学龄前 ASD 静息态 EEG 中发现，ASD 组 **aperiodic offset** 高于神经典型儿童，而 **aperiodic slope/exponent 组间差异不显著**；周期峰组间多不显著，但 ASD 内 aperiodic/periodic 指标与语言能力相关。上述差异提示，ASD 非周期异常可能受**年龄阶段**、认知水平、语言表型与分析参数影响。

儿童期非周期谱特征本身具有年龄敏感性。Hill et al.（2022）报告，典型发育儿童早期至中期童年阶段，周期与非周期成分均呈年龄依赖性变化。Wilkinson et al.（2024）在 2–44 月龄婴儿纵向 EEG 中观察到 aperiodic/periodic 成分的非线性发育轨迹。Karalunas et al.（2022）表明，EEG aperiodic 谱斜率在婴儿与青少年中可被稳定测量，并与早期 ADHD 风险相关，为 aperiodic 指标在发育队列中的**可测性与记录内一致性**提供旁证（Karalunas et al., 2022）。

基于上述背景，本研究使用 specparam 对 ASD 与 TD 儿童静息态睁眼 EEG 进行参数化分析，目标包括：（1）比较 global aperiodic exponent 与 offset；（2）探索 ROI 与通道水平空间分布；（3）比较周期峰参数组间差异；（4）探索 aperiodic 参数与临床/语言指标的关系；（5）通过敏感性分析、年龄交互与分半信度评估稳健性。我们假设 ASD 存在可检测的非周期 EEG 异常，且组间差异可能随年龄变化；**不**假设横断面交互可证明纵向发育轨迹。

---

## 2. 方法

### 2.1 研究设计与被试

本研究为横断面观察性研究，报告遵循 STROBE 声明原则（von Elm et al., 2007）。共纳入 168 名具静息态睁眼 EEG 及基本人口学信息的儿童（ASD 80，TD 88）。经预处理、最少可用 epoch 标准与 specparam 拟合质量控制后，138 名进入主分析（ASD 61，TD 77）。年龄约 40–131 月；≤72 月者 23 名（16.7%）。

ASD 诊断依据为 [待补充：DSM-5/ICD-11/临床医生诊断/ADOS-2 等具体标准]。TD 纳入标准为 [待补充]。排除标准包括 [待补充：癫痫、严重脑损伤、遗传综合征、严重感觉障碍、药物使用、睡眠不足等]。研究已获 [待补充：伦理委员会名称和批准号] 批准；知情同意程序 [待补充]。

认知能力使用 [待补充：IQ 量表名称] 评估。ASD 临床症状使用 [待补充：ADOS/ADOS-2 模块、评估者资质] 评估。`language_score` 来源于 [待补充：量表名称]；[待核实变量定义] 其与 Resting_info/ToMI 的对应关系需在定稿前确认。`ADOS_communication` [待核实变量定义]；`ADOS_RRB` 在本队列无有效数据。

### 2.2 EEG 采集

静息态 EEG 使用 EGI HydroCel-64 系统采集，原始 `.mff` 格式，采样率 500 Hz，睁眼静息。采集指令与现场细节 [待补充]。记录时长 [待补充] 分钟。保留 E1–E64 头皮电极；阻抗标准 [待补充]。

### 2.3 EEG 预处理

预处理在 Python 环境中使用 MNE-Python 完成 [citation needed: MNE-Python reference]。流程包括：0.5–45 Hz 带通、50 Hz 陷波、降采样至 250 Hz、坏导插值、平均参考；2 s 非重叠 epoch；峰峰值 > 500 µV 的 epoch 剔除。主分析要求每名被试 ≥ 60 个可用 epoch（约 120 s）。

ICA 流程为 [待核实：ICA 参数与剔除策略]。未完成系统性逐被试人工 ICA 复核（见局限）。

### 2.4 PSD 估计与功率谱参数化

Welch 方法估计 1–40 Hz 通道 PSD。使用 specparam 对每个被试×通道 PSD 参数化（Donoghue et al., 2020），主分析为 **fixed** aperiodic 模式，拟合 1–40 Hz。主要非周期指标为 exponent 与 offset；周期峰包括 alpha、theta、beta 等频段峰参数。被试级 global 指标为通过 QC 通道的算术平均。

### 2.5 质量控制

通道级：拟合 *R*² ≥ 0.90 等。被试级：无效通道比例 > 20% 则排除。样本流：168 → 145（epoch ≥ 60）→ 138（specparam QC）；7 人因拟合质量排除。

### 2.6 统计分析

参照组为 ASD；`C(group)[T.TD]` 表示 TD 相对 ASD 增量。主模型：

`global_exponent ~ group + age_months + sex + IQ_total + usable_epochs`

次要模型以 global_offset 为结局。ROI 采用五区头皮分组（frontal、central、temporal、parietal、occipital），central 为参照，拟合 group × ROI 混合模型。64 通道分别 OLS 后 FDR 校正。周期峰与 ASD 内临床分析为预设探索性分析；临床变量 [待核实变量定义]。

### 2.7 敏感性、年龄调节与信度

敏感性包括拟合频段（1–40、2–40、1–35、2–35 Hz）、fixed/knee 模式及 epoch 阈值。年龄模型：

`outcome ~ group * age_months + sex + IQ_total + usable_epochs`

≤72 月与 >72 月分层为探索性分析。**横断面** group×age 交互**不能**解释为个体纵向发育轨迹。

奇偶 epoch 分半后独立估计 PSD 与 specparam，计算 Spearman 相关及 Spearman–Brown 校正。**该分析为同一次记录内的 split-half 内部一致性，不是跨日 test–retest 重测信度**（cf. Karalunas et al., 2022）。

---

## 3. 结果

### 3.1 样本纳入与 EEG 质量控制

168 名完成预处理（ASD 80，TD 88）。145 名达到 ≥ 60 个 2 s epoch（ASD 65，TD 80）；23 人因 epoch 不足排除。7 人因 specparam 被试级 QC 未通过排除。主分析 138 名（ASD 61，TD 77）。

两组年龄差异不显著（*p* = 0.319）。TD 组 IQ_total 高于 ASD（*p* < 0.001）；主模型均校正 IQ。组平均 PSD 呈典型 1/f 形态，alpha 频段可见周期峰。

![Figure 1A](../figures/paper_ready_v2/supp_consort_flow_paper.png)

**图 1A.** 样本纳入流程。

![Figure 1B](../figures/paper_ready_v2/fig1_psd_specparam_overview.png)

**图 1B.** 组平均 PSD 与 specparam 拟合示意。

**图 1.** 样本纳入流程与组平均功率谱密度（PSD）。

**A.** CONSORT 式流程图，展示静息态 EEG 非周期分析的被试纳入过程。168 名被试完成预处理；145 名达到至少 60 个 2 s 可用 epoch；另有 7 名因超过 20% 通道未通过 specparam 质量控制而排除，主分析队列 138 名（ASD 61，TD 77）。

**B.** ASD 与 TD 组平均 PSD（specparam 拟合频段 1–40 Hz）。阴影为跨被试标准误。

| 变量 | ASD (*n* = 61) | TD (*n* = 77) | *p* |
|------|----------------|---------------|-----|
| *n* | 61 | 77 | — |
| 年龄（月） | 85.7 ± 16.9 | 88.8 ± 19.6 | 0.319 |
| IQ 总分 | 95.0 ± 15.2 | 113.2 ± 14.6 | < 0.001 |
| 性别 | 56 女 / 5 男 | 49 女 / 28 男 | < 0.001† |
| ADOS 总分‡ | 14.1 ± 3.1 | — | — |
| ADOS 社交（`ADOS_SA`）‡ | 9.3 ± 2.0 | — | — |
| ADOS 沟通‡ | 4.9 ± 1.3 | — | — |
| 语言分数（ToMI）§ | 12.7 ± 3.1 | 18.0 ± 1.7 | < 0.001 |
| 可用 epoch 数 | 120.3 ± 26.8 | 127.1 ± 28.7 | 0.152 |
| 可用记录时长（s） | 240.7 ± 53.5 | 254.3 ± 57.3 | 0.152 |
| 坏导数量 | 1.2 ± 0.6 | 1.3 ± 0.5 | 0.426 |
| 平均拟合 *R*² | 0.983 ± 0.011 | 0.987 ± 0.008 | 0.006 |

† 卡方检验。‡ 仅 ASD。§ `language_score` 映射 ToMI；ASD 缺失 6 例。

**表 1.** 主分析队列（*N* = 138）人口学、临床特征与 EEG/specparam 质量控制摘要。连续变量为均值 ± 标准差；组间检验为独立样本 *t* 检验（双侧），除非注明。

### 3.2 Global aperiodic exponent 与 offset

协变量校正后，TD 组 global exponent 高于 ASD（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]，*n* = 138）。未校正：ASD *M* = 1.69（*SD* = 0.14），TD *M* = 1.79（*SD* = 0.14）。较高 exponent 表示斜率更陡；ASD 相对更平坦。

Global offset：TD > ASD 趋势（β = 0.060，*p* = 0.095）。主组间差异集中在 exponent。

![Figure 2](../figures/paper_ready_v2/fig2_main_aperiodic_effects.png)

**图 2.** 全局非周期参数的组间差异与稳健性分析。

**A.** 按组显示的 global aperiodic exponent（箱线图叠加个体散点）。标注为校正年龄、性别、IQ_total 与可用 epoch 数后的组效应估计。

**B.** 按组显示的 global aperiodic offset。

**C.** global exponent 组效应（TD − ASD）在嵌套 OLS 模型中的稳健性；点为 β，横线为 95% CI。

### 3.3 稳健性与敏感性

嵌套模型中组效应方向均为 TD > ASD：仅组别 β = 0.096，*p* < 0.001；主模型 β = 0.079，*p* = 0.012；+ 平均 *R*² 后 β = 0.056，*p* = 0.030；+ 坏导 β = 0.081，*p* = 0.011。

fixed 模式 1–40、2–40、1–35、2–35 Hz 组效应 *p* = 0.016–0.031；knee 模式方向一致，*p* ≈ 0.08–0.16。

| 模型 | 协变量 | *N* | β (TD − ASD) | SE | 95% CI | *p* |
|------|--------|-----|--------------|-----|--------|-----|
| 仅组别 | C(group) | 138 | 0.096 | 0.025 | [0.048, 0.145] | < 0.001 |
| + 年龄、性别 | C(group) + age_months + C(sex) | 138 | 0.090 | 0.026 | [0.038, 0.142] | < 0.001 |
| + IQ_total | C(group) + age_months + C(sex) + IQ_total | 138 | 0.080 | 0.031 | [0.019, 0.141] | 0.011 |
| 主模型（+ 可用 epoch） | C(group) + age_months + C(sex) + IQ_total + usable_epochs | 138 | 0.079 | 0.031 | [0.018, 0.140] | 0.012 |
| 主模型 + 平均 *R*² | C(group) + age_months + C(sex) + IQ_total + usable_epochs + mean_r_squared | 138 | 0.056 | 0.025 | [0.005, 0.106] | 0.030 |
| 主模型 + 坏导数 | C(group) + age_months + C(sex) + IQ_total + usable_epochs + bad_channel_count | 138 | 0.081 | 0.031 | [0.019, 0.142] | 0.011 |

**表 2.** global aperiodic exponent 的主模型与稳健性 OLS 模型。β > 0 表示 TD > ASD。

### 3.4 年龄依赖性

group × age_months：global exponent（β = 0.0033，*p* = 0.020）；global offset（β = 0.0037，*p* = 0.021）。

≤72 月层 exponent 组效应 β ≈ 0.055，*p* ≈ 0.47（*n* = 23）；>72 月层 β ≈ 0.076，*p* ≈ 0.031。

![Figure 3A](../figures/extension/fig_development_interaction_exponent.png)

**图 3A.** exponent。

![Figure 3B](../figures/extension/fig_development_interaction_offset.png)

**图 3B.** offset。

**图 3.** 非周期 EEG 参数的年龄依赖性组效应。

**A.** global aperiodic exponent 随年龄的模型预测关联（按组）。

**B.** global aperiodic offset 随年龄的模型预测关联（按组）。

group × age 交互对 exponent 与 offset 均显著。本研究为横断面设计，**不应**将上述模式解释为个体纵向发育轨迹。

### 3.5 空间分布（探索性）

ROI 混合模型：组别主效应不显著；部分 ROI 的 group×ROI 交互达到显著，具体系数见补充表。

通道 FDR：E33、E36、E37、E38 显著（TD > ASD），位于顶–枕部 HydroCel-64 电极位置。**Topomap 仅反映头皮电极水平效应，不作皮层源定位推断。**

![Figure 4](../figures/paper_ready_v2/fig3_spatial_distribution.png)

**图 4.** aperiodic exponent 组效应的空间分布（探索性）。

**A.** 各 ROI 上 TD − ASD 对 exponent 的边际效应（混合模型）。

**B.** 64 通道 OLS 回归系数头皮拓扑图（HydroCel-64 布局）；FDR *q* < .05 的通道以标记显示（E33、E36、E37、E38）。**仅反映头皮电极水平，不作皮层源定位推断。**

### 3.6 周期峰参数

alpha 峰功率、中心频率、带宽及 theta、beta 峰功率的 group 项均不显著（所有 *p* > 0.24）。

### 3.7 ASD 组内临床关联（探索性）

*n* = 61。ADOS 总分等 OLS/Spearman 未显著。`ADOS_SA` [待核实变量定义]：OLS *p* ≈ 0.057；Spearman ρ = −0.229，*p* ≈ 0.076。颞叶 ROI exponent 与 `language_score` [待核实变量定义]（*n* = 55）：OLS *p* ≈ 0.319。未校正多重比较。

### 3.8 Split-half 信度

*n* = 138（见图 S1）。Spearman ρ：global exponent 0.959，SB = 0.979；global offset 0.960，SB = 0.980；alpha_pw 0.972，SB = 0.986。**为记录内 epoch 分半一致性，非 test–retest。**

---

## 4. 讨论

### 4.1 主要发现

本研究发现，协变量校正后 TD 儿童 global aperiodic exponent 高于 ASD，ASD 非周期背景相对更平坦；global offset 仅呈趋势；周期峰组间差异不显著。group×age 交互显著，提示组间差异幅度随年龄变化。主要 specparam 指标奇偶分半信度很高。

### 4.2 ASD 中较低 exponent 的解释

结果与“ASD 非周期谱更平坦”的描述一致。Manyukhina et al.（2022）在 MEG 中报告部分 ASD 儿童（尤其低于平均智商者）谱斜率更平坦，但模态、样本与智商结构不同，**不宜**直接等同于本研究静息态 EEG 结果。

aperiodic exponent 与 E/I 平衡的关系在模型与动物工作中有讨论（Gao et al., 2017），被认为与网络兴奋–抑制状态**可能有关**，仍需谨慎解释：本研究为头皮 EEG、横断面、未直接测量 E/I，**不能**将 exponent 降低直接表述为“E/I 失衡”的确定性证据。

### 4.3 与学龄前 ASD EEG 研究的比较

本研究结果与 Chen et al.（2026）学龄前样本**不完全一致**：该研究报告 ASD **offset** 更高而 **exponent 组间不显著**；本研究为 TD > ASD 的 **exponent** 效应，offset 仅趋势。差异可能首先与年龄结构有关：本队列仅 16.7% 被试处于 24–72 月，且 group×age 显著；≤72 月层效应不显著，>72 月层显著。低龄层 *n* = 23，**不能**视为对 Chen et al.（2026）的充分复现。

exponent 与 offset 相关（本队列 *r* ≈ 0.73）；控制 offset 后 exponent 组效应仍保留，控制 exponent 后 offset 不显著，提示两参数对年龄与组别的敏感性不同。上述差异应表述为与 Chen et al.（2026）**不完全一致**，而非将其简单视为相互矛盾。

### 4.4 年龄依赖性与发育解释

group×age 交互与 Hill et al.（2022）、Wilkinson et al.（2024）关于发育期 aperiodic/周期成分变化的文献背景一致，即儿童期谱参数非常态。必须强调：本研究为**横断面**设计，交互**不能**证明纵向发育轨迹或因果性成熟效应（Hill et al., 2022; Wilkinson et al., 2024）。

### 4.5 周期峰阴性结果

周期峰组间不显著，与 Chen et al.（2026）组水平 alpha 峰参数多不显著的结果部分一致，支持组间差异主要见于**非周期 exponent** 而非传统周期峰。这也体现 specparam 分离的价值（Donoghue et al., 2020）：避免将非周期背景变化误判为频段振荡差异。

### 4.6 空间分布

顶–枕通道 FDR 显著为探索性发现；ROI 交互提示空间非均匀性。头皮电位**不能**推断皮层源活动；未做源定位。

### 4.7 临床关联

ASD 内临床关联未达显著；`ADOS_SA` [待核实变量定义] 仅趋势。Chen et al.（2026）报告 ASD 内 aperiodic/周期指标与语言相关，但本研究语言指标 [待核实变量定义] 与量表来源不同，不可直接类比。不能声称 exponent 为症状严重度生物标志物。

### 4.8 信度

分半信度与 Karalunas et al.（2022）关于 aperiodic 斜率可在发育样本中稳定测量的报告方向一致，但本研究为**单次记录内** odd–even 分半，**不是**跨日 test–retest（Karalunas et al., 2022）。

### 4.9 局限

（1）横断面设计；（2）IQ 与性别组间不均衡，虽已校正；（3）临床变量缺失与定义 [待核实变量定义]；（4）ICA [待核实：ICA 参数与剔除策略]；（5）knee 模式证据较弱；（6）无源定位；（7）分半信度 ≠ test–retest；（8）缺少独立外部验证队列。

### 4.10 结论

ASD 儿童静息态 global aperiodic exponent 低于 TD，效应较稳健并具年龄依赖性；周期峰组间不显著。结果支持在年龄匹配样本中进一步区分非周期 exponent 与 offset，并开展纵向与多中心验证。


---

## References

Chen, Y., Tsou, M., Nelson, C. A., & Tager-Flusberg, H. (2026). Resting state aperiodic and periodic EEG activity in preschool-aged autistic children: Differences from neurotypical peers and links to language skills. *Molecular Autism*, *17*, Article 7. https://doi.org/10.1186/s13229-025-00700-1

Donoghue, T., Dominguez, J., & Voytek, B. (2020). Electrophysiological frequency band ratio measures conflate periodic and aperiodic neural activity. *eNeuro*, *7*(6), Article ENEURO.0192-20.2020. https://doi.org/10.1523/ENEURO.0192-20.2020

Donoghue, T., Haller, M., Peterson, E. J., Varma, P., Sebastian, P., Gao, R., Noto, T., Lara, A. H., Wallis, J. D., Knight, R. T., Shestyuk, A., & Voytek, B. (2020). Parameterizing neural power spectra into periodic and aperiodic components. *Nature Neuroscience*, *23*(12), 1655–1665. https://doi.org/10.1038/s41593-020-00744-x

Gao, R., Peterson, E. J., & Voytek, B. (2017). Inferring synaptic excitation/inhibition balance from field potentials. *NeuroImage*, *158*, 70–78. https://doi.org/10.1016/j.neuroimage.2017.06.065

Hill, A. T., Clark, G. M., Bigelow, F. J., Lum, J. A. G., & Enticott, P. G. (2022). Periodic and aperiodic neural activity displays age-dependent changes across early-to-middle childhood. *Developmental Cognitive Neuroscience*, *54*, Article 101076. https://doi.org/10.1016/j.dcn.2022.101076

Karalunas, S. L., Gustafsson, H. C., Ostlund, B. D., Alperin, B. R., Deming, E. M., & Sullivan, E. L. (2022). Electroencephalogram aperiodic power spectral slope can be reliably measured and predicts ADHD risk in early development. *Developmental Psychobiology*, *64*(3), Article e22228. https://doi.org/10.1002/dev.22228

Liang, S., & Mody, M. (2022). Abnormal brain oscillations in developmental disorders: Application of resting state EEG and MEG in autism spectrum disorder and fragile X syndrome. *Frontiers in Neuroimaging*, *1*, Article 903191. https://doi.org/10.3389/fnimg.2022.903191

Manyukhina, V. O., Prokofyev, A. O., Galuta, I. A., Goiaeva, D. E., Obukhova, T. S., Stroganova, T. A., Orekhova, E. V., & Altukhov, D. I. (2022). Globally elevated excitation–inhibition ratio in children with autism spectrum disorder and below-average intelligence. *Molecular Autism*, *13*, Article 20. https://doi.org/10.1186/s13229-022-00498-2

Neo, W. S., Foti, D., Keehn, B., & Kelleher, B. (2023). Resting-state EEG power differences in autism spectrum disorder: A systematic review and meta-analysis. *Translational Psychiatry*, *13*, Article 389. https://doi.org/10.1038/s41398-023-02681-2

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., & Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: Guidelines for reporting observational studies. *PLoS Medicine*, *4*(10), Article e296. https://doi.org/10.1371/journal.pmed.0040296

Wilkinson, C. L., Yankowitz, L. D., Chao, J. Y., et al. (2024). Developmental trajectories of EEG aperiodic and periodic components in children 2–44 months of age. *Nature Communications*, *15*, Article 5788. https://doi.org/10.1038/s41467-024-50204-4


---

## 补充材料

### 表 S1. 样本纳入流程

| stage | n_total | n_ASD | n_TD | excluded_total | exclusion_reason |
| --- | --- | --- | --- | --- | --- |
| participants_total | 168 | 80 | 88 | nan | nan |
| included_final | 168 | 80 | 88 | 0.0 | not included_final=1 |
| preprocessing_success | 168 | 80 | 88 | 0.0 | preprocessing failed or no epochs |
| min_usable_epochs_pass | 145 | 65 | 80 | 23.0 | usable_epochs < 60 |
| specparam_subject_qc_pass | 138 | 61 | 77 | 7.0 | low_quality_subject (invalid channel ratio > threshold) |
| roi_available_after_specparam | 138 | 61 | 77 | 0.0 | nan |
| main_analysis_complete_case | 138 | 61 | 77 | 0.0 | missing outcome/covariates or specparam QC fail |

### 表 S2. 拟合频段与 fixed/knee 敏感性

| freq_range | aperiodic_mode | n | coef_TD_vs_ASD | p | ci_low | ci_high | direction | significant_p05 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.0–35.0 Hz | fixed | 145 | 0.072787675297949 | 0.0159528411230305 | 0.0138028134280818 | 0.1317725371678162 | TD > ASD | True |
| 1.0–35.0 Hz | knee | 145 | 0.0979583944874363 | 0.1265595542592059 | -0.0280517305883811 | 0.2239685195632538 | TD > ASD | False |
| 1.0–40.0 Hz | fixed | 145 | 0.0782445248644347 | 0.021874852579498 | 0.0115220359180365 | 0.144967013810833 | TD > ASD | True |
| 1.0–40.0 Hz | knee | 145 | 0.1256394401949946 | 0.075734423204664 | -0.0131876088525272 | 0.2644664892425163 | TD > ASD | False |
| 2.0–35.0 Hz | fixed | 145 | 0.0835191409272405 | 0.029413044305785 | 0.0084805211403368 | 0.1585577607141442 | TD > ASD | True |
| 2.0–35.0 Hz | knee | 145 | 0.1127135006447078 | 0.162584286777485 | -0.0460282127492142 | 0.27145521403863 | TD > ASD | False |
| 2.0–40.0 Hz | fixed | 145 | 0.0934962251620929 | 0.0310510027340927 | 0.0086422222015419 | 0.1783502281226439 | TD > ASD | True |
| 2.0–40.0 Hz | knee | 145 | 0.1277253810911113 | 0.1404385251556368 | -0.042605124537508 | 0.2980558867197307 | TD > ASD | False |

### 表 S3. 年龄交互与分层组效应

*完整表共 28 行；定稿时可从补充数据包导出。*

| outcome | model_name | n | n_ASD | n_TD | term | coef | se | t | p | ci_low | ci_high | r_squared | aic | bic | highlight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_exponent | interaction_raw | 138 | 61 | 77 | Intercept | 1.805584552420465 | 0.1446755081520446 | 12.480236464923369 | 4.858190824828127e-24 | 1.5193818865141178 | 2.091787218326812 | 0.1491528671575767 | -140.01575281532536 | -119.52497701922492 | False |
| global_exponent | interaction_raw | 138 | 61 | 77 | C(group)[T.TD] | -0.201504391399164 | 0.1225146728156718 | -1.6447368039119308 | 0.1024216736243655 | -0.443867638781984 | 0.0408588559836559 | 0.1491528671575767 | -140.01575281532536 | -119.52497701922492 | True |
| global_exponent | interaction_raw | 138 | 61 | 77 | C(sex)[T.M] | 0.0197984585915517 | 0.0301285648013994 | 0.6571324828135249 | 0.5122485992079473 | -0.0398030294297003 | 0.0793999466128038 | 0.1491528671575767 | -140.01575281532536 | -119.52497701922492 | False |
| global_exponent | interaction_raw | 138 | 61 | 77 | age_months | -0.0018324064124529 | 0.0011306312551831 | -1.6206932225274004 | 0.1074881056105721 | -0.0040690647350931 | 0.0004042519101871 | 0.1491528671575767 | -140.01575281532536 | -119.52497701922492 | False |
| global_exponent | interaction_raw | 138 | 61 | 77 | C(group)[T.TD]:age_months | 0.0033138845829945 | 0.0014014504745182 | 2.364610554028764 | 0.0195173035919586 | 0.0005414812435065 | 0.0060862879224825 | 0.1491528671575767 | -140.01575281532536 | -119.52497701922492 | True |
| global_exponent | interaction_raw | 138 | 61 | 77 | IQ_total | 9.793346694991789e-05 | 0.0008485976465822 | 0.1154062438711065 | 0.908299843621314 | -0.001580795101803 | 0.0017766620357028 | 0.1491528671575767 | -140.01575281532536 | -119.52497701922492 | False |

### 表 S4. 周期峰参数分析

*完整表共 30 行；定稿时可从补充数据包导出。*

| model | outcome | term | coef | std_err | pvalue | ci_low | ci_high | n_obs | r_squared | used_mixedlm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| periodic_peak | alpha_cf | Intercept | 8.309824208168703 | 0.3869029078952398 | 5.3585984676289596e-46 | 7.544848397143197 | 9.074800019194209 | 145 | 0.2089634612383117 | nan |
| periodic_peak | alpha_cf | C(group)[T.TD] | -0.1240000599244796 | 0.1067203302237971 | 0.2472607996110283 | -0.3350051195917071 | 0.0870049997427478 | 145 | 0.2089634612383117 | nan |
| periodic_peak | alpha_cf | C(sex)[T.M] | -0.1858772102935323 | 0.1056405925712171 | 0.0806885247722443 | -0.3947474367258006 | 0.0229930161387358 | 145 | 0.2089634612383117 | nan |
| periodic_peak | alpha_cf | age_months | 0.0129221914366694 | 0.0025242643264026 | 1.0026080590122257e-06 | 0.0079312722398162 | 0.0179131106335225 | 145 | 0.2089634612383117 | nan |
| periodic_peak | alpha_cf | IQ_total | 0.0021755447588242 | 0.0029815805601617 | 0.4668249008406441 | -0.0037195699084586 | 0.0080706594261071 | 145 | 0.2089634612383117 | nan |
| periodic_peak | alpha_cf | usable_epochs | 0.0002957246709521 | 0.0016540487514047 | 0.8583642125762921 | -0.0029746236755228 | 0.0035660730174271 | 145 | 0.2089634612383117 | nan |

### 表 S5. 临床关联（OLS 与 Spearman）

*完整表共 4 行；定稿时可从补充数据包导出。*

| model | outcome | term | coef | std_err | pvalue | ci_low | ci_high | n_obs | r_squared | used_mixedlm | n_asd_complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| clinical_ols | ADOS_total | global_exponent | -3.937794620302176 | 2.9541244538276854 | 0.1880332745025793 | -9.857992321182447 | 1.982403080578094 | 61 | 0.0662474011807772 | nan | 61 |
| clinical_ols | ADOS_SA | global_exponent | -3.559690864327957 | 1.8279013042120704 | 0.0565967983164178 | -7.222886937401583 | 0.1035052087456689 | 61 | 0.1392456264926186 | nan | 61 |
| clinical_ols | ADOS_communication | global_exponent | -1.367304286679511 | 1.193709111543195 | 0.2569928319602953 | -3.759550804432372 | 1.0249422310733498 | 61 | 0.0812369486636854 | nan | 61 |
| clinical_ols | language_score | temporal_exponent | -2.3292325454265925 | 2.3127631642719804 | 0.3188242310165216 | -6.976904129692228 | 2.3184390388390432 | 55 | 0.1640695275352983 | nan | 55 |

### 表 S6. 奇偶分半信度

| metric | n_subjects | pearson_r | pearson_p | spearman_rho | spearman_p | spearman_brown_pearson | spearman_brown_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_exponent | 138 | 0.9608093296081588 | 1.1844081158974275e-77 | 0.9587067255113711 | 3.855885754425061e-76 | 0.980013013096142 | 0.9789180922540364 |
| global_offset | 138 | 0.9596996150944496 | 7.618670782478855e-77 | 0.9603825666854646 | 2.438432776804152e-77 | 0.9794354274526872 | 0.9797909683610792 |
| alpha_pw | 138 | 0.9819015663963376 | 3.6589465518475424e-100 | 0.972163684476094 | 1.3682656203902708e-87 | 0.9908681470813052 | 0.9858853929098178 |


![Figure S1](../figures/extension/fig_split_half_reliability.png)

**图 S1.** specparam 衍生指标的奇偶 epoch 分半信度。

global exponent、global offset 与 alpha 峰功率的组内分半 Spearman 相关及 Spearman–Brown 校正估计均 > 0.97。**为同次记录内的 within-session 一致性，不是跨日 test–retest 重测信度。**

![Figure S2](../figures/compare_preschool_study/fig_fixed_vs_knee_effects.png)

**图 S2.** fixed 与 knee 模式的敏感性分析。

fixed 模式各频段范围的 TD − ASD exponent 效应方向一致且多数达到 *p* < .05；knee 模式方向相似但统计证据较弱。
### 表 S3（续）. 年龄分层组效应

| outcome | age_stratum | n_total | n_ASD | n_TD | ASD_mean | TD_mean | TD_minus_ASD_unadjusted | underpowered | coef_TD_vs_ASD_adjusted | se | p | ci_low | ci_high | r_squared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_exponent | preschool_like | 23 | 10 | 13 | 1.7082476793218555 | 1.7618274374193834 | 0.0535797580975276 | False | 0.0551667498365799 | 0.0740542649107265 | 0.465917957408094 | -0.1004154874882081 | 0.2107489871613681 | 0.1129391333027808 |
| global_exponent | older_child | 115 | 51 | 64 | 1.6885451060027397 | 1.7932129209503205 | 0.1046678149475808 | False | 0.0758985971398923 | 0.0348147653726816 | 0.0313834089663239 | 0.0069039038203242 | 0.1448932904594603 | 0.134251453133862 |
| global_exponent | tertile_1_youngest | 46 | 23 | 23 | 1.7145107944796505 | 1.746733728416825 | 0.0322229339371744 | False | 0.0356741484164716 | 0.04816909818083 | 0.46315505506118 | -0.0616053188689277 | 0.132953615701871 | 0.0345389461555112 |
| global_exponent | tertile_2_middle | 46 | 23 | 23 | 1.700199653099388 | 1.7690078747428266 | 0.0688082216434387 | False | 0.0285222864761954 | 0.0638100131652883 | 0.6572363983225817 | -0.100344649435508 | 0.1573892223878988 | 0.0779243653325872 |
| global_exponent | tertile_3_oldest | 46 | 15 | 31 | 1.64399579366936 | 1.832494411438726 | 0.1884986177693659 | False | 0.1830105927302951 | 0.0585352833393141 | 0.0032477809405442 | 0.0647961898101558 | 0.3012249956504345 | 0.3584967366010942 |
| global_offset | preschool_like | 23 | 10 | 13 | -9.988971735365812 | -9.977151100174725 | 0.0118206351910892 | False | 0.0454243085560106 | 0.0653872443922988 | 0.4961154752022461 | -0.0919491943383921 | 0.1827978114504134 | 0.279528811770392 |
| global_offset | older_child | 115 | 51 | 64 | -10.118033164754287 | -10.070146320829425 | 0.047886843924866 | False | 0.0476616296703058 | 0.0408689697749295 | 0.2460535160680712 | -0.0333310757442924 | 0.1286543350849041 | 0.0700744108471101 |
| global_offset | tertile_1_youngest | 46 | 23 | 23 | -10.036745868774933 | -10.002069026399903 | 0.0346768423750294 | False | 0.059629981296487 | 0.0484402466047398 | 0.2253377215268185 | -0.0381970813400688 | 0.1574570439330428 | 0.1500760408623337 |

### 表 S5（续）. 临床关联 Spearman

| clinical | eeg_variable | rho | pvalue | n |
| --- | --- | --- | --- | --- |
| ADOS_total | global_exponent | -0.1897666020222448 | 0.1429728821528742 | 61 |
| ADOS_SA | global_exponent | -0.2287354336821751 | 0.0762102297329444 | 61 |
| ADOS_communication | global_exponent | -0.1374278938570874 | 0.2908941484817425 | 61 |
| language_score | temporal_exponent | -0.1425711142207802 | 0.2990997292130304 | 55 |

### 表 S2（续）. 敏感性分析（完整）

*完整表共 8 行；摘要见表 S2 主表。*


---

## 附录：图表清单

| 编号 | 内容 | 位置 |
|------|------|------|
| 图 1 | 样本纳入 + 组平均 PSD | 结果 §3.1 |
| 表 1 | 人口学与 EEG QC | 结果 §3.1 |
| 图 2 | 主效应与稳健性 | 结果 §3.2–3.3 |
| 表 2 | 主模型与稳健性模型 | 结果 §3.3 |
| 图 3 | 年龄交互 | 结果 §3.4 |
| 图 4 | 空间分布 | 结果 §3.5 |
| 图 S1 | Split-half 信度 | 补充材料 |
| 图 S2 | fixed vs knee | 补充材料 |
| 表 S1–S6 | 见补充材料 | 补充材料 |

---

## 附录：待补充信息清单

（同 v4：伦理批号、诊断标准、IQ/ADOS 量表、EEG 采集、ICA、`language_score` 等。）

---

## 附录：引用待核查清单

（同 v4；见 `reference_audit_APA.md`。）

---

## 生成统计（v5）

| 指标 | 数值 |
|------|------|
| 正文图 | 4（图 1A/1B 计为图 1 两 panel） |
| 补充图 | 2 |
| 正文表 | 2 |
| 补充表 | 6 |
