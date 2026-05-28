# APA 引用审计报告（manuscript_draft_zh_v4_APA）

**对照稿本**：`manuscript_draft_zh_v4_APA.md`  
**文献来源**：`literature_matrix_for_manuscript.md` + 任务指定 Manyukhina (2022)（DOI 已外部核实，**不在原矩阵**）  
**日期**：2026-05-20

---

## 1. 主审计表

| Citation key | Used in manuscript? | Sections used | Metadata complete? | DOI present? | Notes |
|--------------|---------------------|---------------|----------------------|--------------|-------|
| Chen et al. (2026) | Yes | 引言；讨论 §4.3, 4.5, 4.7 | Partial | Yes | 矩阵 #8–9；作者列表建议按原文补全 Wilkinson 等共同作者（若适用） |
| Donoghue et al. (2020) eNeuro | Yes | 摘要；引言 | Yes | Yes | 矩阵 #3 |
| Donoghue et al. (2020) Nat Neurosci | Yes | 摘要；引言；方法；讨论 §4.5 | Yes | Yes | 矩阵 #4 |
| Gao et al. (2017) | Yes | 引言；讨论 §4.2 | Yes | Yes | 矩阵 #5；仅“可能相关”措辞 |
| Hill et al. (2022) | Yes | 引言；讨论 §4.4 | Yes | Yes | 矩阵 #6 |
| Karalunas et al. (2022) | Yes | 引言；方法；讨论 §4.8 | Partial | Yes | 矩阵 #10；参考文献作者列表需 PubMed 终核 |
| Liang & Mody (2022) | Yes | 引言 | Yes | Yes | 矩阵 #2 |
| Manyukhina et al. (2022) | Yes | 引言；讨论 §4.2 | Yes | Yes | **不在原矩阵**；DOI 10.1186/s13229-022-00498-2；**MEG 非静息 EEG** |
| Neo et al. (2023) | Yes | 摘要；引言 | Yes | Yes | 矩阵 #1 |
| Robertson et al. (2019) | No | — | Yes | Yes | 矩阵 #11；**未写入 v4 正文/References** |
| von Elm et al. (2007) | Yes | 方法 §2.1 | Yes | Yes | 矩阵 #12 |
| Wilkinson et al. (2024) | Yes | 引言；讨论 §4.4 | Partial | Yes | 矩阵 #7；参考文献用 et al.；与 v3 中 Wilkinson (2025) *Autism Research* **非同篇** |
| MNE-Python | No (citation needed) | 方法 §2.3 | — | — | 矩阵未列；正文 [citation needed: MNE-Python reference] |
| Split-half（本项目） | Yes（无文献键） | 结果 §3.8；讨论 | N/A | N/A | 非外部文献；勿列入 References |

---

## 2. 文献矩阵中有但未在 v4 使用的文献

| 矩阵 # | Citation | 原因 |
|--------|----------|------|
| 11 | Robertson et al. (2019) | 可选邻域文献；v4 未引用 |
| 13 | 【待作者补充】其他 ASD specparam 研究 | 无完整书目 |
| 14 | 【待作者补充】本单位既往频段研究 | 无完整书目 |
| 15 | 本项目 split-half 结果 | 应报告于 Results，**不**作为参考文献条目 |

---

## 3. 正文出现但参考文献表应包含的引用（核对结果）

| 引用 | 在 References 中？ |
|------|-------------------|
| Chen et al. (2026) | Yes |
| Donoghue et al. (2020) ×2 | Yes（两条） |
| Gao et al. (2017) | Yes |
| Hill et al. (2022) | Yes |
| Karalunas et al. (2022) | Yes |
| Liang & Mody (2022) | Yes |
| Manyukhina et al. (2022) | Yes |
| Neo et al. (2023) | Yes |
| von Elm et al. (2007) | Yes |
| Wilkinson et al. (2024) | Yes |
| MNE-Python | No — 见 [citation needed] |

**正文未引用、References 已删除**：Robertson et al. (2019)

---

## 4. 参考文献表中有但正文未引用的文献

当前 **无**（Robertson 已删除）。

---

## 5. 所有 [citation needed] 位置

| 位置 | 标记 |
|------|------|
| 方法 §2.3 EEG 预处理 | `[citation needed: MNE-Python reference]` |

---

## 6. metadata incomplete 文献

| 文献 | 缺失/待核内容 |
|------|----------------|
| Karalunas et al. (2022) | 完整作者列表、卷期页码建议按 *Developmental Psychobiology* 最终出版信息核对 |
| Chen et al. (2026) | 页码/文章号已写 Article 7；共同作者是否含 Wilkinson 需按期刊页面核对 |
| Wilkinson et al. (2024) | 参考文献使用 et al.；完整作者列表待补 |
| Manyukhina et al. (2022) | 书目完整；**模态为 MEG**，与本文 EEG 需在讨论中区分 |

---

## 7. v3 → v4 关键文献决策记录

| v3 引用 | v4 处理 | 理由 |
|---------|---------|------|
| Wilkinson et al. (2025) *Autism Research* | **未纳入** | 不在 `literature_matrix`；正式卷期未在矩阵核实；仅 medRxiv 10.1101/2024.12.15.24319061 可查 |
| Manyukhina et al. (2022) | **纳入** | 任务明确要求；DOI 已核实 |
| 脚注链接 [PubMed][1] 等 | **已移除** | 改为 APA 作者-年份 |
| STROBE | von Elm et al. (2007) | 矩阵 #12 |

---

## 8. 汇总统计（与 v4 文末一致）

| 指标 | 数值 |
|------|------|
| References 条目数 | **12** |
| 来自 literature_matrix 的条目 | **11**（#1–#12 除 #11 Robertson 未用、#13–15 非文献） |
| 矩阵外新增（Manyukhina） | **1** |
| 正文 in-text 引用约计 | **约 37**（脚本按作者+年份统计，含重复引用） |
| [citation needed] | **1** |
| metadata incomplete | **4** 条（见 §6） |

---

## 9. 定稿前建议

1. 用 Endnote/Zotero 导入 12 条 DOI，刷新作者与页码。  
2. 补引 **MNE-Python**（Gramfort et al., 2013/2014）或删除软件名。  
3. 决定是否引用 Robertson (2019) 或矩阵 #13 新检 ASD+specparam 文献。  
4. 若需婴儿期 ASD 诊断+语言 aperiodic 文献，单独核实 Wilkinson 2025 *Autism Research* 正式出版信息后再加入——**勿与 Wilkinson 2024 Nat Commun 混淆**。  
5. 全文检索 “contradict”“反映 E/I”“test–retest”“皮层源” 确保 v4 措辞合规。

---

*审计完成。统计引用次数可用：`rg -o '\([A-Z][a-z]+.*?\d{4}\)' manuscript_draft_zh_v4_APA.md`（近似）。*
