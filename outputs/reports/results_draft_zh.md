# Results（正式稿 · 中文）

静息态睁眼 EEG（EGI HydroCel-64）经 specparam 分解（fixed aperiodic 模式，1–40 Hz）。**主分析** *N* = 138（ASD *n* = 61，TD *n* = 77）。回归系数 `C(group)[T.TD]` 表示 TD 相对 ASD（参照组）的增量。

---

## 3.1 样本纳入与数据质量

共 168 名被试具备可分析静息态 EEG 及元数据（ASD 80，TD 88）。预处理后，145 名达到预设最少可用 epoch（≥ 60 个 2 s 分段）；另 7 名因 specparam 被试级拟合质量不达标（无效通道比例过高）排除。主分析完整病例为 **138 名**（ASD **61**，TD **77**）（`outputs/tables/sample_inclusion_flow.csv`）。

表 1 显示两组年龄无显著差异；全样本中 TD 组 IQ 高于 ASD 组（约 113 vs 93，*p* < 0.001），主分析模型均校正 IQ。组平均 PSD 见图 1（`fig01_group_mean_psd.png`）。对代表被试的 specparam 拟合进行肉眼抽查（`outputs/figures/qc_specparam_review/`），1–40 Hz 范围内整体拟合可接受。

---

## 3.2 全脑 aperiodic exponent 的组间差异

在控制年龄、性别、IQ_total 及可用 epoch 数后，TD 组 **global aperiodic exponent** 显著高于 ASD 组（β = **0.079**，SE = 0.031，**p = 0.012**，95% CI [0.018, 0.140]，*n* = 138）。

未校正描述统计：ASD *M* = 1.69（*SD* = 0.14），TD *M* = 1.79（*SD* = 0.14）。**较高的 exponent 表示功率谱斜率更陡，即高频功率相对于低频功率下降更快**；ASD 组 exponent 较低，提示其 1/f 背景相对**更平坦**。

**Global aperiodic offset** 呈 TD > ASD 趋势（β = 0.060，*p* = 0.095）。见图 2（`fig03_global_exponent.png`）。

---

## 3.3 稳健性与敏感性分析

### 协变量模型

组效应方向在所有模型中均为 TD > ASD（`global_exponent_robustness_models.csv`）：

| 模型 | β (TD vs ASD) | *p* |
|------|---------------|-----|
| 仅组别 | 0.096 | < 0.001 |
| + 年龄、性别 | 0.090 | < 0.001 |
| + IQ | 0.080 | 0.011 |
| **主模型（+ 可用 epoch）** | **0.079** | **0.012** |
| + 平均拟合 *R*² | 0.056 | 0.030 |
| + 坏导数量 | 0.081 | 0.011 |

主分析队列中无 IQ < 70 的被试；“排除低 IQ”模型与主模型相同。

### 频率与 aperiodic 模式

在 **fixed** 模式下，拟合频段为 1–40、2–40、1–35 或 2–35 Hz 时，组效应方向一致（*p* = 0.016–0.031；`sensitivity_analysis_final.csv`）。**knee** 模式下方向相同，但统计证据较弱（*p* ≈ 0.08–0.16），仅作补充报告。将最少 epoch 阈值设为 30 或 60 时，组效应估计相近（β ≈ 0.074，*p* ≈ 0.019）。

---

## 3.4 空间分布（探索性）

### 基于 HydroCel-64 初步 ROI 分组

在五类初步 ROI（frontal、central、temporal、parietal、occipital；`config/roi_channels.yaml`）的混合模型中，组别主效应未显著（*p* = 0.44），但 **组别 × ROI 交互显著**（`roi_mixed_model.csv`；`fig05_roi_exponent.png`）。与 central ROI 相比，frontal、temporal、parietal 与 occipital ROI 上 TD 与 ASD 的差异幅度更大（交互项 *p* 约 0.001–0.02）。上述 ROI 划分基于电极空间位置的初步分组，**不作具体皮层来源推断**。

### 通道水平

64 通道组间比较经 FDR 校正后，**E33、E36、E37、E38** 仍显著（FDR *p* < 0.05），方向均为 TD > ASD（`significant_channels_fdr.csv`；`fig07_channel_exponent_topomap.png`）。对照 HydroCel-64 电极布局图，上述编号对应顶–枕过渡区及枕正中 **Oz（E37）** 邻近电极（与 ERP 文献中后部 Pe 记录位点 33、36、38 等一致）；本研究 ROI 配置亦将 E33、E36–E38 划入 occipital 分组。据此将效应保守表述为 **顶–枕部 HydroCel-64 通道（parieto-occipital）**，**不作具体皮层来源推断**。

---

## 3.5 周期峰参数

在控制协变量后，alpha 峰中心频率、峰功率、峰带宽及 theta、beta 峰功率的组别主效应**均未显著**（所有 group 项 *p* > 0.24；`periodic_peak_analysis.csv`）。相比之下，周期峰参数未显示显著组间差异，**本研究观察到的组间差异主要由非周期 exponent 驱动**（specparam 分离结果）。

---

## 3.6 临床关联（探索性；ASD）

临床分析仅纳入与主分析一致的 ASD 被试（通过 EEG 与 specparam 被试级 QC，*n* = **61**）。ADOS 子分来自 Resting_info：**ADOS-2** → 总分；**Social** → `ADOS_SA`；**Communication** → `ADOS_communication`（**非**标准 ADOS RRB 域；见 `clinical_model_n_and_variable_check.csv`）。

在完整病例中，global exponent 与 ADOS 总分（*p* = 0.188）、Communication 子分（*p* = 0.257）均未达显著。ADOS Social（`ADOS_SA`）与 global exponent 的关联呈负向趋势（OLS *p* = 0.057），未达 α = 0.05。颞叶 ROI exponent 与语言分数（*n* = 55，*p* = 0.319）亦无显著关联。

**上述临床结果均为探索性，未达到传统显著性阈值。**

---

## 图表索引

| 项目 | 文件 |
|------|------|
| 样本流程 | `sample_inclusion_flow.csv` |
| 主模型 + 稳健性 | `global_exponent_robustness_models.csv` |
| 临床变量核查 | `clinical_model_n_and_variable_check.csv` |
| Fig 1 PSD | `fig01_group_mean_psd.png` |
| Fig 2 Exponent | `fig03_global_exponent.png` |
| Fig 3 ROI | `fig05_roi_exponent.png` |
| Fig 4 通道 | `fig07_channel_exponent_topomap.png` |
