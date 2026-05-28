# Final Integration Audit (v10)

## 1) 新增整合内容总览

本轮在 v9 基础上新增并整合了“自动 ICA 后局部后部 exponent”结果，生成 v10 投稿稿，包含：

- 主文 Results 新增小节：`3.9 自动 ICA 后局部后部 exponent 的稳健性`。
- 主文新增结果表：`Table 3. Local posterior exponent effects after automated ICA artifact control`。
- Supplementary 新增：`Table S10` 与 `Figure S4`。
- Discussion 新增小节：`4.10 局部后部 exponent 的稳健性与跨研究解释（中英对照）`。
- 摘要 Results/Conclusion 增加局部后部 exponent 的稳健显著性结论句。

## 2) 新增统计摘要（审稿人关注）

### 2.1 全自动 ICA 后局部后部 exponent（E33/E36/E37/E38 平均）

四项关键检验（均控制 age_months、sex、IQ_total、usable_epochs）：

- 0.70 阈值，全样本：β = 0.121，95%CI [0.054, 0.189]，p = 0.000485，BH-FDR p = 0.0078
- 0.80 阈值，全样本：β = 0.128，95%CI [0.054, 0.201]，p = 0.000814，BH-FDR p = 0.0098
- 0.70 阈值，older_child：β = 0.151，95%CI [0.077, 0.226]，p = 0.000108，BH-FDR p = 0.0052
- 0.80 阈值，older_child：β = 0.160，95%CI [0.077, 0.244]，p = 0.000240，BH-FDR p = 0.0058

### 2.2 与全局指标对照

- automated ICA 后 `global_exponent`（全样本）不显著（约 p = 0.115–0.119）。
- 结论：局部后部 exponent 在自动 ICA 场景下较全局指标更稳健。

## 3) 稳健性判断

- **跨阈值稳健**：0.70/0.80 两阈值方向一致且均显著。
- **跨样本层稳健**：全样本与 older_child 子样本均显著。
- **多重比较稳健**：在 48 个局部检验做 BH-FDR 后，4 项关键结果全部保留（p_FDR < 0.01）。
- **与既有发现一致**：与先前后部通道显著（E33/E36/E37/E38）空间分布线索一致。

## 4) 仍需投稿前补充/核对细节

1. Methods 中建议补一句（或在 ICA 子节明确）：
   - “局部后部指标定义为 E33/E36/E37/E38 的被试内通道平均，并沿用主模型协变量（age_months、sex、IQ_total、usable_epochs）。”
2. 在 Supplementary Methods 建议补充：
   - 48 个局部检验的组成（指标 × 阈值 × 子样本）与 BH-FDR 范围说明。
3. 若期刊要求严格可追溯，建议增加一句：
   - “局部后部分析为预先空间线索驱动的后续验证（topography-informed follow-up），非无约束全空间筛选。”
4. 参考文献：本轮未新增虚构引用；mne-icalabel/ICLabel 条目沿用既有版本。

## 5) 推荐写法示例（可直接用于答审）

### 5.1 Results 推荐句

> 在 fully automated ICA artifact-control sensitivity analysis 后，global exponent 在全样本中不再显著；但局部后部通道均值 exponent（E33/E36/E37/E38）在 0.70 与 0.80 阈值下、全样本与 older_child 子样本中均显著，且在 48 个局部检验的 BH-FDR 校正后全部保留（p_FDR < 0.01）。

### 5.2 Discussion 推荐句

> 该模式提示全脑平均指标更易受伪迹控制与脑区异质性的衰减影响，而后部局部 aperiodic exponent 保留了更高的组间分辨能力，支持其作为本队列中更稳健的 ASD–TD 静息态差异信号。

### 5.3 Abstract 推荐句

> Regionally, posterior exponent (E33/E36/E37/E38 average) remained robustly different between TD and ASD even after automated ICA artifact control (all four key tests survived BH-FDR, p_FDR < 0.01).

## 6) 产物核对

- `outputs/reports/manuscript_draft_zh_v10_final.md` 已生成。
- `outputs/reports/manuscript_draft_zh_v10_final.docx` 已生成（含目录域、题注域、图表嵌入、交叉引用锚点）。
- `outputs/reports/final_integration_audit.md`（本文件）已更新。

