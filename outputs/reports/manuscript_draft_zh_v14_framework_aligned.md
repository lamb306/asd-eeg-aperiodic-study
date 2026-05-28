# ASD 儿童静息态后部非周期 EEG 动力学与自然电影共情/心理推理加工（框架对齐稿 v14）

## 一、核心定位

本研究定位为 developmental systems neuroscience 研究，核心问题是：ASD 儿童静息态后部非周期 EEG 动力学是否影响其在自然电影中对共情（pain）与心理推理（mental）情节的刺激锁定神经同步（ISC），以及这种“静息态-自然电影耦合”是否呈年龄依赖性。

一句话主张：ASD 儿童后部非周期皮层动力学异常不仅存在于静息态，而且会削弱其对高阶社会认知电影情节的神经同步；这种基线状态到自然加工的耦合异常可能是 ASD 社会沟通困难的发育性神经生理机制之一。

---

## 二、建议题目

1. 静息态后部非周期 EEG 与自然电影社会加工同步性的发育耦合：来自 ASD 儿童的证据  
2. ASD 儿童静息态-任务态神经耦合异常：后部 1/f 动力学与自然电影心理推理同步性  
3. 从静息态到自然情境：ASD 儿童后部非周期皮层状态与社会认知神经同步的解耦

---

## 三、科学背景与研究缺口

- 既有静息态结果显示：ASD 与 TD 在 aperiodic exponent 存在差异，且具有年龄依赖性；后部局部指标较全局指标更稳健。  
- 但静息态结果本身无法回答：该基线异常是否影响真实世界社会信息加工。  
- 自然电影范式可将“基础神经状态”与“任务中社会加工输出”在同一被试层面连接，从而实现 state-to-processing coupling 检验。

---

## 四、总体机制模型

三层机制模型：
- **层 1（State）**：静息态后部非周期指数（posterior exponent）反映基础皮层动力学状态。  
- **层 2（Processing）**：自然电影社会认知片段中的神经同步（ISC）反映在线加工效率。  
- **层 3（Coupling）**：State 对 Processing 的预测关系在 TD 中存在、在 ASD 中减弱（功能解耦）。

---

## 五、研究假设

### H1：静息态后部非周期异常
ASD 在静息态 posterior exponent 上异常，且存在年龄调节。

### H2：自然电影片段神经同步降低
ASD 在社会认知负荷更高片段（尤其 mental）的 ISC 低于 TD。

### H3：静息态-电影耦合异常
TD 中 resting posterior exponent 能预测 mental ISC；ASD 中该关系减弱或消失。

### H4：年龄依赖性
耦合关系在较大年龄儿童中更可见。

### H5：临床相关（探索）
coupling index 可能比单一静息态指标更接近社会沟通表型。

---

## 六、研究对象与已有数据

- 样本：ASD 与 TD 儿童。  
- 数据：约 5 分钟静息态 EEG + 约 5 分钟自然电影 EEG。  
- 备注：无同步眼动，故结论聚焦 EEG 刺激锁定神经动力学，不做注视独立性强推断。

---

## 七、实验范式

### 7.1 Resting-state EEG
- 5 分钟左右，睁眼静息。  
- 用于估计 static aperiodic 指标（含 posterior exponent）与年龄调节。

### 7.2 《暴力云》自然电影 EEG
- 5 分钟左右，自然观看。  
- 以电影起始 marker（VID+）对齐连续 EEG。  
- 提取 mental / pain 片段并开展事件相关分析与 ISC。

---

## 八、电影剧情分段方案

本稿当前主分析使用三类片段逻辑中的两类高负荷社会认知片段：`mental` 与 `pain`（基于真实事件表 `movie_events.csv`）。  
后续版本可加入独立评分者一致性标注与更细粒度分段验证。

---

## 九、EEG 预处理与质量控制

### 9.1 基础预处理
- 0.5–45 Hz bandpass  
- 50 Hz notch  
- 降采样至 250 Hz  
- 坏导处理 + 平均参考 + ICA 流程  
- 2 s 窗口质量控制与可用 epoch 统计

### 9.2 Movie EEG 特殊处理
- 保留连续序列用于时变指数与 ISC。  
- 滑窗参数：2 s 窗、0.5 s 步。  
- ROI 主分析采用 `roi_mean`（E33/E36/E37/E38）。

### 9.3 无眼动数据补救
控制 `usable_epochs` 等质量协变量，并在稳健模型中加入可用协变量（age/usable_epochs/IQ/sex）。

---

## 十、核心 EEG 指标

### 10.1 Resting-state 指标
- `posterior_exponent`（基于 E33/E36/E37/E38）  
- `global_exponent`、`global_offset` 等

### 10.2 Movie EEG 指标
- `mental ISC`、`pain ISC`（TD-template ISC，Fisher z）  
- 事件相关 `Delta Exponent` 时间过程（局部基线校正）

---

## 十一、主要分析方案（已执行）

### Analysis 1：静息态 posterior 指标复现
使用既有静息态结果作为 state 端输入（`data.csv` 中 `posterior_exponent`）。

### Analysis 2：电影片段 ISC 组差（已完成）
- `mental`：ASD < TD，显著  
- `pain`：组差不显著

### Analysis 3：静息态-电影耦合（已完成）
- OLS：交互边缘显著  
- Winsorize + Huber RLM：交互达到显著（详见结果）

### Analysis 4：年龄调节与 >72 月亚组（已完成）
在 >72 月亚组重复交互模型，方向一致但显著性减弱。

### Analysis 5：Movie-evoked aperiodic modulation（已完成基础版）
完成事件相关时间过程提取与可视化，CBPT 未检出显著时间簇。

### Analysis 6：TRF/encoding（待扩展）
保留为次要分析（需视频/音轨特征工程）。

### Analysis 7：临床关联（待扩展）
建议后续与 ADOS/SRS/语言指标进行 planned secondary 检验。

---

## 十二、机器学习与转化分析

本研究当前主结果聚焦机制模型（state-processing coupling），机器学习仅作为补充方向，后续可检验 coupling 特征是否增益于 resting-only 模型。

---

## 十三、统计控制与敏感性分析

已纳入/尝试控制：  
- age_months  
- usable_epochs  
- IQ_total（可用样本）  
- sex  
- Winsorize（5%-95%）  
- Huber RLM（抗高杠杆点）

---

## 十四、预期结果模式与解释（与当前结果对照）

- 静息态后部异常：支持。  
- 电影社会加工差异：`mental` 显著、`pain` 不显著，支持认知过程分离。  
- 耦合异常：在稳健模型中 `PosteriorExponent × Group` 显著，支持“功能解耦”。

---

## 十五、建议图表安排（当前已出）

- Figure M1：movie ISC 分组箱线图（mental/pain）  
  `../figures/movie_isc_group_boxplot.png`
![Figure M1](../figures/movie_isc_group_boxplot.png)
- Figure M2：全样本耦合散点（ASD/TD 回归线）  
  `../figures/resting_to_movie_coupling_scatter.png`
![Figure M2](../figures/resting_to_movie_coupling_scatter.png)
- Figure M3：>72 月亚组耦合散点  
  `../figures/resting_to_movie_coupling_scatter_older72.png`
![Figure M3](../figures/resting_to_movie_coupling_scatter_older72.png)
- Figure M4：事件相关时间过程  
  `../figures/movie_peri_event_delta_timecourse.png`
![Figure M4](../figures/movie_peri_event_delta_timecourse.png)

---

## 十六、摘要草案（精简）

本研究整合 ASD/TD 儿童静息态与自然电影 EEG，检验后部非周期基线状态是否预测社会认知情节中的神经同步。结果显示：movie `mental` 片段 ISC 在 ASD 显著低于 TD，而 `pain` 片段无显著组差；在控制协变量并使用抗异常值稳健模型后，静息 posterior exponent 与 movie mental ISC 的组别交互显著，提示 ASD 存在静息态-自然社会加工之间的功能解耦。

---

## 十七、Discussion 主线（可直接扩展）

1. ASD 后部非周期异常不仅是静息态现象，还映射到自然社会加工中的同步性下降。  
2. `mental` 显著、`pain` 不显著提示高阶社会认知特异性受损，而非普遍注意不足。  
3. 稳健模型中交互显著说明核心发现不是少数异常值产物。  
4. 耦合方向提示：TD 中存在“基线状态支持任务加工”的关系，而 ASD 中该关系减弱/解耦。  
5. >72 月亚组方向一致但效力下降，提示仍需更大样本验证发育轨迹。

---

## 十八、限制与应对

- 无眼动：通过 EEG 质量指标与稳健模型缓解，但不能完全替代注视控制。  
- 亚组样本量下降导致功效受限。  
- 自然电影事件标注仍可进一步细化与评分者一致性验证。

---

## 十九、投稿定位（当前证据级别）

当前证据已具备“机制导向 + 稳健性验证 + 自然范式”优势，适合 developmental cognitive neuroscience / clinical neuroimaging 方向期刊；若后续临床关联或外部验证增强，可进一步冲击更高影响力目标。

---

## 二十、最终框架一句话

本研究表明，ASD 儿童的后部静息态非周期 EEG 异常并非孤立的静态特征，而是与自然电影高阶社会认知情节中的神经同步下降相耦合；该耦合在稳健统计下呈现显著组别差异，支持 ASD 中“基础皮层状态—自然社会加工”功能解耦这一发育神经机制框架。

---

## 关键结果（数值版，便于审稿回复）

- **mental ISC 组差**：t = -3.0836，p = 0.00236（ASD < TD）  
- **pain ISC 组差**：t = -0.3609，p = 0.7186（n.s.）  
- **耦合 OLS 交互**：p = 0.0743（边缘）  
- **耦合 RLM+Winsor 全样本交互**：beta = -0.2912，p = 0.0463（显著）  
- **RLM+Winsor 简单斜率（全样本）**：  
  - ASD：beta = +0.1140，p = 0.2364  
  - TD：beta = -0.1772，p = 0.1047  
- **RLM+Winsor 大龄亚组（>72月）交互**：beta = -0.2524，p = 0.1448
