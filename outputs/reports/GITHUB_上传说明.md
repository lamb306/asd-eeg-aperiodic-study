# 将本项目推送到 GitHub

目标仓库：**https://github.com/lamb306/asd-eeg-aperiodic-study**

## 仓库内容（已精简）

仅跟踪 **NC 叙事版静息态论文** 相关文件：

- 主分析流水线 `scripts/00`–`17`、`90`–`92`、`94`
- ICLabel 敏感性 `23`、机器学习 `25`/`26`/`30`
- 对应 `src/` 模块与 `config/`
- 稿件：`manuscript_NC_revised_zh_clean.docx`、`manuscript_NC_revised_zh_with_figures.docx`
- 补充材料说明目录 `supplementary_materials_v11/`

**不包含**：电影 ISC、HBN 外部、connectivity、mediation、epoch 变异性、旧版 v11 拼图脚本等（见 `.gitignore`）。

## 推送

```powershell
cd d:\asd_eeg_aperiodic_study
git add .
git status
git commit -m "Update repo for NC manuscript pipeline and figures"
git push origin main
```

推送时需 GitHub 登录或 [Personal Access Token](https://github.com/settings/tokens)。
