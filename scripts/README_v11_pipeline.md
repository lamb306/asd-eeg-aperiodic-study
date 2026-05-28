# v11 论文分析脚本（仅此目录下文件纳入 GitHub）

对应稿件：`outputs/reports/manuscript_draft_zh_v11_final.docx`

| 阶段 | 脚本 |
|------|------|
| 环境 | `00_check_environment.py` |
| 数据 | `01_prepare_participants.py` |
| 预处理–specparam | `02`–`06` |
| 主统计 | `07`, `07b`, `08`–`12`, `14`, `16`, `17` |
| 年龄/信度/对照 | `18`, `19_development_and_reliability_extension.py` |
| ICLabel 敏感性 | `23_iclabel_artifact_sensitivity.py` |
| 机器学习 | `26`, `25`, `28`, `30`（可选 SHAP） |
| 论文图 | `21_make_consort_flow_paper.py`, `21_make_paper_figures_v2.py` |
| QC 图（可选） | `19_plot_specparam_qc_review.py` |

运行顺序见 `outputs/reports/supplementary_materials_v11/02_运行流水线.md`。
