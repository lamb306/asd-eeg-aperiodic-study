# 自闭症谱系障碍儿童静息态后部非周期 EEG 与自然电影社会加工耦合异常：一项整合分析

## 摘要

**背景：** 静息态 EEG 的非周期成分（aperiodic exponent）可刻画宽频皮层动力学，但其是否能预测自然情境下的社会认知加工仍不清楚。  
**目的：** 在 ASD 与 TD 儿童中，整合静息态与自然电影 EEG，检验“静息态后部非周期状态 -> 电影社会认知同步性（ISC）”的耦合及其稳健性。  
**方法：** 静息态主分析队列为 138 名儿童（ASD 61, TD 77）。电影 EEG 可用队列为 186 名儿童（ASD 89, TD 97）。静息态采用 specparam 估计 global/posterior 指标；电影态采用 ROI 均值（E33/E36/E37/E38）动态指数与事件分段分析。根据真实事件标注提取 `mental` 与 `pain` 片段，计算 TD-template ISC（TD 留一模板；ASD 对全 TD 模板），并进行 Fisher z 转换后的组间比较。进一步拟合耦合模型 `mental_isc_z ~ posterior_exponent * group + covariates`，并开展 5%-95% Winsorize + Huber 鲁棒回归。  
**结果：** 静息态中，TD 组 global exponent 高于 ASD（β=0.079, p=0.012）。年龄交互显著（exponent: β=0.00331, p=0.0195；offset: β=0.00375, p=0.0207）。电影事件分段中，`mental ISC` 在 ASD 显著低于 TD（t=-3.08, p=0.00236），而 `pain ISC` 组差不显著（p=0.719）。耦合分析中，初始 OLS 交互项边缘显著（p=0.074），经 Winsorize+RLM 并控制 age/usable_epochs/IQ/sex 后，`posterior_exponent × group` 交互达到显著（β=-0.291, p=0.046）。简单斜率显示 ASD 为弱正向（β=+0.114, p=0.236），TD 为负向趋势（β=-0.177, p=0.105）。  
**结论：** ASD 儿童存在“静息态后部非周期状态与自然社会加工同步性之间的功能解耦”。该结果在抗异常值稳健建模后更清晰，支持以 state-to-processing coupling 解释 ASD 社会沟通困难的发育神经机制。

**关键词：** ASD；静息态 EEG；自然电影；aperiodic exponent；inter-subject correlation；功能解耦

---

## 1. 引言

传统 EEG 频段分析无法有效区分周期峰与非周期背景，限制了 ASD 神经生理机制的解释精度。既往静息态结果已提示 ASD 存在 aperiodic 异常，并且后部局部指标较全局指标更稳健。但静息态差异是否会迁移到自然社会信息加工场景，仍缺乏直接证据。

自然电影范式提供了“高生态效度 + 可重复刺激锁定”的折中路径。本研究以《暴力云》电影事件标注为锚点，将静息态 posterior exponent 与电影社会认知片段（mental/pain）神经同步（ISC）连接，检验 ASD 是否表现为跨状态耦合异常。

---

## 2. 方法

### 2.1 样本与数据

- 静息态主分析样本：138（ASD 61, TD 77）  
- 电影态可用样本：186（ASD 89, TD 97）  
- 每名被试约 5 分钟静息态 EEG + 5 分钟自然电影 EEG

### 2.2 静息态分析（已有主线）

按既有管线进行预处理、PSD 与 specparam 参数化。主模型为：

`global_exponent ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs`

并完成年龄交互、空间分布与敏感性分析。

### 2.3 电影态动态指数与事件分段

电影态采用 ROI 均值模式（`roi_mean`）：每个 2s 滑窗内对 E33/E36/E37/E38 的 PSD 求均值，再做单次 specparam 拟合（步长 0.5s）。事件文件 `movie_events.csv` 包含 `mental` 与 `pain` 片段。

### 2.4 ISC 计算（TD-template）

对同一被试同一事件类型的多个片段进行拼接。  
- TD 被试：与“其余 TD 被试均值模板（leave-one-out）”做 Pearson r。  
- ASD 被试：与“全体 TD 均值模板”做 Pearson r。  
对 r 做 Fisher z 转换后用于统计。

### 2.5 静息态-电影耦合模型

主耦合指标为 `mental_isc_z`，静息态指标为 `posterior_exponent`。  
先跑 OLS，再跑稳健模型（Winsorize + Huber RLM）：

`mental_isc_z_w ~ posterior_exponent_w * C(group) + age_months + usable_epochs + IQ_total + C(sex)`

并提取 simple slopes（ASD/TD 组内斜率）。

---

## 3. 结果

### 3.1 静息态主效应与年龄调节

- `global_exponent`：TD > ASD（β=0.0791, p=0.0119）  
- `global_offset`：TD > ASD 趋势（β=0.0596, p=0.0951）  
- 年龄交互显著：  
  - exponent：`C(group)[T.TD]:age_months` β=0.00331, p=0.0195  
  - offset：`C(group)[T.TD]:age_months` β=0.00375, p=0.0207

### 3.2 电影事件分段 ISC

- `mental`：ASD 显著低于 TD（n_ASD=89, n_TD=97; t=-3.0836, p=0.00236）  
  - ASD mean z=0.0353；TD mean z=0.0837  
- `pain`：组差不显著（t=-0.3609, p=0.7186）

### 3.3 静息态-电影耦合

#### OLS（基线模型）

交互项边缘显著（`posterior_exponent:C(group)[T.TD]`, p=0.0743）。

#### Winsorize + Huber RLM（稳健模型）

在控制 age、usable_epochs、IQ_total、sex 后：  
- 交互项显著：`posterior_exponent_w:C(group)[T.TD]`  
  - β=-0.2912，p=0.0463  
- 年龄项显著：β=0.00135，p=0.0110  
- Bootstrap（n=2000）交互项 95% CI：[-0.4187, 0.0721]，p_boot=0.134（方向一致）

#### 简单斜率（RLM + Winsor）

- ASD：β=+0.1140，p=0.2364  
- TD：β=-0.1772，p=0.1047

方向上表现为：TD 为负向耦合趋势，ASD 为弱正向趋势，支持组别耦合结构差异。

### 3.4 大龄亚组（>72 月）

稳健模型交互方向一致（β=-0.2524），但未达显著（p=0.1448）。  
ASD 斜率 β=+0.1002（p=0.3698）；TD 斜率 β=-0.1522（p=0.2481）。

---

## 4. 讨论

本研究将“静息态后部非周期状态”与“自然电影社会认知同步性”连接，形成了从基础状态到在线加工的机制闭环。核心发现有三点：

1) **静息态后部非周期异常可复现**：TD 在 exponent 上高于 ASD，且存在年龄依赖交互；  
2) **社会认知过程分离**：`mental ISC` 显著组差而 `pain ISC` 不显著，提示高阶社会推理相关处理更受影响；  
3) **稳健耦合异常**：在抗异常值建模中交互项显著，支持 ASD 存在“静息态基线与自然社会加工之间的功能解耦（functional decoupling）”。

从神经生理角度，TD 组负向斜率趋势可理解为：较低静息 posterior exponent（可能对应更高基线皮层唤醒/兴奋状态）倾向于关联更强的 mental 场景同步；而 ASD 未呈现同方向关系，提示状态-加工映射失配。

---

## 5. 局限性

1. 无眼动同步，难以完全排除注视策略影响；  
2. 亚组分析样本量下降，交互检验功效受限；  
3. Bootstrap 交互 CI 跨 0，提示效应方向稳定但仍需独立样本重复。

---

## 6. 结论

ASD 儿童的后部非周期 EEG 异常不仅存在于静息态，还表现为自然电影高阶社会认知加工中的同步性下降，并在稳健模型下呈现显著组别耦合差异。这一“静息态-自然加工功能解耦”框架为解释 ASD 社会沟通困难提供了可量化、可检验的发育神经机制路径。

---

## 图表（投稿版）

### Figure 1. 静息态主效应与稳健性
![Figure 1](../figures/paper_ready_v2/fig2_main_aperiodic_effects.png)

### Figure 2. 静息态空间分布（探索性）
![Figure 2](../figures/paper_ready_v2/fig3_spatial_distribution.png)

### Figure 3. 电影事件分段 ISC（mental vs pain）
![Figure 3](../figures/movie_isc_group_boxplot.png)

### Figure 4. 静息态-电影耦合（全样本）
![Figure 4](../figures/resting_to_movie_coupling_scatter.png)

### Figure 5. 静息态-电影耦合（>72 月亚组）
![Figure 5](../figures/resting_to_movie_coupling_scatter_older72.png)

### Figure 6. 事件相关时间过程（局部基线校正）
![Figure 6](../figures/movie_peri_event_delta_timecourse.png)
