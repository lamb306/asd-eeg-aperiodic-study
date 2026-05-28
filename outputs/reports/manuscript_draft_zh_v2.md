# 儿童静息态 EEG 非周期 1/f 参数的组间差异：一项基于 specparam 的横断面研究

> **稿件状态**：中文初稿 v2（投稿前结构性修订；统计结果与 v1 一致）  
> **主分析队列**：*N* = 138（ASD 61，TD 77）  
> **修订说明**：术语降调、ICA/临床变量待核实、正文图号调整（图 3 = 年龄交互）、内部路径移至可复现性附录

---

## 摘要

**背景**  
静息态脑电功率谱中的非周期（aperiodic）1/f 成分在文献中与神经兴奋–抑制（E/I）平衡、时间常数等生理过程**可能相关**，近年亦见于自闭症谱系障碍（ASD）相关研究。谱参数化（specparam）可将 1/f 背景与周期振荡峰分离。既往部分学龄前样本报告 ASD 组 aperiodic offset 升高而 exponent（斜率）组间差异不显著；在年龄范围较宽的儿童样本中，经严格质量控制后的 exponent 组效应、年龄调节模式及其测量稳定性尚待系统报告。

**方法**  
采用 EGI HydroCel-64 通道静息态睁眼 EEG（[待补充：采集场所、指令、伦理批号]）。经标准预处理、ICA 伪迹处理（[待核实：ICA 参数与剔除策略]）与 2 s 分段后，对可用 epoch ≥ 60 的被试进行 Welch PSD 与 specparam（fixed aperiodic，1–40 Hz）拟合。主分析在 specparam 被试级 QC 后纳入 138 人。以 global aperiodic exponent 为主要结局，global offset 为次要结局；协变量包括年龄、性别、IQ 及可用 epoch 数。分析包括 ROI/通道空间分布（探索性）、周期峰参数、**组别×年龄交互**、奇偶 epoch 分半信度及与学龄前文献对照的探索性分析。

**结果**  
协变量校正后，典型发育（TD）组 global exponent 高于 ASD 组（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]；未校正：ASD *M* = 1.69，*SD* = 0.14；TD *M* = 1.79，*SD* = 0.14）。Global offset 呈 TD > ASD 趋势（β = 0.060，*p* = 0.095）。**组别×年龄**对 exponent（β = 0.0033，*p* = 0.020）与 offset（β = 0.0037，*p* = 0.021）交互显著。fixed 模式多频段敏感性分析方向一致（*p* = 0.016–0.031）；knee 模式方向相同但证据较弱（*p* ≈ 0.08–0.16）。64 通道 FDR 校正后 E33、E36、E37、E38 显著（TD > ASD），分布于顶–枕部 HydroCel-64 电极位置。周期峰参数组间主效应均不显著（所有 group *p* > 0.24）。ASD 内临床关联未达显著（ADOS 社交子分 [待核实变量定义] OLS *p* = 0.057，Spearman *p* = 0.076）。奇偶分半 Spearman ρ：global exponent 0.959（SB = 0.979），global offset 0.960（SB = 0.980），alpha 峰功率 0.972（SB = 0.986）。

**结论**  
本队列（年龄约 40–131 月）中 ASD 与 TD 的静息态 1/f 背景差异主要体现在 exponent（斜率更平坦）而非周期 alpha 峰；组间差异随年龄而变化，**不宜**直接解释为纵向发育效应。结果在协变量与多频段敏感性分析中方向稳定，但受 IQ 与性别组间不均衡、横断面设计及空间探索性分析等限制。

**关键词**  
[待补充]；静息态脑电；非周期成分；specparam；自闭症；1/f 噪声；exponent

---

## 引言

静息态 EEG 功率谱在宽频段上常呈现 1/f 型非周期衰减，其斜率（exponent）与截距（offset）在文献中与不同的神经生理过程**可能相关**；其中 exponent 与 E/I 平衡、时间常数等的联系多为间接推断，需结合动物与干预研究谨慎解读。与传统频段功率或单一 alpha 峰指标相比，specparam 等谱分解方法可将非周期背景与周期振荡分离，有助于减少周期成分对组间比较的混杂。

自闭症谱系障碍的静息态 EEG 研究历史上关注频带功率、连接性与熵等指标；关于非周期参数的报告相对较新。已有**学龄前**样本研究发现，ASD 儿童 aperiodic offset 可能升高，而 exponent 组间差异不显著，提示不同发育阶段或指标维度上的效应可能并不一致。然而，针对**年龄范围较宽的儿童样本**、在统一预处理与拟合 QC 标准下的 exponent 主效应、**年龄调节**、空间分布、协变量稳健性以及测量信度的综合报告仍相对有限。

本研究利用 EGI HydroCel-64 静息态睁眼 EEG 数据，在预设分析流水线上，以 global aperiodic exponent 为主要结局，系统检验 ASD 与 TD 的组间差异，并重点报告组别×年龄交互、offset、空间分布（探索性）、周期峰参数、分半信度及临床探索性关联。研究目的为：（1）在协变量校正后评估组间 exponent 差异；（2）检验组别差异是否随年龄而变化；（3）检验结果对模型设定与频段的稳健性；（4）描述空间分布探索性模式；（5）区分非周期与周期峰贡献；（6）评估 epoch 分半一致性。本文不旨在建立临床诊断工具，亦不对皮层源定位作推断。

---

## 方法

### 研究设计与伦理

本研究为横断面观察性设计，比较 ASD 与 TD 儿童的静息态 EEG 非周期参数。[待补充：研究机构名称]。[待补充：伦理委员会全称及批准号]。[待补充：知情同意程序（儿童/监护人）]。

### 被试

**纳入与分组**  
[待补充：ASD 诊断标准（如 DSM-5）、诊断工具（如 ADOS-2 阈值）、评估者资质]。[待补充：TD 组纳入与排除标准（发育史、共病、家族史等）]。[待补充：年龄纳入范围及招募渠道]。

具备可分析静息态 EEG 及配套人口学/临床变量的初始样本共 **168** 人（ASD 80，TD 88）。

**样本流失与主分析队列**  
经预处理后，**145** 人达到可用 epoch ≥ 60（2 s 分段）；**23** 人因可用 epoch < 60 排除（145 人：ASD 65，TD 80）。另有 **7** 人因 specparam 被试级 QC 未通过（无效通道比例 > 20%）排除，主分析 **138** 人（ASD 61，TD 77）。纳入流程见补充图 S1。

**人口学与临床特征（主分析队列）**  
两组年龄（月）无显著差异（ASD 85.7 ± 16.9，TD 88.8 ± 19.6，*p* = 0.319）。TD 组 IQ 总分高于 ASD（95.0 ± 15.2 vs 113.2 ± 14.6，*p* < 0.001）。性别分布不均衡（ASD 女/男 56/5，TD 49/28，*p* = 0.0003），所有组间模型均校正性别与 IQ。

临床变量用于探索性分析，定义需作者最终确认：[待核实变量定义] **`ADOS_communication`**（数据库字段，来源 Resting_info Communication 子分，**非**标准 ADOS RRB 域）；[待核实变量定义] **`ADOS_RRB`**（本队列无有效数据）；[待核实变量定义] **`ADOS_SA`**（来源 Resting_info Social 子分）；[待核实变量定义] **`language_score`**（映射 ToMI_Total）。详见补充表「临床变量映射核查」。

### EEG 采集

[待补充：实验室环境、静息指导语、屏幕/玩具、阻抗标准、记录时长现场执行细节]。

系统与记录参数：EGI HydroCel GSN-64 1.0；NetStation 格式；原始采样率 500 Hz；记录时长约 300 s；**睁眼静息**；原始参考 Cz（VREF）；保留头皮电极 E1–E64。[待补充：上述参数与现场执行是否一致的核对记录]

### 预处理

重采样至 250 Hz；0.5–45 Hz 带通；50 Hz 陷波；平均参考；2 s 不重叠 epoch；峰峰值振幅 > 500 µV 的 epoch 剔除。

**ICA**  
[待核实：ICA 参数与剔除策略]（包括但不限于：分解方法、成分数设定、自动/人工剔除规则、EOG/肌电判定依据）。**未进行系统性的逐被试人工 ICA 复核**（见局限）。主分析队列中约 43% 被试记录为未剔除任何 ICA 成分（具体含义依赖最终核实的剔除策略）。

### 功率谱与 specparam

**PSD**  
Welch 方法，1–40 Hz；被试内各通道 PSD 用于后续拟合。

**specparam 拟合**  
- 模式：**fixed** aperiodic（主分析）；敏感性分析含 **knee** 模式。  
- 拟合频段：1–40 Hz（主分析）；敏感性含 2–40、1–35、2–35 Hz。  
- 被试级 **global exponent / offset**：通过 QC 的通道上 exponent/offset 的算术平均。

**拟合与纳入 QC**  
- 通道级：拟合 *R*² ≥ 0.90；exponent 在预设生理范围内。  
- 被试级：无效通道比例 ≤ 20% 纳入主分析；否则排除。  
- 主分析队列两组平均拟合 *R*² 均 > 0.98（ASD 略低于 TD，*p* = 0.006；已作稳健性检验）。

### 结局指标

| 类型 | 指标 |
|------|------|
| 主要 | 被试级 global aperiodic exponent |
| 次要 | 被试级 global aperiodic offset |
| 重点报告 | 组别×年龄对 exponent/offset 的交互 |
| 探索性 | ROI/通道 exponent；周期峰（alpha_cf、alpha_pw、alpha_bw 等）；临床关联 |

### 空间分析

**ROI**  
将 64 电极分为 frontal、central（参照）、temporal、parietal、occipital 五区（初步分组，不作解剖强推断）。

**ROI 混合模型**  
`exponent ~ C(group) × C(roi) + age_months + C(sex) + IQ_total + usable_epochs + (1|subject)`，线性混合模型（MixedLM），被试随机截距；报告组别主效应、交互效应及相对 central 的边际 TD−ASD 对比（正文图 4A）。

**通道水平**  
64 通道分别拟合与主分析相同协变量的 OLS；对组间系数进行 Benjamini–Hochberg FDR 校正（64 次检验）。Topomap **仅表示电极位置的系数分布，不作皮层源定位推断**（正文图 4B）。

### 统计检验

**主分析**  
`global_exponent ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs`（OLS）；参照组为 ASD，`C(group)[T.TD]` 表示 TD 相对 ASD 的增量。`global_offset` 采用相同模型。显著性水平 α = 0.05（双侧）。

**年龄交互（正文重点）**  
`outcome ~ C(group) × age_months + C(sex) + IQ_total + usable_epochs`；报告 exponent 与 offset 的交互项（正文图 3）。

**稳健性**  
嵌套模型：仅组别；+ 年龄/性别；+ IQ；+ 可用 epoch（主模型）；+ 平均拟合 *R*²；+ 坏导数量。

**敏感性**  
不同拟合频段、fixed/knee 模式、最少 epoch 阈值（30 vs 60）。

**周期峰**  
`alpha_cf`、`alpha_pw`、`alpha_bw` 及 theta/beta 峰功率等，模型协变量同主分析（正文图 5A–B，*n* = 138）。

**分半信度**  
每名被试 epoch 按奇偶分为两半，独立估计 PSD 与 specparam，计算 Spearman 相关及 Spearman–Brown 校正。**该程序评估单次记录内的 epoch 子样本一致性，不是跨日 test–retest 重测信度**（结果见正文，图见补充材料）。

**临床探索**  
仅 ASD（*n* = 61）；OLS 与 Spearman 相关 global exponent 与 ADOS 总分、[待核实变量定义] `ADOS_SA`、`ADOS_communication`、颞叶 ROI exponent 与 [待核实变量定义] `language_score`（*n* = 55）。

### 软件

Python 3；MNE-Python、specparam、statsmodels、pandas、SciPy、matplotlib 等。[待补充：各库具体版本号与运行环境记录]

---

## 结果

### 样本与数据质量

初始可分析样本 168 人（ASD 80，TD 88）。epoch ≥ 60 后 145 人（ASD 65，TD 80）；specparam QC 后主分析 138 人（ASD 61，TD 77）（补充图 S1）。

主分析队列年龄范围约 40–131 月。其中 ≤ 72 月者 *n* = 23（16.7%）；> 72 月者构成多数。组平均 PSD 与代表被试 specparam 拟合见图 1；拟合质量肉眼 QC 见补充图（specparam QC 示例）。

### 主要结局：global aperiodic exponent

协变量校正后，TD 组 global exponent 高于 ASD（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]，*n* = 138）（图 2A）。

未校正描述统计：ASD *M* = 1.69，*SD* = 0.14；TD *M* = 1.79，*SD* = 0.14。

### 次要结局：global aperiodic offset

TD 组 offset 高于 ASD 的趋势（β = 0.060，*p* = 0.095，*n* = 138）（图 2B）。

### 组别×年龄交互（正文重点）

`group × age_months` 对 global exponent（β = 0.0033，*p* = 0.020）与 global offset（β = 0.0037，*p* = 0.021）均显著（*n* = 138）（图 3；完整系数见补充表 S4）。

≤ 72 月龄亚组 *n* = 23，该层 exponent 组效应 *p* ≈ 0.47；> 72 月龄层 β ≈ 0.076，*p* ≈ 0.031（探索性分层，补充材料）。

### 稳健性与敏感性

**协变量嵌套模型**（图 2C）：各模型 TD > ASD 方向一致；仅组别 β = 0.096，*p* < 0.001；主模型（+ epoch）β = 0.079，*p* = 0.012；+ 平均 *R*² 后 β = 0.056，*p* = 0.030；+ 坏导 β = 0.081，*p* = 0.011。主分析队列无 IQ < 70 被试。

**频段与 aperiodic 模式**：fixed 模式下 1–40、2–40、1–35、2–35 Hz 组效应 *p* = 0.016–0.031；knee 模式方向一致，*p* ≈ 0.08–0.16。最少 epoch 阈值 30 与 60 时 β ≈ 0.074，*p* ≈ 0.019（补充表 S3）。

### 分半信度

奇偶 epoch 分半（*n* = 138）：global exponent Spearman ρ = 0.959，SB = 0.979；global offset ρ = 0.960，SB = 0.980；alpha 峰功率（alpha_pw）ρ = 0.972，SB = 0.986（补充表 S5；补充图 S4）。

### 空间分布（探索性）

**ROI 混合模型**（*n*~obs = 687）：组别主效应 *p* = 0.44；部分 ROI 的 group×ROI 交互达到显著，具体系数见补充表 S7；图 4A 为相对 central 的边际 TD−ASD 效应。

**通道 FDR**：E33、E36、E37、E38 在 FDR *q* < 0.05 下显著，方向均为 TD > ASD（图 4B）。按 HydroCel-64 布局，上述电极位于顶–枕过渡及枕区附近。**Topomap 仅反映电极水平效应，不作皮层源定位推断。**

### 周期峰参数

在主分析队列（*n* = 138）中，alpha 峰功率（协变量校正 group *p* ≈ 0.68）、alpha 中心频率（*p* ≈ 0.26）等周期峰指标组间差异均不显著；所有周期峰模型中 group 项 *p* > 0.24。theta、beta 峰功率组间主效应亦不显著（图 5A–B）。

### 临床关联（探索性；仅 ASD）

*n* = 61。Global exponent 与 ADOS 总分（OLS *p* = 0.188；Spearman *p* = 0.143）、[待核实变量定义] `ADOS_communication`（OLS *p* = 0.257）均无显著关联。  
[待核实变量定义] `ADOS_SA` 与 global exponent：OLS *p* = 0.057；Spearman ρ = −0.229，*p* = 0.076（图 5C）。  
颞叶 ROI exponent 与 [待核实变量定义] `language_score`（*n* = 55）：OLS *p* = 0.319。  
上述分析均为探索性，未校正多重比较。

---

## 讨论

### 主要发现概括

本研究在 specparam QC 后的 138 名**年龄范围较宽的儿童**样本（约 40–131 月）中，发现协变量校正后 TD 组 global aperiodic exponent 高于 ASD 组，与 ASD 静息态 1/f 背景相对**更平坦**（高频相对低频衰减更缓）的描述一致。该效应在协变量嵌套模型与 fixed 模式多频段敏感性分析中方向一致；global offset 仅呈较弱趋势。

与此同时，**组别×年龄交互显著**（图 3），提示组间差异的幅度随年龄而变化；鉴于横断面设计，该结果**不能**解释为纵向发育轨迹。周期峰参数未见显著组间差异，与 specparam 分解下组间差异主要见于**非周期 exponent** 而非 alpha 周期成分的发现一致。

### 与 exponent、offset 及文献的关系

探索性对照显示，global exponent 与 offset 相关约 *r* = 0.73；控制 offset 后 exponent 组效应仍 *p* ≈ 0.048，而控制 exponent 后 offset 组效应不显著。这与既往部分**学龄前**样本强调 offset 升高而 exponent 不显著的报告并不完全一致。本样本仅约 16.7% 被试 ≤ 72 月，该亚组内 exponent 组效应 *p* ≈ 0.47；在 > 72 月层效应更明显（*p* ≈ 0.031）。更审慎的表述是：**非周期指标的表现可能随样本年龄结构而变化**，而非简单“重复”或“否定”既往研究。[待补充：Chen 等学龄前研究的完整文献信息]

### 年龄交互的含义

组别×年龄交互是正文重点结果之一。在控制 IQ、性别等协变量后，组间 exponent/offset 差异随年龄而变化。必须强调：本研究为**横断面**设计，该交互**不能**解释为个体纵向发育轨迹或成熟因果效应，亦不能替代纵向追踪数据。未来研究需在不同年龄波段独立采样或纵向追踪中验证。

### aperiodic exponent 与生理机制

文献中常将 1/f exponent 与 E/I 平衡、时间常数等相联系；本研究仅提供组间关联与分解指标，**不能**据此断言 exponent 直接“反映”E/I 失衡。更合适的表述是：结果与既往关于 ASD 网络时间动力学假说**可能一致**，仍需多模态与因果设计验证。

### 空间探索性结果

部分 ROI 的 group×ROI 交互达到显著；顶–枕通道 FDR 显著均属探索性，且基于电极空间布局。后部效应可能与视觉–注意相关头皮活动、alpha 分布或容积传导等因素有关；**在没有源定位与多模态证据的情况下，不应将 E37 等电极位置直接表述为“枕叶皮层异常”**。

### 临床关联

ASD 子样本内未见 exponent 与 ADOS 总分或 [待核实变量定义] Communication 字段的显著关联；[待核实变量定义] Social 子分仅呈趋势。考虑到样本量、探索性分析、[待核实变量定义] 测量含义及 EEG 与临床评估的时间对齐局限，**不能**据此否定生物学关联，亦**不能**声称 exponent 可作为症状严重程度生物标志物。

### 信度

奇偶分半相关高，说明在单次记录内 epoch 子样本上 aperiodic 估计较稳定。需再次明确：该指标**不是**跨日 test–retest 重测信度，对外部推广至不同日、不同状态记录时应谨慎。

### 方法学优势与不足

优势包括：统一分析流水线、specparam QC、主效应稳健性与敏感性报告、周期与非周期分离、正文报告年龄交互。  
不足见下节。

---

## 局限

1. **横断面设计**：无法推断发育因果；年龄交互仅反映组间差异随年龄的变化模式。  
2. **组间协变量不均衡**：TD 组 IQ 显著高于 ASD（*p* < 0.001），虽已纳入协变量，残余混杂仍可能存在；主分析无 IQ < 70 被试，结论不能推广至智力显著受损亚群。  
3. **性别分布不均衡**：ASD 组男性比例远低于 TD，虽已校正，残余影响不能排除。  
4. **ICA 与伪迹**：[待核实：ICA 参数与剔除策略]；无系统人工复核；约半数被试未剔除任何 ICA 成分，伪迹控制可能不足。  
5. **诊断与临床数据**：[待补充：诊断流程细节]；[待核实变量定义] `ADOS_communication`、`ADOS_RRB`、`language_score` 等；SRS 等变量在 ASD 中缺失，无法检验。  
6. **采集信息缺失**：[待补充：环境、指令、药物、共病、睡眠与行为状态]。  
7. **空间推断**：电极 topomap 与 ROI 不能用于皮层源定位。  
8. **多重比较**：通道 FDR、临床探索性分析等需按探索性解读。  
9. **重测信度**：无跨日 test–retest。  
10. **因果与机制**：EEG 1/f 与 E/I 平衡的关系为间接推断，本研究未直接测量 E/I。

---

## 结论

在通过严格 epoch 与 specparam QC 的 138 名儿童静息态 EEG 样本（年龄约 40–131 月）中，TD 组 global aperiodic exponent 显著高于 ASD 组，ASD 表现为更平坦的 1/f 背景；global offset 仅呈趋势。**组别×年龄交互显著**，提示组间差异随年龄而变化，但**不宜**表述为纵向发育轨迹。效应在 fixed 模式多频段敏感性分析中方向一致，奇偶 epoch 分半信度高。周期峰参数未见显著组间差异；后部电极探索性显著。结果支持在年龄匹配、协变量均衡的独立样本中复现，并区分非周期 exponent 与 offset；**不宜**将本研究单一指标用于临床诊断，**不宜**将电极水平效应解释为皮层源异常。

---

## 图表清单

### 正文图

| 编号 | 图名（文件基名） | 内容 |
|------|------------------|------|
| 图 1 | fig1_psd_specparam_overview | A：代表被试 PSD 与 specparam 拟合；B：组平均 PSD（±1 SEM） |
| 图 2 | fig2_main_aperiodic_effects | A：global exponent；B：global offset；C：稳健性森林图 |
| **图 3** | **fig_development_interaction_*** | **组别×年龄对 exponent/offset 的交互（正文重点）** |
| 图 4 | fig3_spatial_distribution | A：ROI 边际 TD−ASD；B：通道 topomap（FDR：E33/E36/E37/E38） |
| 图 5 | fig4_periodic_clinical_exploratory | A–B：alpha 峰功率/中心频率；C：ASD 内 exponent vs ADOS_SA |

> **排版说明**：投稿前建议将现有 `fig_development_interaction_exponent` / `offset` 图统一编号为正文图 3；原 fig3、fig4 顺延为图 4、图 5（或按期刊要求合并子图）。

### 补充图

| 编号 | 内容 |
|------|------|
| 图 S1 | CONSORT 样本纳入流程（supp_consort_flow_paper） |
| 图 S2 | 与学龄前文献对照（分层、offset–exponent 等） |
| 图 S3 | specparam 拟合 QC 示例 |
| 图 S4 | 奇偶 epoch 分半信度 |

### 表

| 编号 | 内容 |
|------|------|
| 表 1 | 主分析队列人口学/临床（*N* = 138） |
| 表 2 | EEG/specparam 质量组间比较 |
| 表 S1 | 各阶段样本量（纳入流程） |
| 表 S2 | 稳健性模型系数 |
| 表 S3 | 频段/模式敏感性 |
| 表 S4 | 年龄交互模型 |
| 表 S5 | 分半信度 |
| 表 S6 | FDR 显著通道 |
| 表 S7 | ROI 混合模型（完整系数） |
| 表 S8 | 临床变量映射核查 |

---

## 附录 A：可复现性说明（供作者与审稿，不纳入正文）

分析流水线配置见项目根目录 `config/config.yaml`；脚本序列为 00–21。主要统计输出位置示例：

| 内容 | 相对路径 |
|------|----------|
| 主效应 OLS | `derivatives/stats/main_group_analysis.csv` |
| 描述统计 | `outputs/tables/global_exponent_descriptives.csv` |
| 稳健性 | `outputs/tables/global_exponent_robustness_models.csv` |
| 敏感性 | `derivatives/stats/sensitivity_analysis_final.csv` |
| 年龄交互 | `outputs/tables/extension/development_interaction_models.csv` |
| 分半信度 | `outputs/tables/extension/split_half_reliability.csv` |
| ROI 混合模型 | `derivatives/stats/roi_mixed_model.csv` |
| FDR 通道 | `outputs/tables/significant_channels_fdr.csv` |
| 周期峰 | `derivatives/stats/periodic_peak_analysis.csv` |
| 临床 OLS/Spearman | `derivatives/stats/clinical_correlation_*.csv` |
| 纳入流程 | `outputs/tables/sample_inclusion_flow.csv` |
| 表 1（主分析） | `outputs/tables/table1_main_cohort_*.csv` |
| 正文图 | `outputs/figures/paper_ready_v2/` |
| 年龄交互图 | `outputs/figures/extension/` |

修改统计结论前请重新运行对应脚本并核对上述文件。

---

## 附录 B：作者必须补充的信息清单

投稿前请逐项核对；文中 **[待补充]** 与 **[待核实：…]** 须在定稿前处理或写入补充材料。

### 一、伦理与合规

| 序号 | 项目 | 状态 |
|------|------|------|
| B1 | 伦理委员会全称、批准号 | [待补充] |
| B2 | 知情同意类型（儿童/监护人）与签署日期 | [待补充] |
| B3 | 临床试验/观察性研究注册号（如有） | [待补充] |

### 二、被试与诊断

| 序号 | 项目 | 状态 |
|------|------|------|
| B4 | ASD 诊断标准（DSM-5 等）与评估工具 | [待补充] |
| B5 | ADOS-2 模块、校准分、评估者与 EEG 间隔 | [待补充] |
| B6 | TD 纳入/排除标准（发育史、共病、家族史） | [待补充] |
| B7 | 招募渠道、时间与地理范围 | [待补充] |
| B8 | 种族/民族、利手、共病、用药（若未录入数据库） | [待补充] |

### 三、EEG 采集与预处理

| 序号 | 项目 | 状态 |
|------|------|------|
| B9 | 实验室环境、指导语、注视点、阻抗标准 | [待补充] |
| B10 | 记录当日行为状态、睡眠、是否服药 | [待补充] |
| B11 | **ICA 成分数、算法、自动剔除规则、是否人工复核** | **[待核实：ICA 参数与剔除策略]** |
| B12 | 配置文件与现场执行一致性签字核对 | [待补充] |

### 四、临床变量定义（必核）

| 序号 | 变量 | 状态 |
|------|------|------|
| B13 | `ADOS_communication` 与 Resting_info / ADOS-2 标准子分对应关系 | **[待核实变量定义]** |
| B14 | `ADOS_RRB` 为何全缺失、是否应改用其他字段 | **[待核实变量定义]** |
| B15 | `ADOS_SA` 与 ADOS Social Affect 标准命名是否一致 | **[待核实变量定义]** |
| B16 | `language_score` / ToMI 版本、常模与中文适用性 | **[待核实变量定义]** |
| B17 | SRS 等未纳入变量的原因说明（文稿局限段） | [待补充] |

### 五、文献、作者与投稿

| 序号 | 项目 | 状态 |
|------|------|------|
| B18 | Chen 等学龄前研究及关键 1/f–ASD 文献完整引用 | [待补充] |
| B19 | 作者单位、ORCID、通讯作者 | [待补充] |
| B20 | 基金资助、利益冲突、数据/代码可用性声明 | [待补充] |
| B21 | 中英文题目、关键词、Running title 定稿 | [待补充] |
| B22 | 软件精确版本号（MNE、specparam、Python 等） | [待补充] |

### 六、图表与排版

| 序号 | 项目 | 状态 |
|------|------|------|
| B23 | 正文图 3：年龄交互图从补充材料提升至正文并完成编号 | 待排版 |
| B24 | 表 1/表 2 按期刊格式排版（Word/LaTeX） | 待排版 |
| B25 | 补充表 S7 ROI 交互完整系数表 | 待导出 |
| B26 | 图注中英文定稿（含 CONSORT、年龄交互、分半信度） | 待排版 |

### 七、可选（审稿人可能要求）

| 序号 | 项目 | 状态 |
|------|------|------|
| B27 | 周期峰分析是否严格基于 *n* = 138 重跑并附对照说明 | 可选 |
| B28 | 全样本 *N* = 168 与主分析 *N* = 138 的 Table 1 对照脚注 | 可选 |

---

*v2 修订：未改动任何报告统计量；仅结构调整、术语降调、图号建议与路径外移。定稿前请以分析流水线最新输出为准核对。*
