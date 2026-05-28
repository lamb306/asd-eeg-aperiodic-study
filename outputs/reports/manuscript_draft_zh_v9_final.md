# 自闭症谱系障碍儿童静息态 EEG 非周期性成分异常及其年龄依赖性：基于功率谱参数化的研究

## 摘要

背景： 静息态 EEG 功率谱同时包含周期性振荡与非周期性 1/f 背景活动。传统频段功率分析难以区分周期峰与宽频非周期变化，可能混淆组间比较的解释（Donoghue et al., 2020a; Neo et al., 2023）。功率谱参数化（specparam/FOOOF）可将神经功率谱建模为非周期背景与周期峰之和（Donoghue et al., 2020b）。

目的： 比较 ASD 与典型发育（TD）儿童静息态 EEG 的非周期与周期谱参数，重点检验 global aperiodic exponent 的组间差异、空间分布、年龄依赖性、临床关联及记录内稳定性。

方法： 纳入 168 名具静息态睁眼 EEG 及元数据的儿童（ASD 80，TD 88）。经预处理、最少可用 epoch 标准与 specparam 拟合质量控制后，138 名进入主分析（ASD 61，TD 77）。采用 EGI HydroCel-64 采集；Welch 估计 1–40 Hz PSD；specparam fixed 模式参数化。主模型控制年龄、性别、IQ_total 与可用 epoch 数。并进行稳健性、敏感性、ROI/通道探索、周期峰、临床相关、年龄交互与奇偶 epoch 分半信度分析。

结果： 协变量校正后，TD 组 global aperiodic exponent 高于 ASD（β = 0.079，SE = 0.031，p = 0.012，95% CI [0.018, 0.140]）。未校正：ASD M = 1.69（SD = 0.14），TD M = 1.79（SD = 0.14）。Global offset 呈 TD > ASD 趋势（β = 0.060，p = 0.095）。fixed 模式多频段敏感性方向一致（p = 0.016–0.031）；knee 模式方向一致但证据较弱（p ≈ 0.08–0.16）。group × age 对 exponent（β = .0033，p = 0.020）与 offset（β = .0037，p = 0.021）交互显著。FDR 校正后 E33、E36、E37、E38 显著（TD > ASD），位于顶–枕部 HydroCel-64 通道。周期峰参数组间主效应均不显著（所有 group p > 0.24）。ASD 内探索性临床关联未达显著。奇偶分半 Spearman ρ：exponent 0.959（SB = 0.979），offset 0.960（SB = 0.980），alpha_pw 0.972（SB = 0.986）。在自动 ICA 伪迹控制敏感性分析中，TD vs ASD 的 global exponent 方向一致但效应减弱且不再显著（β ≈ 0.053，p ≈ 0.115–0.119）。In an automated ICA artifact-control sensitivity analysis, the direction of the TD–ASD global exponent effect was preserved but attenuated and no longer statistically significant (β ≈ 0.053, p ≈ .115–.119).

结论： ASD 儿童静息态 global aperiodic exponent 低于 TD，提示非周期背景相对更平坦；效应在多种协变量与质量控制下较稳健，并显示年龄依赖性。相比周期峰，aperiodic exponent 可能更敏感地反映本队列静息态组间差异。自动 ICA 敏感性分析显示效应方向保持但统计证据减弱，提示结论对伪迹清洗策略具有一定敏感性。In an automated ICA artifact-control sensitivity analysis, the TD–ASD exponent effect remained directionally consistent but attenuated, suggesting sensitivity of the finding to artifact-cleaning strategy. 结果需在独立样本与纵向设计中进一步验证。

关键词： 自闭症谱系障碍；静息态 EEG；非周期成分；aperiodic exponent；specparam；功率谱参数化；儿童；神经发育

## 1. 引言

自闭症谱系障碍（Autism Spectrum Disorder, ASD）以社会沟通困难与限制性、重复性行为为核心特征，其神经生理机制高度异质（Liang & Mody, 2022）。静息态 EEG 具有无创、时间分辨率高、对儿童友好等特点，常用于发育障碍的脑功能研究（Liang & Mody, 2022; Neo et al., 2023）。与任务态相比，静息态范式对儿童配合要求较低，更适合年龄跨度较大、临床异质性较高的样本（Neo et al., 2023）。

传统 EEG 研究多关注 theta、alpha、beta 等预定义频段功率。然而，频段功率既反映周期振荡峰，也受宽频非周期 1/f 背景影响；频段变化可能来自振荡增强，也可能来自整体斜率或偏移改变（Donoghue et al., 2020a）。因此，仅依赖传统频段功率可能混淆周期与非周期成分，使解释不明确（Donoghue et al., 2020a; Neo et al., 2023）。系统综述与 meta 分析提示，ASD 静息态 EEG 在相对 alpha、gamma 等频段存在效应，但结论异质且多基于传统频段指标，未系统分离非周期成分（Neo et al., 2023）。

Donoghue et al.（2020b）提出的 specparam（原 FOOOF）将功率谱分解为非周期背景（aperiodic exponent、offset）与周期峰（中心频率、峰功率、带宽等），无需预先固定单一频段边界即可分别估计两类成分。其中，exponent 描述功率随频率升高的衰减陡峭程度；较高 exponent 表示频谱斜率更陡，较低 exponent 表示相对更平坦。offset 反映宽频功率背景水平。文献中常讨论 aperiodic 指标与神经群体活动、时间常数或兴奋–抑制（E/I）状态可能相关，但头皮 EEG 上的解释受年龄、状态、参考、伪迹与模型设定等多因素影响，不能简单等同于单一机制（Gao et al., 2017; Donoghue et al., 2020b）。

ASD 非周期 EEG 既往结果并不一致。Manyukhina et al.（2022）在 MEG 研究报告，伴低于平均智商的 ASD 儿童表现为更平坦的 aperiodic 谱斜率，作者将其与 E/I 平衡偏移相联系，但需注意该研究为 MEG 且存在智商亚组效应。Chen et al.（2026）在 2–6 岁学龄前 ASD 静息态 EEG 中发现，ASD 组 aperiodic offset 高于神经典型儿童，而 aperiodic slope/exponent 组间差异不显著；周期峰组间多不显著，但 ASD 内 aperiodic/periodic 指标与语言能力相关。上述差异提示，ASD 非周期异常可能受年龄阶段、认知水平、语言表型与分析参数影响。

儿童期非周期谱特征本身具有年龄敏感性。Hill et al.（2022）报告，典型发育儿童早期至中期童年阶段，周期与非周期成分均呈年龄依赖性变化。Wilkinson et al.（2024）在 2–44 月龄婴儿纵向 EEG 中观察到 aperiodic/periodic 成分的非线性发育轨迹。Karalunas et al.（2022）表明，EEG aperiodic 谱斜率在婴儿与青少年中可被稳定测量，并与早期 ADHD 风险相关，为 aperiodic 指标在发育队列中的可测性与记录内一致性提供旁证（Karalunas et al., 2022）。

基于上述背景，本研究使用 specparam 对 ASD 与 TD 儿童静息态睁眼 EEG 进行参数化分析，目标包括：（1）比较 global aperiodic exponent 与 offset；（2）探索 ROI 与通道水平空间分布；（3）比较周期峰参数组间差异；（4）探索 aperiodic 参数与临床/语言指标的关系；（5）通过敏感性分析、年龄交互与分半信度评估稳健性。我们假设 ASD 存在可检测的非周期 EEG 异常，且组间差异可能随年龄变化；不假设横断面交互可证明纵向发育轨迹。

## 2. 方法

### 2.1 研究设计与被试

本研究为横断面观察性研究，报告遵循 STROBE 声明原则（von Elm et al., 2007）。共纳入 168 名具静息态睁眼 EEG 及基本人口学信息的儿童（ASD 80，TD 88）。经预处理、最少可用 epoch 标准与 specparam 拟合质量控制后，138 名进入主分析（ASD 61，TD 77）。年龄约 40–131 月；≤72 月者 23 名（16.7%）。

ASD 诊断依据为 [待补充：DSM-5/ICD-11/临床医生诊断/ADOS-2 等具体标准]。TD 纳入标准为 [待补充]。排除标准包括 [待补充：癫痫、严重脑损伤、遗传综合征、严重感觉障碍、药物使用、睡眠不足等]。研究已获 [待补充：伦理委员会名称和批准号] 批准；知情同意程序 [待补充]。

认知能力使用 [待补充：IQ 量表名称] 评估。ASD 临床症状使用 [待补充：ADOS/ADOS-2 模块、评估者资质] 评估。临床与语言变量定义见作者需补充清单；探索性语言指标仅于补充表报告。

### 2.2 EEG 采集

静息态 EEG 使用 EGI HydroCel-64 系统采集，原始 MFF 格式，采样率 500 Hz，睁眼静息。采集指令与现场细节 [待补充]。记录时长 [待补充] 分钟。保留 E1–E64 头皮电极；阻抗标准 [待补充]。

### 2.3 EEG 预处理

预处理在 Python 环境中使用 MNE-Python 完成 [citation needed: MNE-Python reference]。流程包括：0.5–45 Hz 带通、50 Hz 陷波、降采样至 250 Hz、坏导插值、平均参考；2 s 非重叠 epoch；峰峰值 > 500 µV 的 epoch 剔除。主分析要求每名被试 ≥ 60 个可用 epoch（约 120 s）。

ICA 流程为 [待核实：ICA 参数与剔除策略]。未完成系统性逐被试人工 ICA 复核（见局限）。

### 2.4 PSD 估计与功率谱参数化

Welch 方法估计 1–40 Hz 通道 PSD。使用 specparam 对每个被试×通道 PSD 参数化（Donoghue et al., 2020b），主分析为 fixed aperiodic 模式，拟合 1–40 Hz。主要非周期指标为 exponent 与 offset；周期峰包括 alpha、theta、beta 等频段峰参数。被试级 global 指标为通过 QC 通道的算术平均。

### 2.5 质量控制

通道级：拟合 R² ≥ 0.90 等。被试级：无效通道比例 > 20% 则排除。样本流：168 → 145（epoch ≥ 60）→ 138（specparam QC）；7 人因拟合质量排除。

### 2.6 统计分析

参照组为 ASD；TD 相对 ASD 的回归系数表示 TD 组增量。主模型：

global exponent ~ group + age (months) + sex + IQ total + usable epochs

次要模型以 global_offset 为结局。ROI 采用五区头皮分组（frontal、central、temporal、parietal、occipital），central 为参照，拟合 group × ROI 混合模型。64 通道分别 OLS 后 FDR 校正。周期峰与 ASD 内临床分析为预设探索性分析（临床变量定义见作者需补充清单）。

### 2.7 敏感性、年龄调节与信度

敏感性包括拟合频段（1–40、2–40、1–35、2–35 Hz）、fixed/knee 模式及 epoch 阈值。年龄模型：

outcome ~ group × age (months) + sex + IQ total + usable epochs

≤72 月与 >72 月分层为探索性分析。横断面 group×age 交互不能解释为个体纵向发育轨迹。

奇偶 epoch 分半后独立估计 PSD 与 specparam，计算 Spearman 相关及 Spearman–Brown 校正。该分析为同一次记录内的 split-half 内部一致性，不是跨日 test–retest 重测信度（cf. Karalunas et al., 2022）。

## 3. 结果

### 3.1 样本纳入与 EEG 质量控制

168 名完成预处理（ASD 80，TD 88）。145 名达到 ≥ 60 个 2 s epoch（ASD 65，TD 80）；23 人因 epoch 不足排除。7 人因 specparam 被试级 QC 未通过排除。主分析 138 名（ASD 61，TD 77）。

两组年龄差异不显著（p = 0.319）。TD 组 IQ_total 高于 ASD（p < 0.001）；主模型均校正 IQ。组平均 PSD 呈典型 1/f 形态，alpha 频段可见周期峰。

![Figure 1A](../figures/paper_ready_v2/supp_consort_flow_paper.png)

图 1A. 样本纳入流程。

![Figure 1B](../figures/paper_ready_v2/fig1_psd_specparam_overview.png)

图 1B. 组平均 PSD 与 specparam 拟合示意。

图 1. 样本纳入流程与组平均功率谱密度（PSD）。

A. CONSORT 式流程图，展示静息态 EEG 非周期分析的被试纳入过程。168 名被试完成预处理；145 名达到至少 60 个 2 s 可用 epoch；另有 7 名因超过 20% 通道未通过 specparam 质量控制而排除，主分析队列 138 名（ASD 61，TD 77）。

B. ASD 与 TD 组平均 PSD（specparam 拟合频段 1–40 Hz）。阴影为跨被试标准误。

| Characteristic | ASD (n = 61) | TD (n = 77) | Statistic | p |
|----------------|--------------|-------------|-----------|-----|
| Age, months | 85.7 ± 16.9 | 88.8 ± 19.6 | t | p = .319 |
| Sex, F/M | 5 F / 56 M | 28 F / 49 M | χ² | p < .001 |
| IQ total | 95.0 ± 15.2 | 113.2 ± 14.6 | t | p < .001 |
| Usable epochs | 120.3 ± 26.8 | 127.1 ± 28.7 | t | p = .152 |
| Usable seconds | 240.7 ± 53.5 | 254.3 ± 57.3 | t | p = .152 |
| Bad channel count | 1.2 ± 0.6 | 1.3 ± 0.5 | t | p = .426 |
| Mean specparam R² | 0.983 ± 0.011 | 0.987 ± 0.008 | t | p = .006 |

Table 1. Demographic characteristics and EEG quality metrics for the primary analysis cohort (N = 138). Continuous variables are mean ± SD. TD–ASD comparisons used two-sided independent-samples t tests except sex (χ²). R² = specparam model fit quality per subject.

### 3.2 Global aperiodic exponent 与 offset

协变量校正后，TD 组 global exponent 高于 ASD（β = 0.079，SE = 0.031，p = 0.012，95% CI [0.018, 0.140]，n = 138）。未校正：ASD M = 1.69（SD = 0.14），TD M = 1.79（SD = 0.14）。较高 exponent 表示斜率更陡；ASD 相对更平坦。

Global offset：TD > ASD 趋势（β = 0.060，p = 0.095）。主组间差异集中在 exponent。

![Figure 2](../figures/paper_ready_v2/fig2_main_aperiodic_effects.png)

图 2. 全局非周期参数的组间差异与稳健性分析。

A. 按组显示的 global aperiodic exponent（箱线图叠加个体散点）。标注为校正年龄、性别、IQ_total 与可用 epoch 数后的组效应估计。

B. 按组显示的 global aperiodic offset。

C. global exponent 组效应（TD − ASD）在嵌套 OLS 模型中的稳健性；点为 β，横线为 95% CI。

### 3.3 稳健性与敏感性

嵌套模型中组效应方向均为 TD > ASD：仅组别 β = 0.096，p < 0.001；主模型 β = 0.079，p = 0.012；+ 平均 R² 后 β = 0.056，p = 0.030；+ 坏导 β = 0.081，p = 0.011。

fixed 模式 1–40、2–40、1–35、2–35 Hz 组效应 p = 0.016–0.031；knee 模式方向一致，p ≈ 0.08–0.16。

| Model | Covariates | β (TD − ASD) | SE | 95% CI | p |
|-------|------------|--------------|-----|--------|-----|
| Group only | Group | 0.096 | 0.025 | [0.048, 0.145] | p < .001 |
| + Age, sex | Group + age + sex | 0.090 | 0.026 | [0.038, 0.142] | p < .001 |
| + IQ | Group + age + sex + IQ | 0.080 | 0.031 | [0.019, 0.141] | p = .011 |
| Primary | Group + age + sex + IQ + usable epochs | 0.079 | 0.031 | [0.018, 0.140] | p = .012 |
| + Mean R² | Primary + mean specparam R² | 0.056 | 0.025 | [0.005, 0.106] | p = .030 |
| + Bad channels | Primary + bad channel count | 0.081 | 0.031 | [0.019, 0.142] | p = .011 |

Table 2. Primary and robustness OLS models for global aperiodic exponent (N = 138). Positive β indicates higher exponent in TD than ASD.


### 自动 ICA 伪迹控制敏感性分析（Artifact-Control Sensitivity Analysis）

为评估残留眼动/肌电伪迹对 global exponent 组效应的潜在影响，我们在不替代主流程的前提下开展自动 ICA 伪迹控制敏感性分析。该分析使用 mne-icalabel 对独立成分自动分类，并在 eye blink、muscle artifact、heart beat、line noise、channel noise 任一类别概率达到阈值时剔除相应成分（阈值 0.80 与 0.70）。

自动 ICA 质量控制覆盖主队列 138 名被试并在两个阈值下重复运行（138 × 2）。总体平均每名被试剔除 ICA 成分约 3.4 个，保留成分最大伪迹概率的平均值约为 0.082。重处理后，进入完整协变量回归模型的样本量为 n = 135（阈值 0.80）与 n = 137（阈值 0.70）。

在与主模型相同协变量结构（age_months、sex、IQ_total、usable_epochs）下，global exponent 的 TD − ASD 效应在自动 ICA 后方向保持一致（TD > ASD）但显著减弱：阈值 0.80 时 β = 0.053，95% CI [−0.013, 0.119]，p = 0.115；阈值 0.70 时 β = 0.053，95% CI [−0.014, 0.121]，p = 0.119。对应的 global offset 在两阈值下亦未达显著。该结果提示：主效应未发生方向反转，但统计证据对伪迹清洗策略具有敏感性。

### 3.4 年龄依赖性

group × age_months：global exponent（β = .0033，p = 0.020）；global offset（β = .0037，p = 0.021）。

≤72 月层 exponent 组效应 β ≈ 0.055，p ≈ 0.47（n = 23）；>72 月层 β ≈ 0.076，p ≈ 0.031。

![Figure 3A](../figures/extension/fig_development_interaction_exponent.png)

图 3A. exponent。

![Figure 3B](../figures/extension/fig_development_interaction_offset.png)

图 3B. offset。

图 3. 非周期 EEG 参数的年龄依赖性组效应。

A. global aperiodic exponent 随年龄的模型预测关联（按组）。

B. global aperiodic offset 随年龄的模型预测关联（按组）。

group × age 交互对 exponent 与 offset 均显著。本研究为横断面设计，不应将上述模式解释为个体纵向发育轨迹。

### 3.5 空间分布（探索性）

ROI 混合模型：组别主效应不显著；部分 ROI 的 group×ROI 交互达到显著，具体系数见补充表。

通道 FDR：E33、E36、E37、E38 显著（TD > ASD），位于顶–枕部 HydroCel-64 电极位置。Topomap 仅反映头皮电极水平效应，不作皮层源定位推断。

![Figure 4](../figures/paper_ready_v2/fig3_spatial_distribution.png)

图 4. aperiodic exponent 组效应的空间分布（探索性）。

A. 各 ROI 上 TD − ASD 对 exponent 的边际效应（混合模型）。

B. 64 通道 OLS 回归系数头皮拓扑图（HydroCel-64 布局）；FDR q < .05 的通道以标记显示（E33、E36、E37、E38）。仅反映头皮电极水平，不作皮层源定位推断。

### 3.6 周期峰参数

alpha 峰功率、中心频率、带宽及 theta、beta 峰功率的 group 项均不显著（所有 p > 0.24）。

### 3.7 ASD 组内临床关联（探索性）

在 ASD 子样本（n = 61）中，探索性临床关联分析未发现经多重比较校正后仍显著的主效应（详见补充表 S5）。具体变量定义与量表映射待作者核实后于补充材料报告。

### 3.8 Split-half 信度

n = 138（见图 S1）。Spearman ρ：global exponent 0.959，SB = 0.979；global offset 0.960，SB = 0.980；alpha_pw 0.972，SB = 0.986。为记录内 epoch 分半一致性，非 test–retest。

## 4. 讨论

本研究在年龄跨度较大的 ASD 与 TD 儿童队列中，采用功率谱参数化（specparam）分离静息态 EEG 的非周期背景与周期振荡成分，系统评估了组间差异、年龄调节、空间分布、探索性临床关联及记录内稳定性。下文在既有结果基础上，从谱参数含义、与既往文献的关系、方法学启示及研究局限等方面展开讨论，而不将各小节写成与结果一一对应的复述清单。

### 4.1 主要发现

在控制年龄、性别、IQ 与可用 epoch 数后，本研究观察到 TD 儿童 global aperiodic exponent 高于 ASD（β = 0.079，SE = 0.031，p = .012，95% CI [0.018, 0.140]），对应 ASD 组非周期功率谱背景相对更平坦；未校正描述性均值亦支持该方向（ASD M = 1.69，TD M = 1.79）。Global aperiodic offset 仅呈 TD > ASD 趋势（β = 0.060，p = .095），提示组间差异在本队列中更集中地体现在 exponent 而非 offset 上。周期峰相关参数（alpha、theta、beta 峰功率、中心频率与带宽）在组水平上均未显示显著主效应（所有 group p > .24），说明传统意义上的振荡峰强度或峰频率并非本研究的主要组间分离维度。

在方法学层面，上述 exponent 组效应在嵌套协变量模型、拟合频段与 fixed 模式敏感性分析中方向一致；纳入平均 specparam 拟合质量或坏导数量后，TD > ASD 的方向仍保留。年龄方面，group × age 对 global exponent（β = .0033，p = .020）与 global offset（β = .0037，p = .021）的交互均达到显著，表明组间差异的幅度随年龄而变化，但须在横断面设计下谨慎解读（见 4.4 节）。探索性空间分析显示顶–枕部 HydroCel-64 通道（E33、E36、E37、E38）在 FDR 校正后显著，ROI 模型亦提示效应的空间非均匀性。奇偶 epoch 分半分析显示 global exponent、offset 与 alpha 峰功率的 Spearman ρ 为 0.959–0.972，Spearman–Brown 校正后均 > 0.97，表明主要 specparam 指标在同次记录内具有较高内部一致性。综合而言，本研究的主要贡献在于：在儿童静息态 EEG 中，以 aperiodic exponent 作为相对稳健的 ASD–TD 分离指标，并揭示其可能的发育阶段依赖性，同时表明周期峰参数在本队列中未提供额外的组间判别信息。

### 4.2 非周期 exponent 作为组间敏感谱特征

Aperiodic exponent 描述功率随频率升高而衰减的陡峭程度：数值较低表示 1/f 背景相对平坦，较高则表示斜率更陡。本研究中 ASD 组 exponent 低于 TD，应在“频谱整体形态”而非单一频段功率的框架下理解，这与传统 band power 或 alpha 峰高度所刻画的周期振荡强度属于不同维度。Neo et al.（2023）的系统综述提示，ASD 静息态 EEG 在传统频段指标上存在异质性结论，且多数研究未区分非周期背景对频段功率的贡献；Donoghue et al.（2020a）亦指出，频带比等指标可能反映非周期活动而非单纯的振荡增强。本研究在周期峰参数无显著组差的前提下观察到 exponent 组效应，支持 ASD–TD 差异在本队列中主要体现于非周期背景，而非周期峰参数的系统性偏移。

从机制讨论角度，aperiodic 指标与神经群体时间常数、兴奋–抑制（E/I）平衡等概念在模型与动物研究中被联系起来（Gao et al., 2017; Donoghue et al., 2020b），Manyukhina et al.（2022）在 MEG 中亦报告部分 ASD 儿童谱斜率更平坦，但其样本为 MEG、且存在智商亚组结构，与本研究静息态头皮 EEG 结果不宜直接等同。本研究未测量突触 E/I 或细胞外机制，亦不能由 exponent 降低推断“E/I 失衡”的确定性结论；更稳妥的表述是：ASD 儿童静息态宽频谱背景相对平坦，其神经生理学基础仍需结合模态、状态与发育因素进一步验证。

### 4.3 与学龄前 ASD 静息态 EEG 研究的比较

Chen et al.（2026）在 2–6 岁学龄前 ASD 与神经典型儿童中发现，组水平差异主要体现在 aperiodic offset（ASD 更高），而 slope/exponent 组间比较未达显著；周期峰参数组间多不显著，但 ASD 内 aperiodic/periodic 指标与语言能力相关。本研究结果与上述报告并不完全一致：本队列在协变量校正后显示 TD > ASD 的 **exponent** 效应，而 offset 仅为趋势（β = 0.060，p = .095）。这一差异不宜理解为相互矛盾，而更应放在样本年龄结构、参数维度与测量语境中理解。

首先，本研究主分析队列年龄约 40–131 月，仅 16.7%（23/138）处于 24–72 月，与 Chen et al.（2026）聚焦的学龄前窗口并不重合；分层分析中 ≤72 月层 exponent 组效应未达显著（β ≈ 0.055，p ≈ .47，n = 23），而 >72 月层显著（β ≈ 0.076，p ≈ .031），且全样本 group × age 交互显著。其次，exponent 与 offset 在本队列中相关（r ≈ 0.73）。补充联合模型分析显示，在控制 offset 后 exponent 的组效应仍保留，而在控制 exponent 后 offset 的组效应不显著，提示两参数对年龄与组别的敏感性可能不同；该结果仅作为参数维度区分的补充说明，不作为主结论。再次，语言与症状指标来源不同——本研究探索性语言分数与 Chen et al.（2026）所用标准语言评估并非同一测量体系，不宜将 ASD 内临床相关模式直接类比。上述要点共同表明，ASD 相关的 aperiodic EEG 异常可能具有 **发育阶段依赖性** 与 **临床异质性**；在跨研究比较时，应同时报告年龄分布、参数类型（exponent vs offset）及协变量结构，而非假定单一“ASD 谱斜率方向”适用于所有儿童期样本。

### 4.4 年龄依赖性效应

Group × age 交互是本研究相对于仅报告主效应的研究的重要扩展。Hill et al.（2022）在典型发育儿童中报告周期与非周期成分随年龄系统性变化；Wilkinson et al.（2024）在婴幼儿纵向 EEG 中观察到 aperiodic/periodic 成分的非线性发育轨迹。本研究在较大年龄跨度的横断面样本中检测到 group × age 对 exponent 与 offset 的显著交互，为理解“为何不同年龄段文献对 ASD aperiodic 指标的报告不一致”提供了线索：组间差异的幅度可能随年龄而调制，而非在所有月龄段保持恒定。

必须明确的是，本研究为 **横断面** 设计，交互项反映的是不同年龄点上组间差异的横断面模式，**不能** 解释为个体纵向发育轨迹，也不能推断因果性的成熟效应或“ASD 随年龄恶化/改善”的时间动态。未来研究需要覆盖婴幼儿至学龄期的 **纵向** EEG，并在同一分析框架下追踪 exponent 与 offset 的个体内变化，方可检验本研究提出的发育阶段依赖性假说。

### 4.5 空间分布

探索性 ROI 与通道分析提示，aperiodic exponent 的 TD–ASD 差异并非在所有头皮区域均匀分布。FDR 校正后，E33、E36、E37、E38 等顶–枕部 HydroCel-64 通道显示显著组间效应（TD > ASD），与全脑平均 global 指标的方向一致；ROI 混合模型中部分 group × ROI 交互达到显著，进一步支持空间非均匀性。然而，这些结果应严格限定在 **头皮电极水平**：顶–枕部电压变化可能反映后部皮层的突触活动、体积传导或参考方案的影响，**不能** 据此作出皮层源定位或特定脑区功能障碍的推断。本研究未进行源重建，空间发现应视为 **探索性**，有待独立样本、高密度电极布局或源定位方法复现与深化。

### 4.6 周期峰阴性结果与谱参数化的方法学意义

本研究中 alpha、theta、beta 等周期峰参数的组主效应均未达显著（所有 group p > .24），与 Chen et al.（2026）组水平 alpha 峰参数多不显著的结果在方向上部分一致，但二者样本年龄与协变量结构不同，比较时仍应保持克制。周期峰阴性结果的方法学含义在于：若仅依赖传统频段功率或峰高比较，可能将非周期背景的变化误判为“alpha 增强/减弱”等振荡性解释；specparam 将非周期与周期成分显式分离后，本队列的组间信号主要留在 aperiodic exponent 上，这与 Donoghue et al.（2020a, 2020b）关于 band power 混淆非周期活动的论述相呼应。因此，在 ASD 儿童静息态 EEG 研究中，报告 aperiodic exponent/offset 与周期峰参数并重，有助于提高结论的可解释性，避免将宽频谱形态差异简化为单一振荡频段效应。

### 4.7 临床相关性

本研究预设的 ASD 组内探索性临床关联（含 ADOS 相关指标与探索性语言分数）在 OLS 与 Spearman 分析中均未达显著，且未进行多重比较校正。据此，**不能** 将 global aperiodic exponent 表述为症状严重度或语言能力的生物标志物。与 Chen et al.（2026）报道的 ASD 内语言相关模式相比，本研究语言指标定义尚待作者终核，缺失率与量表来源亦不同，因而不宜将“阴性结果”解释为对既往研究的否定。

临床关联未显著的可能原因包括：样本量有限（ASD n = 61）、ASD 临床异质性高、症状与语言指标测量误差、以及 exponent 与行为表型之间可能存在的非线性或亚型特异性关联。未来研究可在明确变量定义的前提下，按语言能力、认知水平或 ADOS 亚型分层，检验 aperiodic 指标是否在特定临床亚群中更具变异解释力；此类分析应继续定位为 **探索性**，而非本研究主结论的延伸。

### 4.8 信度与方法学启示

奇偶 epoch 分半显示 global exponent、offset 与 alpha 峰功率在同次静息态记录内具有高度稳定性（ρ = 0.959–0.972，SB > 0.97），与 Karalunas et al.（2022）关于发育队列中 aperiodic 斜率可被稳定测量的报告方向一致。高 split-half 信度支持本研究组间比较所依赖的 subject-level 指标在记录内部具有可重复性，降低了“组效应由单次记录噪声驱动”的担忧。

需要强调的是，分半信度反映的是 **同一次会话内** 的 within-session 一致性，**不是** 跨日 test–retest，也 **不是** 跨实验室、跨设备或跨分析流水线的泛化信度。未来多中心研究应报告重测信度与测量不变性，并在预注册分析计划中明确 specparam 拟合与 QC 标准，以支持结果的可比性与可重复性。


### 4.9 自动 ICA 敏感性结果的解释与方法学意义（中英对照）

在自动 ICA 伪迹控制敏感性分析中，global exponent 的 TD > ASD 方向在 0.80/0.70 阈值下均得到保留，但效应量下降且 p 值未达显著。一个合理解释是，exponent 对高频肌电及眼动相关宽频背景较敏感，自动 ICA 与主流程在伪迹识别与剔除强度上的差异会改变可用于拟合的有效信号组成，从而削弱统计证据。与此同时，方向一致说明结果并非完全反转，更可能反映“效应强度被清洗策略调制”而非“主假设被推翻”。

方法学上，该结果强调儿童静息态 EEG 非周期分析应常规报告伪迹敏感性，并将自动化伪迹控制与主流程并列呈现。与 Chen et al.（2026）在学龄前样本更强调 offset 的结论相比，本研究在主流程中更突出 exponent、在自动 ICA 下表现为方向一致但减弱，进一步提示不同年龄结构、清洗流程与参数定义可能共同影响“offset vs exponent”哪一维度更易达到显著。

**English integration paragraph.** In the automated ICA artifact-control sensitivity analysis, the TD > ASD direction for global exponent was preserved at both thresholds (0.80/0.70), but the effect size was attenuated and no longer statistically significant. A plausible explanation is that exponent is sensitive to broadband high-frequency and ocular/myogenic contamination, and differences between automated ICA and the primary cleaning workflow can change the effective signal composition used for model fitting. The preserved direction argues against a full reversal and is more consistent with modulation of effect magnitude by cleaning strategy. Methodologically, pediatric resting-state aperiodic studies should routinely report artifact-sensitivity analyses. Relative to Chen et al. (2026), which emphasized offset in preschool samples, our pattern (primary exponent effect with attenuation under automated ICA) supports context dependence across developmental stage, cleaning pipeline, and parameter definition.

### 4.10 局限

本研究存在以下局限。第一，**横断面** 设计无法确立年龄相关效应的因果方向或个体内发育轨迹。第二，TD 组 IQ 高于 ASD，虽已纳入协变量，但残余混杂与能力–症状耦合仍可能存在。第三，两组 **性别分布不均衡**（ASD 5 女/56 男，TD 28 女/49 男，χ²，p < .001），主模型虽校正性别，亚组分析与性别特异性机制仍需更大样本验证。第四，临床与语言变量定义尚待终核，探索性临床分析结论受限。第五，ICA 与伪迹剔除策略 [待核实：ICA 参数与剔除策略]，且缺乏系统性逐被试人工复核。自动 ICA 敏感性分析使用 mne-icalabel/ICLabel，而非 HAPPE/MARA；自动分类性能可能受训练数据域差异、滤波带宽与儿童数据特征影响，因此该敏感性分析用于稳健性评估，不能取代主流程推断。Sixth, the automated ICLabel branch is informative for sensitivity but should not be interpreted as a replacement of the predefined primary pipeline because classifier behavior may vary with preprocessing assumptions and pediatric signal properties.第六，knee 模式敏感性分析方向与 fixed 模式一致，但统计证据较弱（p ≈ .08–.16）。第七，无源定位，空间结果仅限头皮水平。第八，缺少独立外部验证队列。第九，儿童 **睁眼静息** 状态可能受注意、眼动、疲劳与配合度影响，与闭眼静息或任务态研究的可比性需谨慎对待。

### 4.11 结论

综上所述，本研究提示 ASD 儿童静息态 EEG 的 global aperiodic exponent 低于 TD，表现为非周期功率谱背景相对更平坦；该效应在协变量与多种 QC 敏感性分析中方向较为一致，并呈现显著的年龄交互，且主要 specparam 指标在同次记录内分半信度很高。周期峰参数未显示显著组间差异，支持在本队列中将非周期 exponent 而非传统周期峰作为主要的组间敏感特征。上述发现应在横断面与设计约束下解读，不宜外推为 E/I 失衡的确定性证据或临床生物标志物。未来研究需结合 **纵向** 采样、**多中心** 验证及按年龄与临床表型分层的设计，进一步厘清 ASD aperiodic EEG 异常的发育时间进程及其与语言、认知症状的可重复关联模式。

## References

Chen, Y., Tsou, M., Nelson, C. A., & Tager-Flusberg, H. (2026). Resting state aperiodic and periodic EEG activity in preschool-aged autistic children: Differences from neurotypical peers and links to language skills. Molecular Autism, 17, Article 7. https://doi.org/10.1186/s13229-025-00700-1 [metadata verification required]

Donoghue, T., Dominguez, J., & Voytek, B. (2020a). Electrophysiological frequency band ratio measures conflate periodic and aperiodic neural activity. eNeuro, 7(6), Article ENEURO.0192-20.2020. https://doi.org/10.1523/ENEURO.0192-20.2020

Donoghue, T., Haller, M., Peterson, E. J., Varma, P., Sebastian, P., Gao, R., Noto, T., Lara, A. H., Wallis, J. D., Knight, R. T., Shestyuk, A., & Voytek, B. (2020b). Parameterizing neural power spectra into periodic and aperiodic components. Nature Neuroscience, 23(12), 1655–1665. https://doi.org/10.1038/s41593-020-00744-x

Gao, R., Peterson, E. J., & Voytek, B. (2017). Inferring synaptic excitation/inhibition balance from field potentials. NeuroImage, 158, 70–78. https://doi.org/10.1016/j.neuroimage.2017.06.065

Hill, A. T., Clark, G. M., Bigelow, F. J., Lum, J. A. G., & Enticott, P. G. (2022). Periodic and aperiodic neural activity displays age-dependent changes across early-to-middle childhood. Developmental Cognitive Neuroscience, 54, Article 101076. https://doi.org/10.1016/j.dcn.2022.101076

Karalunas, S. L., Gustafsson, H. C., Ostlund, B. D., Alperin, B. R., Deming, E. M., & Sullivan, E. L. (2022). Electroencephalogram aperiodic power spectral slope can be reliably measured and predicts ADHD risk in early development. Developmental Psychobiology, 64(3), Article e22228. https://doi.org/10.1002/dev.22228

Liang, S., & Mody, M. (2022). Abnormal brain oscillations in developmental disorders: Application of resting state EEG and MEG in autism spectrum disorder and fragile X syndrome. Frontiers in Neuroimaging, 1, Article 903191. https://doi.org/10.3389/fnimg.2022.903191

Manyukhina, V. O., Prokofyev, A. O., Galuta, I. A., Goiaeva, D. E., Obukhova, T. S., Stroganova, T. A., Orekhova, E. V., & Altukhov, D. I. (2022). Globally elevated excitation–inhibition ratio in children with autism spectrum disorder and below-average intelligence. Molecular Autism, 13, Article 20. https://doi.org/10.1186/s13229-022-00498-2

Pion-Tonachini, L., Kreutz-Delgado, K., & Makeig, S. (2019). ICLabel: An automated electroencephalographic independent component classifier, dataset, and website. NeuroImage, 198, 181–197. https://doi.org/10.1016/j.neuroimage.2019.05.026

MNE-ICALabel Developers. (n.d.). mne-icalabel (ICLabel integration for MNE-Python) [Computer software]. GitHub. https://github.com/mne-tools/mne-icalabel

Neo, W. S., Foti, D., Keehn, B., & Kelleher, B. (2023). Resting-state EEG power differences in autism spectrum disorder: A systematic review and meta-analysis. Translational Psychiatry, 13, Article 389. https://doi.org/10.1038/s41398-023-02681-2

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., & Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: Guidelines for reporting observational studies. PLoS Medicine, 4(10), Article e296. https://doi.org/10.1371/journal.pmed.0040296

Wilkinson, C. L., Yankowitz, L. D., Chao, J. Y., et al. (2024). Developmental trajectories of EEG aperiodic and periodic components in children 2–44 months of age. Nature Communications, 15, Article 5788. https://doi.org/10.1038/s41467-024-50204-4 [metadata verification required]


## Supplementary Materials
### Supplementary Table S1. Clinical and exploratory variables

| Variable | ASD (n = 61) | TD (n = 77) | p | Note |
|----------|--------------|-------------|-----|------|
| ADOS total | 14.1 ± 3.1 (n = 61) | — | — | ASD only |
| ADOS social affect | 9.3 ± 2.0 (n = 61) | — | — | ASD only |
| ADOS communication | 4.9 ± 1.3 (n = 61) | — | — | ASD only |
| Language score (exploratory) | 12.7 ± 3.1 (n = 55) | 18.0 ± 1.7 | — | Exploratory; definition pending verification |

Supplementary Table S1. Clinical and exploratory language variables. Language score mapping requires author verification before primary-text reporting.
### Supplementary Table S2. Sample inclusion flow

| Stage | N total | N ASD | N TD | Excluded | Reason |
| --- | --- | --- | --- | --- | --- |
| participants_total | 168.000 | 80.000 | 88.000 | — | — |
| included_final | 168.000 | 80.000 | 88.000 | 0.000 | not included_final=1 |
| preprocessing_success | 168.000 | 80.000 | 88.000 | 0.000 | preprocessing failed or no epochs |
| min_usable_epochs_pass | 145.000 | 65.000 | 80.000 | 23.000 | usable_epochs < 60 |
| specparam_subject_qc_pass | 138.000 | 61.000 | 77.000 | 7.000 | low_quality_subject (invalid channel ratio > threshold) |
| roi_available_after_specparam | 138.000 | 61.000 | 77.000 | 0.000 | — |
| main_analysis_complete_case | 138.000 | 61.000 | 77.000 | 0.000 | missing outcome/covariates or specparam QC fail |
### Supplementary Table S3. Age interaction models (summary)

| outcome | model_name | n | n_ASD | n_TD | term | coef | se | t | p | ci_low | ci_high | r_squared | aic | bic | highlight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_exponent | interaction_raw | 138.000 | 61.000 | 77.000 | Intercept | 1.806 | 0.145 | 12.480 | p < .001 | 1.519 | 2.092 | 0.149 | -140.016 | -119.525 | — |
| global_exponent | interaction_raw | 138.000 | 61.000 | 77.000 | C(group)[T.TD] | -0.202 | 0.123 | -1.645 | p = .102 | -0.444 | 0.041 | 0.149 | -140.016 | -119.525 | — |
| global_exponent | interaction_raw | 138.000 | 61.000 | 77.000 | age_months | -0.002 | 0.001 | -1.621 | p = .107 | -0.004 | 0.000 | 0.149 | -140.016 | -119.525 | — |
| global_exponent | interaction_raw | 138.000 | 61.000 | 77.000 | C(group)[T.TD]:age_months | 0.003 | 0.001 | 2.365 | p = .020 | 0.001 | 0.006 | 0.149 | -140.016 | -119.525 | — |
| global_offset | interaction_raw | 138.000 | 61.000 | 77.000 | Intercept | -9.586 | 0.165 | -57.987 | p < .001 | -9.913 | -9.259 | 0.153 | -103.204 | -82.713 | — |
| global_offset | interaction_raw | 138.000 | 61.000 | 77.000 | C(group)[T.TD] | -0.258 | 0.140 | -1.842 | p = .068 | -0.535 | 0.019 | 0.153 | -103.204 | -82.713 | — |
| global_offset | interaction_raw | 138.000 | 61.000 | 77.000 | age_months | -0.004 | 0.001 | -2.966 | p = .004 | -0.006 | -0.001 | 0.153 | -103.204 | -82.713 | — |
| global_offset | interaction_raw | 138.000 | 61.000 | 77.000 | C(group)[T.TD]:age_months | 0.004 | 0.002 | 2.341 | p = .021 | 0.001 | 0.007 | 0.153 | -103.204 | -82.713 | — |
Note. Full coefficient tables are provided in the supplementary data file.

### Supplementary Table S4. Periodic peak group models (summary)

| model | outcome | term | coef | std_err | pvalue | ci_low | ci_high | n_obs | r_squared | used_mixedlm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| periodic_peak | alpha_cf | C(group)[T.TD] | -0.124 | 0.107 | p = .247 | -0.335 | 0.087 | 145.000 | 0.209 | — |
| periodic_peak | alpha_pw | C(group)[T.TD] | 0.030 | 0.048 | p = .535 | -0.065 | 0.125 | 145.000 | 0.053 | — |
| periodic_peak | alpha_bw | C(group)[T.TD] | -0.120 | 0.103 | p = .247 | -0.324 | 0.084 | 145.000 | 0.065 | — |
| periodic_peak | theta_pw | C(group)[T.TD] | -0.010 | 0.029 | p = .729 | -0.066 | 0.047 | 145.000 | 0.085 | — |
| periodic_peak | beta_pw | C(group)[T.TD] | -0.005 | 0.028 | p = .858 | -0.060 | 0.050 | 145.000 | 0.071 | — |
### Supplementary Table S5. Clinical association models (exploratory)

| model | outcome | term | coef | std_err | pvalue | ci_low | ci_high | n_obs | r_squared | used_mixedlm | n_asd_complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| clinical_ols | ADOS_total | global_exponent | -3.938 | 2.954 | p = .188 | -9.858 | 1.982 | 61.000 | 0.066 | — | p = 61.000 |
| clinical_ols | ADOS_SA | global_exponent | -3.560 | 1.828 | p = .057 | -7.223 | 0.104 | 61.000 | 0.139 | — | p = 61.000 |
| clinical_ols | ADOS_communication | global_exponent | -1.367 | 1.194 | p = .257 | -3.760 | 1.025 | 61.000 | 0.081 | — | p = 61.000 |
| clinical_ols | language_score | temporal_exponent | -2.329 | 2.313 | p = .319 | -6.977 | 2.318 | 55.000 | 0.164 | — | p = 55.000 |
### Supplementary Table S6. Split-half reliability

| metric | n_subjects | pearson_r | pearson_p | spearman_rho | spearman_p | spearman_brown_pearson | spearman_brown_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_exponent | 138.000 | p = .961 | p < .001 | p = .959 | p < .001 | p = .980 | p = .979 |
| global_offset | 138.000 | p = .960 | p < .001 | p = .960 | p < .001 | p = .979 | p = .980 |
| alpha_pw | 138.000 | p = .982 | p < .001 | p = .972 | p < .001 | p = .991 | p = .986 |
### Supplementary Table S7. Frequency range and fixed/knee sensitivity

| freq_range | aperiodic_mode | n | coef_TD_vs_ASD | p | ci_low | ci_high | direction | significant_p05 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.0–35.0 Hz | fixed | 145.000 | 0.073 | p = .016 | 0.014 | 0.132 | TD > ASD | — |
| 1.0–35.0 Hz | knee | 145.000 | 0.098 | p = .127 | -0.028 | 0.224 | TD > ASD | — |
| 1.0–40.0 Hz | fixed | 145.000 | 0.078 | p = .022 | 0.012 | 0.145 | TD > ASD | — |
| 1.0–40.0 Hz | knee | 145.000 | 0.126 | p = .076 | -0.013 | 0.264 | TD > ASD | — |
| 2.0–35.0 Hz | fixed | 145.000 | 0.084 | p = .029 | 0.008 | 0.159 | TD > ASD | — |
| 2.0–35.0 Hz | knee | 145.000 | 0.113 | p = .163 | -0.046 | 0.271 | TD > ASD | — |
| 2.0–40.0 Hz | fixed | 145.000 | 0.093 | p = .031 | 0.009 | 0.178 | TD > ASD | — |
| 2.0–40.0 Hz | knee | 145.000 | 0.128 | p = .140 | -0.043 | 0.298 | TD > ASD | — |
### Supplementary Table S5 (continued). Spearman clinical correlations

| clinical | eeg_variable | rho | pvalue | n |
| --- | --- | --- | --- | --- |
| ADOS_total | global_exponent | -0.190 | p = .143 | 61.000 |
| ADOS_SA | global_exponent | -0.229 | p = .076 | 61.000 |
| ADOS_communication | global_exponent | -0.137 | p = .291 | 61.000 |
| language_score | temporal_exponent | -0.143 | p = .299 | 55.000 |

### Supplementary Table S3 (continued). Age-stratified group effects

| outcome | age_stratum | n_total | n_ASD | n_TD | ASD_mean | TD_mean | TD_minus_ASD_unadjusted | underpowered | coef_TD_vs_ASD_adjusted | se | p | ci_low | ci_high | r_squared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_exponent | preschool_like | 23.000 | 10.000 | 13.000 | 1.708 | 1.762 | 0.054 | — | 0.055 | 0.074 | p = .466 | -0.100 | 0.211 | 0.113 |
| global_exponent | older_child | 115.000 | 51.000 | 64.000 | 1.689 | 1.793 | 0.105 | — | 0.076 | 0.035 | p = .031 | 0.007 | 0.145 | 0.134 |
| global_exponent | tertile_1_youngest | 46.000 | 23.000 | 23.000 | 1.715 | 1.747 | 0.032 | — | 0.036 | 0.048 | p = .463 | -0.062 | 0.133 | 0.035 |
| global_exponent | tertile_2_middle | 46.000 | 23.000 | 23.000 | 1.700 | 1.769 | 0.069 | — | 0.029 | 0.064 | p = .657 | -0.100 | 0.157 | 0.078 |
| global_exponent | tertile_3_oldest | 46.000 | 15.000 | 31.000 | 1.644 | 1.832 | 0.188 | — | 0.183 | 0.059 | p = .003 | 0.065 | 0.301 | 0.358 |
| global_offset | preschool_like | 23.000 | 10.000 | 13.000 | -9.989 | -9.977 | 0.012 | — | 0.045 | 0.065 | p = .496 | -0.092 | 0.183 | 0.280 |
| global_offset | older_child | 115.000 | 51.000 | 64.000 | -10.118 | -10.070 | 0.048 | — | 0.048 | 0.041 | p = .246 | -0.033 | 0.129 | 0.070 |
| global_offset | tertile_1_youngest | 46.000 | 23.000 | 23.000 | -10.037 | -10.002 | 0.035 | — | 0.060 | 0.048 | p = .225 | -0.038 | 0.157 | 0.150 |

![figs1](../figures/extension/fig_split_half_reliability.png)

Supplementary Figure S1. Split-half reliability of specparam metrics within the recording session (not test–retest).

![figs2](../figures/compare_preschool_study/fig_fixed_vs_knee_effects.png)

Supplementary Figure S2. Fixed versus knee aperiodic mode sensitivity for global exponent TD − ASD effects.





### Supplementary Table S8. ICLabel artifact QC summary

| Threshold | Processed participants | Mean removed ICA components (per subject) | Mean removed fraction (%) | Mean retained artifact probability | Mean max retained artifact probability |
|-----------|------------------------|-------------------------------------------|---------------------------|------------------------------------|----------------------------------------|
| 0.80 | 138 | 3.01 | 10.02 | 0.092 | 0.676 |
| 0.70 | 138 | 3.82 | 12.73 | 0.072 | 0.576 |
| Combined | 276 (two-threshold runs) | 3.41 | 11.38 | 0.082 | 0.626 |

Supplementary Table S8. Summary of automated ICLabel artifact-control QC across thresholds. Values are derived from all successful ICLabel runs and presented in manuscript-friendly aggregated format.

### Supplementary Table S9. ICLabel vs Primary group effects

| Analysis | Outcome | n | β (TD − ASD) | 95% CI | p | Interpretation |
|----------|---------|---:|-------------:|--------|---:|----------------|
| Primary | Global exponent | 138 | 0.079 | [0.018, 0.140] | 0.012 | Primary reference |
| ICLabel 0.80 | Global exponent | 135 | 0.053 | [−0.013, 0.119] | 0.115 | Direction consistent, weaker evidence |
| ICLabel 0.70 | Global exponent | 137 | 0.053 | [−0.014, 0.121] | 0.119 | Direction consistent, weaker evidence |
| Primary | Global offset | 138 | 0.060 | [−0.011, 0.130] | 0.095 | Primary reference |
| ICLabel 0.80 | Global offset | 135 | 0.029 | [−0.049, 0.106] | 0.465 | Direction consistent, weaker evidence |
| ICLabel 0.70 | Global offset | 137 | 0.032 | [−0.046, 0.111] | 0.419 | Direction consistent, weaker evidence |

Supplementary Table S9. Comparison between primary and ICLabel-cleaned models with identical covariate structure (age_months, sex, IQ_total, usable_epochs).

![figs3](../figures/iclabel_sensitivity/fig_iclabel_vs_primary_forest.png)

Supplementary Figure S3. Forest plot of primary versus automated ICLabel sensitivity models for global exponent and global offset (effect size shown as β for TD − ASD with 95% confidence intervals).


## 作者需补充清单（投稿前）

### 伦理与诊断
- [待补充] ASD 诊断标准（DSM-5/ICD-11/ADOS-2 等）
- [待补充] TD 纳入标准
- [待补充] 排除标准完整列表
- [待补充] 伦理委员会名称与批准号
- [待补充] 知情同意程序

### 评估与变量
- [待补充] IQ 量表名称与施测说明
- [待补充] ADOS/ADOS-2 模块与评估者资质
- [待核实] language_score 与 ToMI/Resting_info 映射（探索性，仅补充表）
- [待核实] ADOS_communication、ADOS_SA 操作定义
- [待核实] ICA 参数与伪迹剔除策略

### 采集
- [待补充] EEG 采集指令、记录时长、阻抗标准

### 软件引用
- [citation needed] MNE-Python 正式文献条目

### 引用终核
- Chen et al. (2026)、Wilkinson et al. (2024)：metadata verification required（勿在未核对前修改卷期页码）
