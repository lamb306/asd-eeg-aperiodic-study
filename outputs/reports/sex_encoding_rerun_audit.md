# 性别编码修正与含 sex 分析重跑审计

**日期**：2026-05-20  
**编码规则（已确认）**：`Resting_info` 中 **0 = 男（M），1 = 女（F）**  
**修正文件**：`scripts/sync_participants_from_resting_info.py`（`_sex_code`）

---

## 1. 结论（给写稿用）

| 问题 | 结论 |
|------|------|
| 此前稿件中的 **主效应数字** 是否仍有效？ | **是。** `global exponent` 的 TD−ASD 效应 **β = 0.079，p = .012** 在修正性别后 **数值不变**（与旧误编码结果一致至机器精度）。 |
| 年龄交互是否不变？ | **是。** `C(group)[T.TD]:age_months` 对 exponent：**β = 0.003314，p = .020**（不变）。 |
| 稳健性 Table 2 主模型是否不变？ | **是。** `model_4` **β = 0.079，p = .012**（不变）。 |
| 什么量变了？ | **`C(sex)[T.M]` 系数符号翻转**（因标签对调）；Table 1 性别计数（此前表 1 已在同步后修正）。 |
| 含 sex 的分析是否已全部重跑？ | **是**（见下表）；`participants.csv` 与 `derivatives/participants_analysis.csv` 已于 2026-05-20 18:50/19:01 更新。 |

**解释**：旧编码将 0/1 对调，相当于在模型中把“男/女”标签互换。在含 **group + sex + 其他协变量** 的线性模型中，**group 系数可因对称性保持不变**，而 **sex 系数反号**。主结论（TD > ASD 的 exponent）不依赖 sex 标签方向，故稿件核心统计可保留；讨论中关于“性别协变量”的解释应基于 **修正后** 的 `C(sex)[T.M]`。

---

## 2. 数据层验证

| 文件 | ASD | TD |
|------|-----|-----|
| `data/participants/participants.csv` | M=71, F=9（全样本 168） | M=58, F=30 |
| 主分析队列 `main_cohort_subject_list.csv` | **M=56, F=5** | **M=49, F=28** |

Excel 抽查（TD 表头 `Sex`）：`0 → M`，`1 → F`。**通过。**

---

## 3. 重跑脚本清单

| 脚本 | 输出 | 重跑时间 | 含 sex |
|------|------|----------|--------|
| `sync_participants_from_resting_info.py` | `participants.csv` | 2026-05-20 18:50 | 源数据 |
| `01_prepare_participants.py` | `derivatives/participants_analysis.csv` | 2026-05-20 19:01 | 传递 |
| `07b_table1_main_cohort.py` | Table 1 CSV | 2026-05-20 18:50+ | 描述性 |
| `08_main_group_analysis.py` | `main_group_analysis.csv` | **2026-05-20 19:01** | 是 |
| `09_roi_mixed_model.py` | `roi_mixed_model.csv` | 19:01 | 是 |
| `10_channel_level_analysis.py` | 通道/FDR | 19:01 | 是 |
| `11_clinical_correlation.py` | 临床相关 | 19:01 | 是（ASD 内） |
| `12_periodic_peak_analysis.py` | `periodic_peak_analysis.csv` | 19:01 | 是 |
| `14_sensitivity_analysis.py` | `sensitivity_analysis_final.csv` | 19:08 | 是 |
| `16_generate_report_tables.py` | `global_exponent_robustness_models.csv` 等 | 19:08 | 是 |
| `17_qc_and_sensitivity_followup.py` | QC 对照模型 | 19:08 | 是 |
| `18_compare_with_preschool_study_checks.py` | `compare_preschool_study/*.csv` | 19:08 批次 | 是 |
| `19_development_and_reliability_extension.py --overwrite` | `development_interaction_models.csv` + 图 | **2026-05-20 19:08** | 是 |

**未重跑（与 sex 无关）**：`02–06` 预处理、PSD、specparam 拟合（不读 sex）。

**建议可选**：`21_make_paper_figures_v2.py`（图注数字来自 OLS，主效应未变；若图含 sex 分层注释可酌情重跑）。

---

## 4. 主效应与 sex 系数：修正前 vs 修正后

| 项 | 修正前（误编码，~5/19） | 修正后（2026-05-20） | 稿件是否可保留 |
|----|-------------------------|----------------------|----------------|
| exponent `C(group)[T.TD]` | 0.07908, p=.012 | **0.07908, p=.012** | **可** |
| exponent `C(sex)[T.M]` | **+0.0195**, p=.526 | **−0.0195**, p=.526 | 解释需按修正后（参照=F） |
| offset `C(group)[T.TD]` | 0.0596, p=.095 | **0.0596, p=.095** | **可** |
| offset `C(sex)[T.M]` | −0.0353 | **+0.0353** | 解释需按修正后 |
| `group×age` exponent | 0.003314, p=.020 | **0.003314, p=.020** | **可** |
| `group×age` offset | 0.003749, p=.021 | **0.003749, p=.021** | **可** |
| 稳健性 model_4 β | 0.07908 | **0.07908** | **可** |
| FDR 显著通道 | E33,E36,E37,E38 | **仍为 4 个**（方向 TD>ASD） | **可** |
| split-half ρ | 0.959–0.972 | **不变**（不依赖 sex） | **可** |

---

## 5. 对稿件/讨论的影响

- **摘要、结果 §3.2–3.4、Table 2、图 2–3**：主效应与交互数字 **无需因 sex 修正而改动**。  
- **Table 1**：已为 **5 F / 56 M（ASD）**，**28 F / 49 M（TD）**。  
- **讨论 §4.9 性别不均衡**：应写 **ASD 以男性为主**，而非此前误表下的“女性偏多”。  
- **v8 讨论 Risk note** 中“需重跑主分析”一项 **可关闭**（已完成）。  
- 若报告 **`C(sex)[T.M]`**：修正后表示 **男性相对女性的增量**（参照=F），p 仍不显著。

---

## 6. 复现命令（记录）

```text
python scripts/sync_participants_from_resting_info.py
python scripts/01_prepare_participants.py
python scripts/07b_table1_main_cohort.py
python scripts/08_main_group_analysis.py
python scripts/09_roi_mixed_model.py
python scripts/10_channel_level_analysis.py
python scripts/11_clinical_correlation.py
python scripts/12_periodic_peak_analysis.py
python scripts/14_sensitivity_analysis.py
python scripts/16_generate_report_tables.py
python scripts/17_qc_and_sensitivity_followup.py
python scripts/18_compare_with_preschool_study_checks.py
python scripts/19_development_and_reliability_extension.py --overwrite
```

---

*审计完成。核心组间结论在正确性别编码下得到确认。*
