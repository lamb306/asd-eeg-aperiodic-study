# 补充材料：分析脚本与复现说明

**对应论文稿**：`outputs/reports/manuscript_draft_zh_v11_final.docx`（同源 Markdown：`manuscript_draft_zh_v11_final.md`）

**GitHub 仓库**：<https://github.com/lamb306/asd-eeg-aperiodic-study>（论文方法 §2.9 已引用）

**研究主题**：自闭症谱系障碍（ASD）与典型发育（TD）儿童静息态 EEG 非周期成分（specparam）比较，含主统计、敏感性、ICLabel 伪迹控制、年龄交互、分半信度及 nested CV 机器学习补充分析。

---

## 本文件夹内容

| 文件 | 说明 |
|------|------|
| `01_脚本与论文章节对照表.md` | 论文章节 / 图表 / 补充表 ↔ 脚本 ↔ 主要输出路径 |
| `02_运行流水线.md` | 推荐运行顺序、依赖安装、注意事项 |
| `run_v11_pipeline.bat` | Windows 一键顺序调用（需在项目根目录执行） |
| `requirements_reference.txt` | 与项目根目录 `requirements.txt` 一致的依赖列表 |
| `scripts/` | 与主分析对应的脚本**副本**（便于课程打包；**请从项目根目录运行 `scripts/` 下原版**，见下文） |

---

## 如何运行（重要）

所有 Python 脚本假定**当前工作目录为项目根目录** `asd_eeg_aperiodic_study/`，并依赖同级的 `config/`、`src/`、`data/`、`derivatives/`。

```powershell
cd d:\asd_eeg_aperiodic_study
.venv\Scripts\activate
pip install -r requirements.txt
pip install mne-icalabel   # 仅 ICLabel 敏感性分析需要

# 按顺序运行（亦可双击 run_v11_pipeline.bat）
python scripts\00_check_environment.py
# … 详见 02_运行流水线.md
```

`supplementary_materials_v11/scripts/` 内文件仅供提交审阅；路径解析以项目根下 `scripts/` 为准。

---

## 课程作业打包建议

将以下目录/文件一并压缩提交（勿包含受试者原始 EEG，除非课程允许）：

1. 论文：`manuscript_draft_zh_v11_final.docx`
2. 本文件夹：`outputs/reports/supplementary_materials_v11/`
3. 项目脚本与模块：`scripts/`（00–28 相关条目）、`src/`、`config/`
4. 依赖说明：`requirements.txt`
5. （可选）已生成的图表：`outputs/figures/paper_ready_v2/`、`outputs/figures/extension/`、`outputs/ml_biomarker/`

---

## 不在 v11 稿范围内的脚本

电影 ISC、HBN 外部验证、post-QC 匹配队列等扩展分析（如 `scripts/31+`、`scripts/69+`、`scripts/81+`）未纳入本补充材料，与 v11 静息态主文无关。
