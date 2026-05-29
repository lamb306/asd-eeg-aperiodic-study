# NC 叙事版论文分析脚本（GitHub 仓库仅跟踪本清单）

对应稿件：
- `outputs/reports/manuscript_NC_revised_zh_clean.docx`
- `outputs/reports/manuscript_NC_revised_zh_with_figures.docx`（含主图 + Extended Data）

## 主分析流水线

| 阶段 | 脚本 |
|------|------|
| 环境 | `00_check_environment.py` |
| 数据 | `01_prepare_participants.py` |
| 预处理–specparam | `02`–`06` |
| 主统计 | `07`, `07b`, `08`–`12`, `14`, `16`, `17` |
| 年龄交互 / 分半信度 | `19_development_and_reliability_extension.py` |
| 学前对照与 fixed/knee 敏感性表 | `18_compare_with_preschool_study_checks.py` |
| ICLabel 敏感性 | `23_iclabel_artifact_sensitivity.py` |
| 规范模型（Figure 4） | `90_normative_exponent_analysis.py` |
| IAF / 年龄联合模型（Figure 5E） | `91_spectral_maturation_joint_model.py` |
| 非线性年龄敏感性（Figure 3） | `92_nonlinear_age_sensitivity.py` |
| 机器学习（Extended Data） | `25`, `26`, `30`（可选 SHAP） |
| **NC 主图生成 + 写入 Word** | `94_nc_figures_and_manuscript.py` |

## 一键生成 NC 图并插入稿件

```bash
python scripts/94_nc_figures_and_manuscript.py
```

输出图：`outputs/figures/nc_manuscript/Figure1_*.png` … `ExtendedData_Figure1_*.png`  
输出稿：`outputs/reports/manuscript_NC_revised_zh_with_figures.docx`

## 不包含（非 NC 主线）

电影 ISC、HBN 外部、connectivity/wPLI、mediation、epoch-level 变异性、旧版 v11 拼图脚本等——见根目录 `.gitignore`。
