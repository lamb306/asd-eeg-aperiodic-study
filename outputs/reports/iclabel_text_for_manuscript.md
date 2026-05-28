# ICLabel 敏感性分析 — 可粘贴稿件段落

> 自动生成；请勿覆盖主分析。分析名称：**artifact-control sensitivity analysis**（伪迹控制敏感性分析）。

## Methods（中文）

为检验残留眼动或肌电伪迹是否影响非周期 exponent 的组间效应，我们在不改动主分析流水线的前提下，另行开展 **伪迹控制敏感性分析**。对每名被试的连续 EEG 重新进行 extended infomax ICA（`random_state=97`），并使用 **mne-icalabel**（ICLabel）对独立成分进行自动分类。当某成分在眼动、肌电、心电、工频或通道噪声类别上的概率 ≥ 0.70 时予以剔除；脑活动与其他类别成分保留。随后在 `derivatives/preprocessed/iclabel_cleaned/` 与 `derivatives/epochs/iclabel_cleaned/` 下重新分段、估计 Welch PSD 并拟合 specparam（fixed 模式，1–40 Hz）。在通过主分析相同纳入与 specparam QC 标准的队列（*N* = 138）上，拟合与主分析一致的 OLS 模型：`global_exponent` / `global_offset` ~ 组别 + 年龄 + 性别 + IQ + 可用 epoch 数。本分析 **未** 使用 HAPPE 或 MARA。

## Methods（英文模板）

To address whether residual ocular or myogenic artifacts could influence the aperiodic exponent group effect, we conducted an **artifact-control sensitivity analysis** separate from the primary pipeline. Continuous EEG was re-processed with extended infomax ICA (`random_state=97`) and independent component labels from **mne-icalabel** (ICLabel). Components with artifact-class probabilities ≥ 0.70 (eye blink, muscle artifact, heart beat, line noise, channel noise) were removed; brain and other components were retained. Epochs, Welch PSD, and specparam (fixed mode, 1–40 Hz) were recomputed under `derivatives/*/iclabel_cleaned/` without altering primary outputs. The same OLS models as the primary analysis (`global_exponent` / `global_offset` ~ group + age + sex + IQ + usable epochs) were fit on the primary cohort (*N* = 138 after identical QC rules). This procedure is **not** HAPPE or MARA.

## Results（中文）

ICLabel 处理成功 276 名被试；平均剔除 3.4 个 ICA 成分（占 11.4%），保留成分的平均最大伪迹类概率为 0.082。在概率阈值 0.70 下，global aperiodic exponent 的 TD − ASD 效应为 β = 0.053，*p* = 0.119（*n* = 137），主分析为 β = 0.079，*p* = .012。敏感性分析与主分析在效应方向上 **不一致或减弱**。

## Results（英文模板）

ICLabel processing succeeded in 276 subjects (mean removed components = 3.4, mean removed fraction = 11.4%, mean max retained artifact probability among kept components = 0.082). After ICLabel cleaning (threshold = 0.70), the global exponent TD − ASD effect was β = 0.053, *p* = 0.119 (*n* = 137), compared with the primary β = 0.079, *p* = .012. The sensitivity analysis was **attenuated (weaker evidence)** with the primary direction.

The group effect was attenuated after ICLabel-based artifact removal (β = 0.053, p = 0.115), suggesting that residual artifacts may partly contribute to the primary effect and should be considered in interpretation.

## Discussion（中文）

ICLabel 敏感性分析用于评估：在自动剔除高概率眼动/肌电相关成分后，非周期 exponent 的 ASD–TD 差异是否仍然存在。若与主分析方向一致，则支持组间差异不太可能仅由 ICLabel 可检测的残留伪迹驱动；若效应减弱或反转，则应在讨论中更谨慎地表述，并考虑补充人工 ICA 复核。该分析 **不替代** 主分析预处理流程。

## Discussion（英文模板）

The artifact-control sensitivity analysis using ICLabel was intended to test robustness of the aperiodic exponent finding to automated ocular and myogenic artifact removal. Agreement with the primary effect would support interpretation that group differences in 1/f slope were not solely driven by residual artifacts detectable by ICLabel; divergence would warrant more conservative wording and further manual ICA review.

## Limitations（中文）

ICLabel 在原始训练中假设平均参考、extended infomax 及约 1–100 Hz 数据；本敏感性分支若复用已低通至 45 Hz 的清洗数据，分类性能可能受影响。本研究 **未** 运行 HAPPE 或 MARA。ICLabel 在儿童 EGI 睁眼静息数据上的自动标注应谨慎解释。本分析仅为敏感性补充，不能替代主分析推断。

## Limitations（英文模板）

ICLabel was trained under specific preprocessing assumptions (average reference, extended infomax, approximately 1–100 Hz data). Our sensitivity branch may use cleaned continuous data that differ from those assumptions (e.g., lower low-pass if reloaded from prior preprocessing). ICLabel is not HAPPE, MARA, or HAPPE-style automated pipelines unless explicitly run. Automatic labels on pediatric EGI resting-state data should be interpreted cautiously. This analysis supplements but does not replace the primary preprocessing and main inferential results.
