可以。我先给你写一版**正式中文论文初稿 v3**，它会比 Cursor 那版更像期刊论文。下面这版已经加入核心文献引用、正式论文语气、结果主线和讨论逻辑；所有我不能替你确认的信息都用 **[待补充]** 或 **[待核实]** 标出来，避免编造。

---

# 自闭症谱系障碍儿童静息态 EEG 非周期性成分异常及其年龄依赖性：基于功率谱参数化的研究

## 摘要

**背景：** 静息态 EEG 功率谱不仅包含传统意义上的周期性振荡成分，也包含非周期性 1/f 背景活动。传统频段功率分析往往难以区分真正的振荡峰与宽频非周期背景变化。近年来，功率谱参数化方法被用于将神经功率谱分解为非周期成分和周期峰成分，为研究自闭症谱系障碍儿童的静息态神经生理特征提供了新的工具。Donoghue 等提出的功率谱参数化方法可将神经功率谱建模为非周期背景和周期峰的组合，避免将二者混合解释。([PubMed][1])

**目的：** 本研究旨在比较自闭症谱系障碍儿童与典型发育儿童静息态 EEG 的非周期性和周期性功率谱参数，重点检验 global aperiodic exponent 的组间差异、空间分布、年龄依赖性、临床关联以及指标稳定性。

**方法：** 本研究纳入 168 名具有静息态睁眼 EEG 数据及基本元数据的儿童，其中 ASD 80 名，TD 88 名。经预处理、最少可用 epoch 标准和 specparam 拟合质量控制后，138 名被试进入主分析，包括 ASD 61 名和 TD 77 名。EEG 采用 EGI HydroCel-64 系统采集，原始数据为 `.mff` 格式。使用 Welch 方法估计 1–40 Hz 功率谱，并使用 specparam fixed aperiodic 模式对每个被试、每个通道的功率谱进行参数化。主要结局为被试水平 global aperiodic exponent。主模型控制年龄、性别、IQ_total 和可用 epoch 数。进一步进行了协变量稳健性、频段敏感性、fixed/knee 模式比较、ROI 与通道水平探索、周期峰分析、临床相关、年龄交互以及 split-half 信度分析。

**结果：** TD 组 global aperiodic exponent 显著高于 ASD 组（β = 0.079，SE = 0.031，p = 0.012，95% CI [0.018, 0.140]）。未校正描述统计显示，ASD 组 global exponent 均值为 1.69（SD = 0.14），TD 组为 1.79（SD = 0.14）。该组效应在控制 IQ、可用 epoch、拟合质量和坏导数量后仍保持稳定。Global offset 显示 TD 高于 ASD 的趋势，但未达到传统显著性水平（β = 0.060，p = 0.095）。Fixed 模式下不同拟合频段均显示一致方向的组间效应，而 knee 模式方向一致但统计证据较弱。年龄交互分析显示，group × age 对 global exponent 和 global offset 均显著，提示 ASD–TD 的非周期 EEG 差异可能随年龄变化。通道水平 FDR 校正分析显示，E33、E36、E37 和 E38 表现出显著组间差异，方向均为 TD > ASD，位于 HydroCel-64 顶–枕部头皮通道。周期峰参数未显示显著组间差异。ASD 组内临床相关分析未达到传统显著性阈值。Split-half 分析显示 global exponent、global offset 和 alpha peak power 均具有很高的内部稳定性，Spearman-Brown 校正信度均高于 0.97。

**结论：** ASD 儿童静息态 EEG 表现出较低的 global aperiodic exponent，提示其非周期背景活动存在异常。该差异在多种协变量和质量控制条件下保持稳健，并可能具有年龄依赖性。相比传统周期峰参数，aperiodic exponent 可能更敏感地反映 ASD 儿童静息态神经生理差异。未来需要纵向、多中心和外部验证研究进一步确定该指标的发育意义和临床价值。

**关键词：** 自闭症谱系障碍；静息态 EEG；非周期成分；aperiodic exponent；specparam；功率谱参数化；儿童；神经发育

---

# 1. 引言

自闭症谱系障碍（autism spectrum disorder, ASD）是一类以社会沟通困难和限制性、重复性行为为核心特征的神经发育障碍。尽管 ASD 的行为诊断标准相对明确，但其神经生理机制高度异质。静息态 EEG 具有非侵入、时间分辨率高、对儿童友好等特点，因此被广泛用于研究儿童神经发育障碍中的脑功能特征。与任务态 EEG 相比，静息态 EEG 对儿童配合要求较低，更适合用于年龄跨度较大、临床异质性较高的 ASD 儿童样本。

传统 EEG 频谱研究通常关注 theta、alpha、beta 等预定义频段功率。然而，传统频段功率并不只反映真正的周期性神经振荡，也受到宽频非周期背景活动的影响。换言之，某一频段功率的变化可能来自该频段振荡峰的增强，也可能来自整体 1/f 背景斜率或偏移的改变。因此，单纯依赖传统频段功率可能会混淆周期峰和非周期背景，使神经生理解释变得不明确。

功率谱参数化方法为解决这一问题提供了重要工具。Donoghue 等提出的 FOOOF/specparam 方法将神经功率谱分解为非周期背景成分和叠加其上的周期峰成分，从而分别估计 aperiodic exponent、aperiodic offset 以及周期峰中心频率、峰功率和带宽等参数。([PubMed][1]) 其中，aperiodic exponent 描述功率谱随频率升高而衰减的陡峭程度；较高 exponent 表示频谱斜率更陡，而较低 exponent 表示频谱相对更平坦。Aperiodic offset 则反映整体宽频功率背景水平。需要强调的是，虽然 aperiodic 指标常被讨论为与神经群体活动、时间常数或兴奋–抑制状态有关，但其生理解释并非单一，不能简单等同于某一种神经机制。

已有研究提示 ASD 儿童可能存在非周期 EEG 异常，但具体表现尚不一致。Manyukhina 等报告，ASD 儿童，尤其是低于平均 IQ 的 ASD 儿童，表现出更平坦的 aperiodic spectral slope，这被作者解释为可能与兴奋–抑制比例改变有关。([PubMed][2]) 然而，近期一项针对 2–6 岁学龄前 ASD 儿童的静息态 EEG 研究发现，ASD 儿童 aperiodic offset 高于神经典型儿童，而 aperiodic slope/exponent 未显示显著组间差异；该研究还报告 aperiodic 和 periodic EEG 指标与语言能力存在关联。([PMC][3]) 这些发现提示 ASD 中的 aperiodic EEG 异常可能受到年龄阶段、认知能力、语言表型和分析参数设定的影响。

发育阶段可能是解释既往研究不一致的重要因素。儿童 EEG 的非周期谱特征本身具有年龄敏感性，早期发育研究也提示 aperiodic EEG 指标可被稳定测量，并可能与神经发育风险或语言发展相关。Karalunas 等研究表明，EEG aperiodic power spectral slope 具有可测量的内部一致性，并与早期 ADHD 风险相关。([PMC][4]) Wilkinson 等进一步报告，生命早期 aperiodic EEG 活动变化与后续 autism diagnosis 和语言发展相关。([PMC][5]) 因此，在 ASD 儿童样本中检验 aperiodic 指标的年龄依赖性，有助于理解不同年龄段研究结果之间的差异。

基于上述背景，本研究使用 specparam 对 ASD 与 TD 儿童静息态睁眼 EEG 功率谱进行参数化分析。研究目标包括：第一，比较 ASD 与 TD 儿童 global aperiodic exponent 和 offset 的差异；第二，探索这些差异在 ROI 和通道水平的空间分布；第三，比较传统周期峰参数是否存在组间差异；第四，检验 aperiodic 参数与临床症状及语言能力的关系；第五，通过敏感性分析、年龄交互模型和 split-half 信度分析评估主要结果的稳健性与发展意义。我们假设 ASD 儿童会表现出异常的 aperiodic EEG 参数，且这些差异可能比传统周期峰指标更敏感。

---

# 2. 方法

## 2.1 研究设计与被试

本研究为横断面观察性研究。共纳入 168 名具有静息态睁眼 EEG 数据和基本人口学信息的儿童，其中 ASD 80 名，TD 88 名。经 EEG 预处理、最少可用 epoch 标准和 specparam 拟合质量控制后，最终 138 名被试进入主分析，包括 ASD 61 名和 TD 77 名。被试年龄范围约为 40–131 月。≤72 月的学龄前年龄段被试为 23 名，占主分析样本的 16.7%。

ASD 组诊断依据为 [待补充：DSM-5/ICD-11/临床医生诊断/ADOS-2 等具体标准]。TD 组纳入标准为 [待补充：无神经发育障碍史、无精神神经系统疾病、筛查方式]。所有被试排除标准包括 [待补充：癫痫、严重脑损伤、遗传综合征、严重视觉/听觉障碍、药物使用、睡眠不足等]。研究已获得 [待补充：伦理委员会名称和批准号] 批准，所有儿童监护人均签署知情同意书，儿童本人根据年龄和理解能力提供口头或书面同意 [待补充]。

认知能力使用 [待补充：IQ 量表名称，如 WPPSI/WISC/其他] 评估，得到 IQ_total 及相关分量表。ASD 组临床症状使用 [待补充：ADOS/ADOS-2 模块、CARS、SRS 等量表及评估者资质] 评估。语言能力指标 `language_score` 来源于 [待补充：量表名称、计分方向、分数含义]。由于部分临床变量存在缺失，临床相关分析作为探索性分析。

本研究报告遵循观察性研究报告规范 STROBE 的原则。STROBE 声明为横断面、病例对照和队列等观察性研究提供报告清单。([EQUATOR Network][6])

## 2.2 EEG 采集

静息态 EEG 使用 EGI HydroCel-64 系统采集。原始数据以 `.mff` 格式保存，原始采样率为 500 Hz。采集时儿童处于睁眼静息状态，具体指令为 [待补充：注视点/空屏/动画/安静坐着/其他]。记录时长为 [待补充] 分钟。采集时参考为 VREF/Cz 参考，后续预处理中移除 VREF 通道，并保留 E1–E64 共 64 个 EEG 通道用于分析。电极阻抗控制标准为 [待补充：EGI 推荐阈值或实际标准]。

## 2.3 EEG 预处理

EEG 预处理在 Python 环境中使用 MNE-Python 完成。原始 `.mff` 文件经读取后，首先移除 VREF 参考通道及明显非 EEG 通道，保留 E1–E64 作为 EEG 分析通道。随后对连续数据进行 0.5–45 Hz 带通滤波和 50 Hz 陷波滤波，并降采样至 250 Hz。明显坏导经自动检测后插值。数据随后重参考至平均参考。

连续数据被切分为 2 s 非重叠 epoch。根据峰–峰振幅阈值剔除明显伪迹 epoch。初步测试显示 150 μV 阈值对儿童 EGI 睁眼数据过于严格，因此主分析使用 500 μV 阈值。主分析要求每名被试至少保留 60 个可用 epoch，即至少约 120 s 可用数据。对于 ICA，当前流程为 [待核实：n_components=0.99 或 30；是否自动剔除；是否读取人工 JSON 标注]。若存在人工标注的 ICA 排除文件，则按标注剔除相应成分；否则默认不剔除或按当前配置执行 [待核实]。由于未完成系统性的逐被试人工 ICA 复核，该点在局限性中讨论。

## 2.4 PSD 估计

对清洗后的 epoch 使用 Welch 方法估计每名被试、每个 EEG 通道的功率谱密度。主分析频率范围为 1–40 Hz。PSD 结果以 subject × channel × frequency 形式保存。被试水平 global PSD 和 global aperiodic 参数由有效 EEG 通道平均得到。所有 PSD 分析仅使用 EEG 通道，不包括 stim、misc、ECG 或 EOG 通道。

## 2.5 功率谱参数化

使用 specparam 对每个 subject × channel 的 PSD 进行参数化。主分析使用 fixed aperiodic mode，拟合范围为 1–40 Hz。参数设置包括 peak_width_limits = [1, 8]、max_n_peaks = 6、min_peak_height = 0.1、peak_threshold = 2.0。主要非周期指标为 aperiodic exponent 和 aperiodic offset。周期峰指标包括 theta、alpha、beta 和 low-gamma 频段内的中心频率、峰功率和带宽。若某一频段未检测到周期峰，则该频段峰参数记为缺失值，而非 0。

## 2.6 质量控制

质量控制包括 EEG 预处理质量和 specparam 拟合质量两部分。EEG 层面要求每名被试至少保留 60 个可用 2 s epoch。Specparam 通道级拟合质量标准包括：r² ≥ 0.90、exponent 位于 0–5 合理范围内，以及 fit_error 不处于全样本最高 5%。每名被试计算低质量通道比例；若 invalid_channel_ratio > 20%，则该被试被排除。

样本流失过程如下：初始具备 EEG 且完成预处理的被试为 168 名，其中 ASD 80 名，TD 88 名。145 名被试满足可用 epoch ≥60 标准，其中 ASD 65 名，TD 80 名。进一步有 7 名被试因 specparam 低质量通道比例过高被排除，最终主分析样本为 138 名，包括 ASD 61 名和 TD 77 名。

## 2.7 统计分析

所有统计分析在 Python 中完成，主要使用 pandas、scipy 和 statsmodels。组别变量以 ASD 为参照组，`C(group)[T.TD]` 表示 TD 相对 ASD 的增量。主模型为：

```text
global_exponent ~ group + age_months + sex + IQ_total + usable_epochs
```

次要模型以 global_offset 为结局，协变量相同。稳健性分析逐步纳入年龄、性别、IQ_total、可用 epoch、平均拟合 r²、坏导数量等协变量。ROI 分析使用五类 HydroCel-64 头皮 ROI，包括 frontal、central、temporal、parietal 和 occipital，并拟合 group × ROI 混合模型。通道水平分析对 64 个 EEG 通道分别拟合组间模型，并使用 FDR 校正多重比较。

周期峰分析比较 alpha_cf、alpha_pw、alpha_bw、theta_pw 和 beta_pw 等参数的组间差异。临床相关分析仅在 ASD 组内进行，包括 OLS 回归和 Spearman 相关。由于部分临床变量缺失较多，临床分析作为探索性分析。

## 2.8 敏感性、年龄调节和信度分析

敏感性分析包括不同 specparam 拟合频率范围（1–40 Hz、2–40 Hz、1–35 Hz、2–35 Hz）、fixed 与 knee aperiodic mode 比较，以及不同可用 epoch 标准。为检验年龄依赖性，拟合 group × age_months 交互模型：

```text
global_exponent ~ group * age_months + sex + IQ_total + usable_epochs
global_offset ~ group * age_months + sex + IQ_total + usable_epochs
```

同时将样本分为 ≤72 月和 >72 月年龄层进行分层分析。由于研究为横断面设计，年龄交互结果不能解释为个体内纵向发育轨迹。

为评估指标内部稳定性，将每名被试的 epoch 按奇偶分为两半，分别计算 PSD 和 specparam 参数，并计算 global_exponent、global_offset 和 alpha_pw 的 split-half Spearman 相关及 Spearman-Brown 校正信度。该分析反映同一次 EEG 记录内部稳定性，并不等同于跨天 test–retest 信度。

---

# 3. 结果

## 3.1 样本纳入与 EEG 质量控制

共 168 名被试完成静息态 EEG 预处理，其中 ASD 80 名，TD 88 名。根据最少可用数据标准，145 名被试保留至少 60 个 2 s epoch，其中 ASD 65 名，TD 80 名。23 名被试因可用 epoch 不足被排除。进一步根据 specparam 通道级拟合质量控制，7 名被试因低质量通道比例超过 20% 被排除。最终主分析样本为 138 名，包括 ASD 61 名和 TD 77 名。

两组年龄差异不显著 [待补充具体统计量]。TD 组 IQ_total 高于 ASD 组 [待补充具体统计量]，因此所有主模型均控制 IQ_total。组平均 PSD 显示两组均呈典型 1/f 下降形态，并在 alpha 频段附近可见峰值。PSD 图同时显示，ASD 与 TD 在高频端存在一定分离，这与后续 exponent 分析方向一致。

## 3.2 Global aperiodic exponent 和 offset 的组间差异

在控制年龄、性别、IQ_total 和可用 epoch 数后，TD 组 global aperiodic exponent 显著高于 ASD 组（β = 0.079，SE = 0.031，p = 0.012，95% CI [0.018, 0.140]，n = 138）。未校正描述统计显示，ASD 组 global exponent 均值为 1.69（SD = 0.14），TD 组为 1.79（SD = 0.14）。较高的 exponent 表示功率谱斜率更陡，即高频功率相对于低频功率下降更快。因此，该结果提示 ASD 组静息态 EEG 的非周期频谱相对更平坦。

Global aperiodic offset 的次要模型显示，TD 组 offset 高于 ASD 组的趋势未达到传统显著性阈值（β = 0.060，p = 0.095）。因此，本研究的主要组间差异集中在 aperiodic exponent，而非 offset。

## 3.3 稳健性与敏感性分析

稳健性模型显示，global exponent 的组效应方向在所有模型中保持一致。仅包含组别的模型显示 TD 组 exponent 高于 ASD 组（β = 0.096，p < 0.001）。加入年龄和性别后，组效应仍显著（β = 0.090，p < 0.001）。进一步控制 IQ_total 后，组效应仍存在（β = 0.080，p = 0.011）。主模型加入可用 epoch 后结果保持稳定（β = 0.079，p = 0.012）。额外控制平均拟合 r² 后，组效应减小但仍达到显著（β = 0.056，p = 0.030）；控制坏导数量后结果亦稳定（β = 0.081，p = 0.011）。这些结果提示主效应并非由单一协变量设定或数据质量指标偶然驱动。

频段敏感性分析显示，在 fixed aperiodic mode 下，将拟合范围设为 1–40 Hz、2–40 Hz、1–35 Hz 或 2–35 Hz 时，TD > ASD 的组效应方向均保持一致，且 p 值介于 0.016–0.031。Knee 模式下组效应方向多保持一致，但统计证据较弱（p 约 0.08–0.16）。因此，主分析以 fixed 模式结果为核心，knee 模式结果作为补充分析报告。

## 3.4 年龄依赖性组间效应

为检验组间差异是否随年龄变化，我们拟合了 group × age_months 交互模型。在控制性别、IQ_total 和可用 epoch 数后，global exponent 的 group × age 交互显著（β = 0.0033，p = 0.020）。Global offset 亦显示显著 group × age 交互（β = 0.0037，p = 0.021）。这些结果提示 ASD–TD 的非周期 EEG 差异可能具有年龄依赖性。

年龄分层分析进一步显示，在 ≤72 月年龄层中，exponent 组效应方向与主分析一致，但未达到显著性（β ≈ 0.055，p ≈ 0.47，n = 23）。在 >72 月儿童中，TD > ASD 的 exponent 差异达到显著（β ≈ 0.076，p ≈ 0.031）。由于本研究为横断面设计，上述结果不能解释为个体内纵向发育轨迹，但提示年龄阶段可能是影响 ASD aperiodic EEG 表现的重要因素。

## 3.5 空间分布：ROI 和通道水平探索

ROI 混合模型显示，组别主效应未达到显著，但 group × ROI 交互提示 ASD–TD exponent 差异在头皮区域上分布不均匀。部分 ROI 中 TD 相对 ASD 的 exponent 升高更明显，具体模型系数见补充表。

通道水平探索性分析显示，经 FDR 校正后，E33、E36、E37 和 E38 仍表现出显著组间差异，方向均为 TD > ASD。根据 HydroCel-64 电极布局，这些通道位于顶–枕部头皮区域，其中 E37 位于 Oz 附近。因此，本文将这些结果保守表述为顶–枕部 HydroCel-64 通道差异，而不进一步推断具体皮层来源。

## 3.6 周期峰参数

与 global aperiodic exponent 的组间差异不同，周期峰参数未显示显著组别主效应。在控制年龄、性别、IQ_total 和可用 epoch 数后，alpha peak frequency、alpha peak power、alpha bandwidth、theta peak power 和 beta peak power 的 group 项均未达到显著性（所有 p > 0.24）。该结果提示，本研究观察到的 ASD–TD 静息态 EEG 差异主要体现在非周期背景活动，而非传统周期峰参数。

## 3.7 ASD 组内临床关联

在 ASD 组内，global exponent 与 ADOS 总分及相关分量表的关联均未达到传统显著性阈值。ADOS 社交相关指标显示负向趋势，但 OLS 与 Spearman 结果均未达到 p < 0.05（OLS p ≈ 0.057；Spearman p ≈ 0.076）。颞部 ROI exponent 与语言分数亦未显示显著关联。由于临床变量存在缺失，且部分变量定义仍需核实，临床相关结果仅作为探索性分析报告，不能支持 aperiodic exponent 作为当前样本中临床症状严重程度的明确预测指标。

## 3.8 Split-half 信度

为评估 specparam 指标在单次静息 EEG 记录内部的稳定性，我们将每名被试的 epoch 按奇偶分半，并分别计算 PSD 和 specparam 参数。Global exponent、global offset 和 alpha peak power 均显示很高的 split-half 稳定性。Spearman 相关分别为 0.959、0.960 和 0.972；Spearman-Brown 校正信度分别为 0.979、0.980 和 0.986。该结果表明，本研究所使用的主要频谱参数在当前数据中具有较高的记录内稳定性。需要注意的是，该分析反映的是同一次记录内部的 split-half 信度，而非跨天 test–retest 信度。

---

# 4. 讨论

## 4.1 主要发现

本研究使用功率谱参数化方法分析 ASD 与 TD 儿童静息态 EEG，发现 ASD 儿童 global aperiodic exponent 显著低于 TD 儿童。该差异在控制年龄、性别、IQ、可用 EEG 数据量以及多种数据质量指标后仍保持稳定。相比之下，global offset 仅显示边缘趋势，周期峰参数未显示显著组间差异。进一步分析显示，aperiodic 指标的组间差异具有年龄依赖性，并且主要 specparam 指标在 split-half 分析中表现出很高的记录内稳定性。

## 4.2 ASD 中较低 aperiodic exponent 的解释

较低的 aperiodic exponent 表示功率谱斜率更平坦，即高频功率相对于低频功率的衰减较慢。本研究中 ASD 组 exponent 低于 TD，提示 ASD 儿童静息态 EEG 的非周期背景活动存在异常。该结果与部分既往研究方向一致，例如 Manyukhina 等报告 ASD 儿童，尤其是低于平均 IQ 的 ASD 儿童，表现出更平坦的 aperiodic slope。([PubMed][2])

需要强调的是，aperiodic exponent 的生理解释应保持谨慎。尽管它常被讨论为与神经兴奋–抑制状态、神经群体时间常数或背景活动有关，但 scalp EEG 的 aperiodic 指标受到多种因素影响，包括年龄、状态、参考方式、伪迹残留、频率范围和模型设定。因此，本研究结果更稳妥的解释是：ASD 儿童在静息态下表现出可测量的非周期谱形态改变，而非直接证明某一特定神经机制。

## 4.3 与学龄前 ASD EEG 研究的比较

本研究结果与近期学龄前 ASD 静息态 EEG 研究并不完全一致。Chen 等研究报告，2–6 岁 ASD 儿童相较神经典型儿童表现出更高的 aperiodic offset，但 aperiodic slope/exponent 未显示显著组间差异；该研究还发现 aperiodic/periodic 指标与语言能力存在关联。([PMC][3]) 与之相比，本研究发现 ASD 儿童 global exponent 降低，而 offset 仅为趋势。

本研究的 follow-up 分析提示，这种差异可能首先与年龄阶段有关。本研究年龄范围更宽，仅 23 名被试处于 2–6 岁学龄前范围，且 group × age 交互显著，提示 ASD–TD exponent 差异可能随年龄变化。低龄子样本中 exponent 组效应方向与主结果一致但不显著，而 >72 月儿童中组效应显著。由于低龄子样本较小，不能将其视为对学龄前研究的充分复现；但这些结果支持这样的解释：ASD 的 aperiodic EEG 异常可能具有发育阶段依赖性。

其次，offset 和 exponent 虽然相关，但并非等价。在本研究中，控制 offset 后 exponent 的组效应仍存在，而控制 exponent 后 offset 组效应不显著。这说明不同研究中 offset 与 exponent 可能对不同年龄阶段、认知水平和语言表型具有不同敏感性。综合来看，本研究并非简单否定既往学龄前研究，而是提示 ASD 相关非周期 EEG 异常可能具有异质性。

## 4.4 年龄依赖性与发育解释

年龄交互分析是本研究的重要扩展结果。Global exponent 和 global offset 均显示显著 group × age 交互，提示 ASD–TD 的非周期 EEG 差异可能随年龄变化。已有早期发育研究也提示 aperiodic EEG 活动与神经发育风险和语言发展有关。Wilkinson 等报告，生命早期 aperiodic EEG 活动变化与 autism diagnosis 和语言发展相关。([PMC][5])

然而，本研究为横断面设计，不能据此推断个体内发育轨迹。年龄交互结果仅说明不同年龄被试之间的组间差异模式不同。未来需要纵向追踪研究检验 ASD 儿童 aperiodic exponent 和 offset 是否随发育呈现不同轨迹，以及这些轨迹是否与语言、认知和症状变化相关。

## 4.5 周期峰阴性结果与功率谱参数化价值

本研究未发现 alpha、theta 或 beta 峰参数的显著组间差异。这一结果与 Chen 等学龄前研究中 ASD 与 NT 在 alpha peak frequency 和 alpha peak power 上无显著差异的发现部分一致。([PMC][3]) 周期峰阴性结果并不意味着静息 EEG 中不存在组间差异，而是提示差异主要体现在非周期背景活动上。

这一发现凸显了功率谱参数化的价值。如果只进行传统频段功率比较，非周期背景变化可能被误解释为某一频段振荡变化。Specparam 将周期峰和非周期背景分离，使本研究能够更清楚地定位 ASD–TD 差异的来源。

## 4.6 空间分布

通道水平分析显示，FDR 校正后显著差异主要集中在 E33、E36、E37 和 E38，即 HydroCel-64 顶–枕部头皮通道。ROI 分析亦提示组间差异具有非均匀空间分布。这一发现提示 ASD–TD 的 aperiodic exponent 差异可能并非全脑完全均匀，而是在后部头皮区域更突出。

但 EEG 头皮电位不能直接等同于皮层源活动。本研究未进行源定位或 MRI 约束建模，因此不将这些通道结果解释为特定皮层区域或 Brodmann 区的异常。未来研究可结合高密度 EEG、源定位和结构 MRI 进一步验证这些空间发现。

## 4.7 临床意义

ASD 组内临床相关分析未达到传统显著性阈值，ADOS 社交相关指标仅显示趋势。因此，本研究支持 aperiodic exponent 作为组水平神经生理差异指标，但尚不能证明其具有个体层面的临床预测价值。临床相关较弱可能与样本量、临床变量缺失、量表异质性、语言指标测量方式以及 ASD 表型多样性有关。

未来研究应使用更完整的临床和语言测量，并考虑 ASD 内部亚型分析。例如，根据语言能力、认知水平或症状严重程度分层，可能比简单线性相关更能揭示 aperiodic EEG 与临床表型之间的关系。

## 4.8 指标稳定性与方法学意义

Split-half 分析显示 global exponent、global offset 和 alpha peak power 均具有很高的记录内稳定性。这说明本研究的主要 specparam 指标不太可能由少数 epoch 或随机功率谱噪声驱动。Karalunas 等也报告 aperiodic EEG slope 可被可靠测量，并可用于早期发育风险研究。([PMC][4])

需要注意的是，本研究的 split-half 分析仅反映同一次 EEG 记录内部稳定性，并不等同于跨天、跨设备或跨实验室 test–retest reliability。未来研究需要进一步评估 aperiodic 指标在不同记录条件和不同样本中的复现性。

## 4.9 局限性

本研究有若干局限。第一，研究为横断面设计，年龄交互不能解释为纵向发育轨迹。第二，ASD 与 TD 在 IQ_total 上存在差异，虽然统计模型中控制了 IQ，且稳健性分析支持主结果，但组间认知水平不匹配仍是设计限制。第三，部分临床变量缺失较多，且个别变量定义仍需核实，因此临床相关分析只能作为探索性结果。第四，ICA 人工复核有限，残留眼动或肌电伪迹仍可能影响频谱估计。第五，knee 模式下组效应统计证据较弱，提示结果对 aperiodic 模型设定存在一定敏感性。第六，本研究未进行源定位，因此空间结果仅限于头皮电极水平。第七，split-half 信度并不等同于跨日重测信度。最后，本研究缺少独立外部验证样本，结果仍需在其他队列中复现。

## 4.10 结论

本研究表明，ASD 儿童静息态 EEG 表现出较低的 global aperiodic exponent，提示其非周期背景活动存在异常。该结果在控制年龄、性别、IQ、可用 EEG 数据量和多种质量指标后保持稳健，并显示年龄依赖性。相比之下，周期峰参数未显示显著组间差异。研究结果支持 specparam 分离出的非周期 EEG 指标作为理解 ASD 儿童静息态神经生理差异的有用工具。未来纵向和多中心研究需要进一步验证 aperiodic exponent 在 ASD 发育机制和临床表型中的意义。

---

# 参考文献草稿

Donoghue, T., Haller, M., Peterson, E. J., Varma, P., Sebastian, P., Gao, R., Noto, T., Lara, A. H., Wallis, J. D., Knight, R. T., Shestyuk, A., & Voytek, B. (2020). Parameterizing neural power spectra into periodic and aperiodic components. *Nature Neuroscience, 23*, 1655–1665. ([Nature][7])

Chen, Y., et al. (2026). Resting state aperiodic and periodic EEG activity in preschool-aged autistic children: Differences from neurotypical peers and links to language skills. *Molecular Autism*. ([PMC][3])

Manyukhina, V. O., et al. (2022). Globally elevated excitation–inhibition ratio in children with autism spectrum disorder and below-average intelligence. *Molecular Autism*. ([PubMed][2])

Karalunas, S. L., et al. (2022). Electroencephalogram aperiodic power spectral slope can be reliably measured and predicts ADHD risk in early development. *Developmental Psychobiology*. ([PMC][4])

Wilkinson, C. L., et al. (2025). Changes in early aperiodic EEG activity are linked to autism diagnosis and language development in infants with family history of autism. *Autism Research*. ([PMC][5])

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., Vandenbroucke, J. P., & STROBE Initiative. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology Statement: guidelines for reporting observational studies. *PLoS Medicine, 4*(10), e296. ([PMC][8])

---

# 图注草稿

**Figure 1. Sample inclusion and group-averaged PSD.**
A CONSORT-style flow diagram shows participant inclusion for the resting-state EEG aperiodic analysis. Of 168 participants with available and preprocessed resting-state EEG data, 145 met the usable epoch criterion of at least 60 two-second epochs. Seven additional participants were excluded because more than 20% of channels failed specparam quality control, resulting in a primary analysis cohort of 138 participants (61 ASD, 77 TD). Group-averaged PSD curves are shown for ASD and TD groups across 1–40 Hz.

**Figure 2. Group differences in global aperiodic parameters.**
TD children showed higher global aperiodic exponent than ASD children after adjusting for age, sex, IQ_total, and usable epochs. Global aperiodic offset showed a trend in the same direction but did not reach conventional significance.

**Figure 3. Age-dependent group effects.**
Group-by-age interaction models suggested that ASD–TD differences in global exponent and global offset varied as a function of age. These cross-sectional effects should not be interpreted as longitudinal developmental trajectories.

**Figure 4. Spatial distribution of channel-level group effects.**
Channel-wise regression coefficients for TD–ASD differences in aperiodic exponent are shown on the HydroCel-64 layout. FDR-significant channels are marked. Significant effects were observed over parieto-occipital HydroCel-64 channels, including E33, E36, E37, and E38.

**Supplementary Figure 1. Split-half reliability.**
Odd-even split-half analyses showed high within-session reliability for global exponent, global offset, and alpha peak power. Spearman-Brown corrected reliability estimates were all greater than 0.97.

---

# 你现在必须补充的信息

下面这些是投稿前必须人工补齐的，不建议让 AI 编：

```text
1. 伦理委员会名称和批准号
2. ASD 诊断标准：DSM-5/ADOS-2/临床医生诊断
3. TD 组筛查标准
4. IQ_total 使用的量表
5. ADOS 版本、模块、评分者资质
6. language_score 的量表名称、分数方向和含义
7. EEG 采集环境：睁眼时看什么、记录时长、阻抗标准
8. 药物、癫痫、神经系统疾病等排除标准
9. ICA 的真实参数和剔除策略
10. ROI 通道划分的最终依据
```

这版已经可以作为**正式论文中文 v3 草稿**。下一步建议不要继续加分析，而是做两件事：
**第一，补齐 Methods 的真实信息；第二，把这版翻译和改写成英文 manuscript。**

[1]: https://pubmed.ncbi.nlm.nih.gov/33230329/?utm_source=chatgpt.com "Parameterizing neural power spectra into periodic ... - PubMed"
[2]: https://pubmed.ncbi.nlm.nih.gov/35550191/?utm_source=chatgpt.com "Globally elevated excitation-inhibition ratio in children with ..."
[3]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12849409/?utm_source=chatgpt.com "Resting state aperiodic and periodic EEG activity in preschool ..."
[4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9707315/?utm_source=chatgpt.com "Electroencephalogram aperiodic power spectral slope can be ..."
[5]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11702732/?utm_source=chatgpt.com "Changes in early aperiodic EEG activity are linked to autism ..."
[6]: https://www.equator-network.org/reporting-guidelines/strobe/?utm_source=chatgpt.com "Statement: guidelines for reporting observational studies"
[7]: https://www.nature.com/articles/s41593-020-00744-x?utm_source=chatgpt.com "Parameterizing neural power spectra into periodic and ..."
[8]: https://pmc.ncbi.nlm.nih.gov/articles/PMC2034723/?utm_source=chatgpt.com "Strengthening the reporting of observational studies in ... - PMC"
