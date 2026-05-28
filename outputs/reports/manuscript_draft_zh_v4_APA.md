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

两组年龄差异不显著 [待补充具体统计量]。TD 组 IQ_total 高于 ASD [待补充具体统计量]；主模型均校正 IQ。组平均 PSD 呈典型 1/f 形态，alpha 频段可见周期峰。

### 3.2 Global aperiodic exponent 与 offset

协变量校正后，TD 组 global exponent 高于 ASD（β = 0.079，SE = 0.031，*p* = 0.012，95% CI [0.018, 0.140]，*n* = 138）。未校正：ASD *M* = 1.69（*SD* = 0.14），TD *M* = 1.79（*SD* = 0.14）。较高 exponent 表示斜率更陡；ASD 相对更平坦。

Global offset：TD > ASD 趋势（β = 0.060，*p* = 0.095）。主组间差异集中在 exponent。

### 3.3 稳健性与敏感性

嵌套模型中组效应方向均为 TD > ASD：仅组别 β = 0.096，*p* < 0.001；主模型 β = 0.079，*p* = 0.012；+ 平均 *R*² 后 β = 0.056，*p* = 0.030；+ 坏导 β = 0.081，*p* = 0.011。

fixed 模式 1–40、2–40、1–35、2–35 Hz 组效应 *p* = 0.016–0.031；knee 模式方向一致，*p* ≈ 0.08–0.16。

### 3.4 年龄依赖性

group × age_months：global exponent（β = 0.0033，*p* = 0.020）；global offset（β = 0.0037，*p* = 0.021）。

≤72 月层 exponent 组效应 β ≈ 0.055，*p* ≈ 0.47（*n* = 23）；>72 月层 β ≈ 0.076，*p* ≈ 0.031。

### 3.5 空间分布（探索性）

ROI 混合模型：组别主效应不显著；部分 ROI 的 group×ROI 交互达到显著，具体系数见补充表。

通道 FDR：E33、E36、E37、E38 显著（TD > ASD），位于顶–枕部 HydroCel-64 电极位置。**Topomap 仅反映头皮电极水平效应，不作皮层源定位推断。**

### 3.6 周期峰参数

alpha 峰功率、中心频率、带宽及 theta、beta 峰功率的 group 项均不显著（所有 *p* > 0.24）。

### 3.7 ASD 组内临床关联（探索性）

*n* = 61。ADOS 总分等 OLS/Spearman 未显著。`ADOS_SA` [待核实变量定义]：OLS *p* ≈ 0.057；Spearman ρ = −0.229，*p* ≈ 0.076。颞叶 ROI exponent 与 `language_score` [待核实变量定义]（*n* = 55）：OLS *p* ≈ 0.319。未校正多重比较。

### 3.8 Split-half 信度

*n* = 138。Spearman ρ：global exponent 0.959，SB = 0.979；global offset 0.960，SB = 0.980；alpha_pw 0.972，SB = 0.986。**为记录内 epoch 分半一致性，非 test–retest。**

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

## 附录：图表清单

| 编号 | 内容 |
|------|------|
| 图 1 | 样本纳入流程 + 组平均 PSD / specparam 示意 |
| 图 2 | Global exponent/offset + 稳健性森林图 |
| 图 3 | 年龄×组别交互（正文重点） |
| 图 4 | ROI 边际效应 + 通道 topomap |
| 图 5 | 周期峰 + ASD 内临床探索 |
| 图 S1 | CONSORT 流程图 |
| 图 S4 | Split-half 信度 |

---

## 附录：待补充信息清单

伦理批号；ASD/TD 诊断与排除标准；IQ 与 ADOS 量表详情；EEG 采集现场；ICA [待核实]；`ADOS_communication`、`ADOS_RRB`、`language_score` [待核实变量定义]；Table 1 具体检验统计量。

---

## 附录：引用待核查清单

| 项目 | 说明 |
|------|------|
| MNE-Python | 正文标注 [citation needed: MNE-Python reference] |
| Manyukhina et al. (2022) | 已纳入参考文献（DOI 已核实）；**不在原 literature_matrix**；为 MEG 非静息态 EEG |
| Wilkinson et al. (2025) *Autism Research* | v3 曾引用；**未纳入**（不在 literature_matrix；正式卷期页码待作者核对） |
| Robertson et al. (2019) | 文献矩阵 #11；正文未引用，参考文献表已删除 |

---

## 生成统计（v4）

| 指标 | 数值 |
|------|------|
| 参考文献条数 | 12 |
| 正文 in-text 引用约计（含叙述式与括号式） | 约 37 |
| [citation needed] 处数 | 1（MNE-Python） |
| metadata incomplete（见 `reference_audit_APA.md`） | 4（Karalunas、Chen 作者终核、Wilkinson et al.、Manyukhina 模态说明） |

*定稿前请用 Zotero 核对 Karalunas 与 Wilkinson (2024) 完整作者列表。*
