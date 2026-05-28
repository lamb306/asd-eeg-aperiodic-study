# Submission readiness audit (v6)

## 已解决的问题

- **性别编码修正**（2026-05-20）：`Resting_info` 中 **0=男、1=女**；已修正 `sync_participants_from_resting_info.py` 中误写为 0=女的映射，并重新同步 `participants.csv` 与 Table 1。修正后主分析队列：ASD **5 女 / 56 男**，TD **28 女 / 49 男**（此前表内 F/M 对调）。

- 清理 Markdown 星号、分隔线、反引号与代码块式公式
- 统一 p 值、β、SE、CI 与三位小数格式
- Donoghue (2020) 拆分为 2020a（eNeuro）与 2020b（Nature Neuroscience），正文与 References 同步
- Table 1 仅保留人口学与 EEG QC；临床变量移至 Supplementary Table S1（探索性标注）
- Table 2 精简为协变量模型摘要
- 补充表去除 nan/True/False 与导出体例；大表仅保留摘要行
- Results 3.7 与 Discussion 4.7 弱化未核实临床变量，不突出 ADOS 趋势
- Word：12 pt、1.5 倍行距、图居中、References 悬挂缩进、三线表（无竖线）

## 仍需作者补充的信息

见稿末「作者需补充清单」：伦理批号、诊断/排除标准、IQ/ADOS 量表、EEG 采集细节、ICA 策略、MNE 引用。

## 仍需核查的引用

- Chen et al. (2026) — metadata verification required
- Wilkinson et al. (2024) — metadata verification required（完整作者列表）
- MNE-Python — [citation needed]
- Karalunas et al. (2022) — 建议用 Zotero 终核卷期页码

## 含 sex 分析重跑状态（2026-05-20 已完成）

性别编码已修正（0=男，1=女），并重跑 `08`–`12`、`14`、`16`–`19`（`--overwrite`）。**主效应与年龄交互数字不变**（β=0.079、p=.012；group×age p=.020）。详见 `outputs/reports/sex_encoding_rerun_audit.md`。

## 仍建议补做的分析

1. **女性仅样本**主模型（female-only primary model），报告 β 与 n
2. **性别平衡或性别敏感性**：sex-balanced subsample 或强化 sex-adjusted 报告（主模型已含 sex，建议补充女性子样本与男性比例说明）
3. **周期峰分析**：若时间允许，按主分析 N = 138（非 N = 145）重跑 periodic peak OLS，更新 Supplementary Table S4
4. **临床关联**：language_score 未核实前，仅保留于补充材料；勿写入正文主结论

## 投稿前必须人工检查的图表

| 项目 | 检查内容 |
|------|----------|
| Figure 1A | CONSORT 数字与正文 168→145→138 一致 |
| Figure 1B | PSD 轴标签与 specparam 拟合范围 1–40 Hz |
| Figure 2 | 箱线图 TD>ASD 与 β = 0.079, p = .012 一致 |
| Figure 3 | 横断面交互勿写成纵向轨迹（图注已提醒） |
| Figure 4 | Topomap 为头皮水平，非源定位 |
| Figure S1 | 标注 split-half，非 test–retest |
| Table 1 | 性别分布不均衡已在讨论说明 |
| Table 2 | 主模型行与摘要结果一致 |
| 所有图 | Word 中确为嵌入图而非占位文字 |

## 输出文件

- `manuscript_draft_zh_v6_submission_style.md`
- `manuscript_draft_zh_v6_submission_style.docx`
- `reference_audit_v6.md`
- `figure_table_audit_v6.md`
