# 文献矩阵（ASD 静息态 EEG · specparam 论文）

**用途**：为 `manuscript_draft_zh_v2.md` 选题、引言、方法、讨论与补充材料引用提供对照表。  
**原则**：仅收录**已在项目文档中确认**或**经公开页面核实题名/DOI**的文献；**不编造**作者、卷期或未核对条目。  
**更新**：2026-05-20

---

## 使用说明

| 列名 | 含义 |
|------|------|
| **Citation** | 建议引用格式（定稿前请用 Endnote/Zotero 再核对） |
| **Topic** | 与本研究的关系主题 |
| **Sample / modality** | 样本与模态 |
| **Key finding** | 与本文相关的核心结论（简述） |
| **How it supports our paper** | 如何支撑本研究叙事 |
| **Where to cite** | 建议引用位置（稿本章节） |
| **Caution / limitation** | 引用时注意点 |

**图例**  
- **【项目已确认】**：`supplementary_results_compare_preschool.md` 等已用作对照分析。  
- **【DOI 已核实】**：通过网络检索核对题名与 DOI。  
- **【待作者补充】**：主题需要，但本仓库尚无完整书目信息。

---

## 主表

| # | Citation | Topic | Sample / modality | Key finding | How it supports our paper | Where to cite | Caution / limitation |
|---|----------|-------|-------------------|-------------|---------------------------|---------------|----------------------|
| 1 | **Neo, W. S., Foti, D., Keehn, B., et al. (2023).** Resting-state EEG power differences in autism spectrum disorder: a systematic review and meta-analysis. *Translational Psychiatry*, 13, 389. https://doi.org/10.1038/s41398-023-02681-2 **【DOI 已核实】** | ASD 静息态 EEG 频谱研究 | 41 项研究 Meta；1246 ASD / 1455 TD；静息态 EEG 频段功率 | 相对 alpha 降低（*g*≈−0.35），gamma 升高；delta/theta/beta 多不显著；异质性大；睁眼/闭眼与记录时长可调制效应 | 建立“ASD 静息态频谱文献以传统频段为主、结论混合”的背景；为本研究采用 specparam 提供**问题动机**（频段指标综述未分离非周期成分） | 引言 §1；讨论（与传统 alpha/gamma 文献对照，勿与 exponent 直接混谈） | **未使用 specparam**；效应为频段功率非 exponent/offset；与本研究年龄范围（约 40–131 月）不完全重叠 |
| 2 | **Liang, S., & Mody, M. (2022).** Abnormal brain oscillations in developmental disorders: application of resting state EEG and MEG in autism spectrum disorder and fragile X syndrome. *Frontiers in Neuroimaging*, 1, 903191. https://doi.org/10.3389/fnimg.2022.903191 **【DOI 已核实】** | ASD 静息态 EEG 频谱研究（综述） | 综述；ASD、FXS；静息态 EEG/MEG | 总结发育障碍中振荡异常及方法学考量；强调静息态范式在发育样本中的价值与局限 | 引言中补充“发育障碍静息态 EEG 综述”脉络；支持静息态作为可行模态 | 引言 §1 | 叙述性综述，**无本研究同类 specparam 指标**；不宜用于定量对比 |
| 3 | **Donoghue, T., Dominguez, J., & Voytek, B. (2020).** Electrophysiological frequency band ratio measures conflate periodic and aperiodic neural activity. *eNeuro*, 7(6), ENEURO.0192-20.2020. https://doi.org/10.1523/ENEURO.0192-20.2020 **【DOI 已核实】** | 传统 band power / 频带比值的局限 | 模拟 + 人 EEG；频带比（含 θ/β） | 频带比常反映**非周期活动**而非单纯振荡功率；建议显式参数化功率谱 | 论证主分析采用 specparam 而非单纯 trapz 频段功率或频带比的**方法学必要性**；与项目 script 13 传统频段对照分析呼应 | 引言 §1–2；方法（为何报告周期峰与非周期分离） | 该文重点为**频带比**而非所有 band power；引用时勿过度概括为“所有频段功率均无效” |
| 4 | **Donoghue, T., Haller, M., Peterson, E. J., et al. (2020).** Parameterizing neural power spectra into periodic and aperiodic components. *Nature Neuroscience*, 23(12), 1655–1665. https://doi.org/10.1038/s41593-020-00744-x **【DOI 已核实】** | FOOOF / specparam 方法 | 多模态（EEG/MEG/LFP）；方法学 + 应用示例 | 提出将功率谱分解为周期峰 + 非周期（offset、exponent）；开源实现（现 specparam 包） | 方法学**核心引用**：说明 global exponent/offset、alpha_pw 等指标来源与 fixed/knee 模式含义 | 方法 §specparam；图 1 说明；补充材料（拟合 QC） | 算法假设（峰检测、频段范围）影响结果；本研究用 **fixed** 为主、knee 为敏感性 |
| 5 | **Gao, R., Peterson, E. J., & Voytek, B. (2017).** Inferring synaptic excitation/inhibition balance from field potentials. *NeuroImage*, 158, 70–78. https://doi.org/10.1016/j.neuroimage.2017.06.065 **【DOI 已核实】** | aperiodic exponent / offset 的生理解释 | 动物模型 + 场电位；理论/模型 | 提出 1/f exponent 与 E/I 平衡关系的计算模型框架 | 讨论中**谨慎**引用：exponent 与 E/I **可能相关**的生物学依据之一；须与 v2 降调措辞一致（“可能”而非“反映”） | 讨论 §机制；局限（间接推断、无 invivo E/I 测量） | **非 ASD 样本**；从场电位到 E/I 仍为模型推断，不能作为本研究因果证据 |
| 6 | **Hill, A. T., Clark, G. M., Bigelow, F. J., Lum, J. A. G., & Enticott, P. G. (2022).** Periodic and aperiodic neural activity displays age-dependent changes across early-to-middle childhood. *Developmental Cognitive Neuroscience*, 54, 101076. https://doi.org/10.1016/j.dcn.2022.101076 **【DOI 已核实】** | ASD/儿童 aperiodic slope；发育 | 3–18 岁典型发育儿童；EEG；specparam/FOOOF 类分解 | 儿童期周期与非周期成分随年龄系统性变化 | 支撑**年龄协变量/年龄交互**的讨论背景：exponent 在发育期非常态；解释横断面 group×age 的文献语境 | 引言；讨论 §年龄交互；局限（本研究非纵向） | **非 ASD**；年龄范围与本文 40–131 月部分重叠但设计不同 |
| 7 | **Wilkinson, C. L., Yankowitz, L. D., Chao, J. Y., et al. (2024).** Developmental trajectories of EEG aperiodic and periodic components in children 2–44 months of age. *Nature Communications*, 15, 5788. https://doi.org/10.1038/s41467-024-50204-4 **【DOI 已核实】** | aperiodic EEG 与发育；周期/非周期发育轨迹 | 纵向 EEG；592 名 2–44 月龄典型婴儿 | 婴儿期 aperiodic/periodic 呈非线性发育轨迹；讨论 E/I 解释需谨慎 | 讨论**发育轨迹**与学龄前年龄窗；说明婴儿期与较大儿童谱形态差异；勿将本文横断面交互等同于该文纵向轨迹 | 讨论 §年龄；引言（发育敏感性） | **婴幼儿典型发育**；与 ASD 组间差异无直接对比 |
| 8 | **Chen, Y., Tsou, M., Nelson, C. A., et al. (2026).** Resting state aperiodic and periodic EEG activity in preschool-aged autistic children: differences from neurotypical peers and links to language skills. *Molecular Autism*, 17, 7. https://doi.org/10.1186/s13229-025-00700-1 **【项目已确认】【DOI 已核实】** | 学龄前 ASD resting EEG aperiodic/periodic | 64 ASD vs 64 TD；2–6 岁；静息态 EEG；SpecParam | 组水平：**offset 更高**，**slope/exponent 组间不显著**；周期峰组间多不显著；ASD 内 offset/alpha 峰与语言相关 | **核心外部对照**：本文 TD>ASD **exponent** 与 Chen **offset** 重点不同；仅 16.7% 被试落在 24–72 月，不宜称“重复检验” | 引言；讨论 §与学龄前研究差异；补充材料 S-C（项目已写 `supplementary_results_compare_preschool.md`） | 横断面；样本 SES 较高；与本文年龄结构差异大；措辞用 **“不完全一致”** 而非“矛盾” |
| 9 | **Chen, Y., Tsou, M., Nelson, C. A., et al. (2026).** *同上* | aperiodic EEG 与发育/语言 | 同上；语言样本 + 标准语言评估 | ASD 内：较低 offset、较高 alpha 峰幅与更好语言/非语言发育相关 | 支撑探索性临床分析（exponent vs ADOS_SA 趋势）的**背景**：非周期/周期均可能与语言相关，但本研究临床关联未显著 | 讨论 §临床；结果 §探索性临床 | 本文 **language_score 为 ToMI 映射** [待核实变量定义]；与 Chen 语言指标**非同源**，不可直接类比 |
| 10 | **Karalunas, S. L., et al. (2022).** Electroencephalogram aperiodic power spectral slope can be reliably measured and predicts ADHD risk in early development. *Developmental Psychobiology*, 64(3), e22228. https://doi.org/10.1002/dev.22228 **【DOI 已核实】** | EEG aperiodic 指标信度；儿童/青少年 | 婴儿 1 月龄 *n*=69；青少年 *n*=262；静息态 EEG；FOOOF/specparam 类 | aperiodic slope/exponent 在婴儿与青少年均具**良好内部一致性**；与 ADHD 风险相关（方向随年龄变化） | 讨论 **split-half** 时引用外部先例：aperiodic 指标可具有较高内部一致性；强调本文 split-half 为 **epoch 分半** 而非该文跨年龄设计 | 方法 §分半信度；讨论 §信度；局限（非 test–retest） | **ADHD 非 ASD**；指标为 slope/exponent 与本文一致但临床构念不同；勿将 ADHD 机制外推至 ASD |
| 11 | **Robertson, M. M., Furlong, S., Voytek, B., Donoghue, T., Boettiger, C. A., & Sheridan, M. A. (2019).** EEG power spectral slope differs by ADHD status and stimulant medication exposure in early childhood. *Journal of Neurophysiology*, 122(5), 2427–2437. https://doi.org/10.1152/jn.00388.2019 **【DOI 已核实】** | 儿童 aperiodic slope；神经发育障碍邻域 | 学龄前儿童 ADHD vs TD；EEG；spectral slope | 早期儿童 ADHD 与 slope 差异相关；与药物状态有关 | 补充“儿童期非周期斜率文献”邻域证据；讨论中说明 ASD 文献仍少，可对比神经发育队列方法学 | 讨论（可选） | **非 ASD**；与本文表型/诊断不同，仅作方法学与发育敏感性旁证 |
| 12 | **von Elm, E., Altman, D. G., Egger, M., et al. (2007).** The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *PLOS Medicine*, 4(10), e296. https://doi.org/10.1371/journal.pmed.0040296 **【DOI 已核实】** | 横断面研究报告规范 STROBE | 观察性研究报告指南；非原始数据 | 22 项清单，改进队列/病例对照/**横断面**研究报告透明度 | 方法/补充材料声明遵循 STROBE 横断面报告（样本流、协变量、缺失）；与 CONSORT 流程图（补充图 S1）互补 | 方法 §设计；补充材料（STROBE checklist 待填） | STROBE 不替代预注册；**不能**弥补因果推断局限 |
| 13 | **【待作者补充】** 其他 ASD 静息态 **specparam/FOOOF** 研究（非学龄前、非 Chen 2026） | ASD/儿童 aperiodic slope 研究 | — | — | 若存在学龄或混合年龄 ASD 样本的 exponent 报告，用于扩展讨论“ASD 非周期指标是否一致” | 讨论 | 勿编造；检索关键词建议：`autism` + `FOOOF` / `specparam` + `aperiodic` + `resting` |
| 14 | **【待作者补充】** 本研究数据采集单位既有 ASD 静息态 EEG 传统频段论文（若有） | 传统 band power 的局限（本地背景） | 若课题组曾发表频段功率 ASD 研究 | — | 衔接“从频段功率到 specparam”的同一队列叙事 | 引言/讨论 | 仅在有真实出版物时纳入 |
| 15 | **本项目分析结果（非外部文献）** Split-half：ρ=0.959–0.972，SB>0.97（*n*=138） | EEG aperiodic 指标信度（本研究） | 本队列；奇偶 epoch 分半；specparam fixed | 高内部一致性 | 结果 §分半信度；讨论中说明**不等于** test–retest | 结果；补充图 S4 | **不可作为文献引用**；正文引用 Karalunas 等 + 报告自身估计 |

---

## 按稿本章节的推荐引用组合（最小集）

| 章节 | 建议优先引用（#） |
|------|-------------------|
| **摘要/引言** | 4, 3, 1, 8 |
| **方法** | 4, 12；软件可另引 MNE/specparam 文档 [待作者补充版本] |
| **结果** | 一般不引方法学文献，除 CONSORT/STROBE 图注 |
| **讨论 – 主发现** | 8, 1, 6, 7 |
| **讨论 – 年龄交互** | 6, 7, 8；强调横断面措辞 |
| **讨论 – 机制** | 5（降调）；避免过度引用 E/I |
| **讨论 – 临床** | 8, 9；[待核实变量定义] |
| **讨论 – 信度** | 10, 15（自身结果） |
| **局限** | 3, 4, 12, 8 |

---

## 主题覆盖自检

| 要求主题 | 矩阵行 # | 状态 |
|----------|----------|------|
| ASD 静息态 EEG 频谱研究 | 1, 2 | 已覆盖 |
| 传统 band power 的局限 | 3 | 已覆盖 |
| FOOOF/specparam 方法 | 4 | 已覆盖 |
| exponent/offset 生理解释 | 5 | 已覆盖（降调） |
| ASD/儿童 aperiodic slope | 6, 8, 11, 13 | 8 已确认；13 待补 |
| 学龄前 ASD aperiodic/periodic | 8, 9 | **项目已确认** |
| aperiodic EEG 与发育/语言 | 7, 8, 9 | 已覆盖 |
| EEG aperiodic 指标信度 | 10, 15 | 已覆盖 |
| STROBE 横断面 | 12 | 已覆盖 |

---

## 作者待办（书目与检索）

1. **必做**：将 #8 Chen et al. (2026) 导入参考文献库，核对作者列表、卷期、页码与 PMC ID。  
2. **必做**：用同一检索式在 PubMed/Google Scholar 补 #13（ASD + specparam + resting），只添加能核对 PDF/DOI 的条目。  
3. **建议**：核对 #10 完整作者列表（Karalunas et al. 是否含 Waschke 为第一作者，依期刊显示为准）。  
4. **建议**：若投 *Molecular Autism*，核对期刊对 STROBE、CONSORT 扩展说明与数据可用性的要求。  
5. **禁止**：在未读全文前，根据摘要编造“ASD exponent 升高/降低”的统一方向。

---

## 附：与本项目分析的直接对照（非文献，供讨论写作）

| 对比维度 | Chen et al. (2026) 学龄前 | 本研究主分析 (*N*=138) |
|----------|---------------------------|------------------------|
| 年龄窗 | 24–72 月（2–6 岁） | 约 40–131 月；仅 23 人 ≤72 月 |
| 主效应参数 | offset ↑ in ASD | exponent：TD > ASD（*p*=.012） |
| exponent 组效应 | 不显著 | 显著 |
| 周期峰组间 | 多不显著 | 所有 group *p*>0.24 |
| 设计 | 横断面 | 横断面 + group×age 显著 |

*详见 `outputs/reports/supplementary_results_compare_preschool.md`。*

---

*本矩阵为写作辅助，不构成引用清单终稿。定稿前请由通讯作者逐条核对原文与 DOI。*
