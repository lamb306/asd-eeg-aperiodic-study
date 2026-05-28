# Discussion 整合审计（v8 integrated）

**基线稿**：`manuscript_draft_zh_v6_submission_style.md`（v7 不存在）  
**扩展讨论来源**：`manuscript_draft_zh_v8_discussion_expanded.md`  
**输出稿**：`manuscript_draft_zh_v8_discussion_integrated.md` / `.docx`

---

## 1. 替换的小节（原 v6 → 新 v8）

| 小节 | 处理 |
|------|------|
| 4.1 主要发现 | 由单段扩展为两段；整合主效应、周期峰阴性、稳健性、年龄交互、空间探索、分半信度 |
| 4.2 | 原「ASD 较低 exponent 解释」→「非周期 exponent 作为组间敏感谱特征」 |
| 4.3 | 扩展 Chen et al. (2026) 对照；英文提示语改为中文 |
| 4.4 | 原「年龄依赖性与发育解释」→「年龄依赖性效应」；强调横断面界限 |
| 4.5 | 原 v6 的 4.6「空间分布」提前至此（与扩展稿结构一致） |
| 4.6 | 原 v6 的 4.5「周期峰阴性」→ 方法学意义专节 |
| 4.7 | 扩展临床相关性；禁止 biomarker 结论 |
| 4.8 | 扩展 split-half；强调非 test–retest |
| 4.9 | 编号清单改为段落；保留性别局限（修正后编码） |
| 4.10 | 正式结论段 |

**未改动部分**：摘要；§1–3；References；Supplementary Materials；图表明细；作者需补充清单。

---

## 2. 删除的英文提示语 / 标题英文

| 原文字 | 替换为 |
|--------|--------|
| `（Principal findings）` 等 10 处小节英文括号 | 已删除，仅保留中文标题 |
| `differ from / not fully consistent with` | 「与上述报告并不完全一致」 |
| `biomarker`（括号内） | 删除英文，保留「生物标志物」 |
| `发育时间 course` | 「发育时间进程」 |

---

## 3. 性别局限如何处理

| 项目 | 决定 |
|------|------|
| Table 1 性别检验 | ASD 5 女/56 男，TD 28 女/49 男，χ²，**p < .001**（修正后编码，见 `sex_encoding_rerun_audit.md`） |
| 讨论 4.9 | **保留**「性别分布不均衡」局限，数字为 **5 女/56 男、28 女/49 男** |
| 是否删除性别局限 | **否** — 组间性别构成仍显著不均衡，虽已协变量校正 |

---

## 4. 统计数字核对（与主稿 Results 一致）

| 指标 | 讨论中的表述 |
|------|----------------|
| 主效应 exponent | β = 0.079，SE = 0.031，p = .012，95% CI [0.018, 0.140] |
| offset 趋势 | β = 0.060，p = .095 |
| group × age exponent | β = .0033，p = .020 |
| group × age offset | β = .0037，p = .021 |
| split-half | ρ = 0.959–0.972，SB > 0.97 |
| 周期峰 | 所有 group p > .24 |
| 通道 FDR | E33、E36、E37、E38 |

---

## 5. 引用核对（讨论 vs References）

| 引用 | 在 References 中 |
|------|------------------|
| Chen et al. (2026) | 是 |
| Donoghue et al. (2020a, 2020b) | 是 |
| Gao et al. (2017) | 是 |
| Hill et al. (2022) | 是 |
| Karalunas et al. (2022) | 是 |
| Manyukhina et al. (2022) | 是 |
| Neo et al. (2023) | 是 |
| Wilkinson et al. (2024) | 是 |

**新增引用**：无  
**[citation needed]**：无（MNE 仅在方法节，不在讨论）

---

## 6. 仍需作者核实的信息

- [待补充] / [待核实]：伦理、诊断、IQ、ADOS、ICA、语言分数（与原 v6 一致）
- Chen et al. (2026)、Wilkinson et al. (2024)：References 已标注 metadata verification required
- 4.3 中 exponent–offset 联合模型：已明确为**补充分析**，非主结论

---

## 7. 讨论中最核心的三条论点

1. **主发现**：在协变量校正后，TD 儿童静息态 global aperiodic exponent 高于 ASD（更陡的 1/f 背景），效应在敏感性分析中方向一致；周期峰参数无显著组间差异，提示组间信号主要在**非周期 exponent** 而非传统振荡峰。

2. **发育与文献语境**：group × age 交互显著，为不同年龄段 ASD aperiodic 文献不一致提供线索；但必须在横断面设计下解读，**不能**等同于纵向发育轨迹。

3. **方法学与谨慎外推**：specparam 分离支持将非周期与周期变化区分；记录内分半信度高但**不是** test–retest；头皮 topomap 不能作源定位；exponent **不能**直接等同于 E/I 失衡或临床生物标志物。

---

*整合完成：2026-05-20*
