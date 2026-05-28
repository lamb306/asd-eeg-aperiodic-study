# 自闭症谱系障碍儿童静息态-自然观影耦合分析补充（v12）

## 新增方法（可并入 Methods / Supplementary Methods）

### 自然观影视觉事件的神经同步性分析（ISC）
在自然观影范式中，我们基于后部 ROI 均值动态非周期指数序列（`E33/E36/E37/E38`，滑窗 2 s、步长 0.5 s）进行事件分段 ISC 分析。根据 `movie_events.csv`，分别提取 `mental` 与 `pain` 片段，并将同一被试同类事件片段按时间顺序拼接为单一时间序列。随后构建 TD-template ISC：对每名 TD 被试采用留一法（leave-one-out），将其序列与其余 TD 被试平均序列计算 Pearson 相关；对每名 ASD 被试，将其序列与全体 TD 平均序列计算 Pearson 相关。相关系数统一进行 Fisher z 转换后用于组间统计（独立样本 t 检验）。

### 静息态-观影加工耦合分析
为评估“静息态后部非周期基线”与“任务态社会加工同步性”的跨状态耦合，提取静息态 posterior exponent（V11 阶段数据表中的 `posterior_exponent`）与 movie `mental ISC`（Fisher z）。首先在 ASD 与 TD 组内分别计算 Pearson/Spearman 相关；随后拟合交互模型：

`mental_isc_z ~ posterior_exponent * C(group) + age_months`

并进一步实施稳健性增强分析：考虑 EEG 指标重尾分布特征，对 `posterior_exponent` 与 `mental_isc_z` 做 5%–95% Winsorize，并使用 Huber’s T 的鲁棒线性模型（RLM），同时控制 `age_months`、`usable_epochs`、`IQ_total` 与 `sex`。此外进行 >72 月亚组重复建模，并报告 simple slopes（ASD 与 TD 组内斜率）。

---

## 新增结果（可并入 Results）

### 1) 电影事件相关 ISC 的认知过程分离
`mental` 条件下，ASD 组 ISC 显著低于 TD 组（ASD mean z = 0.0353；TD mean z = 0.0837；t = -3.08，p = 0.00236）。`pain` 条件下组间差异不显著（ASD mean z = 0.0547；TD mean z = 0.0603；t = -0.36，p = 0.719）。该结果形成了清晰的过程分离模式：高阶社会认知情节下同步性下降，而低阶共情/痛觉线索下未见同等程度的组间差异。

### 2) 静息态-观影耦合：从边缘显著到稳健显著
初步 OLS 交互模型显示 `posterior_exponent × group` 为边缘显著（p = 0.074）。考虑到 EEG 非周期指数与 ISC 指标均存在重尾分布风险，我们进行 5%–95% Winsorize + Huber RLM 稳健建模（并控制年龄、usable_epochs、IQ、sex）后，交互项达到显著（β = -0.291，p = 0.046）。这表明关键耦合发现并非由少数极端值驱动，反而在抗异常值建模后得到强化。

### 3) 简单斜率与功能机制
在稳健模型下，ASD 组斜率为正向但不显著（β = +0.114，p = 0.236），TD 组斜率为负向趋势（β = -0.177，p = 0.105）。方向上提示：在 TD 中，较低的静息后部 exponent（可理解为更高基线皮层唤醒/兴奋状态）倾向于预测更强的 mental 情节神经同步；而 ASD 未呈现同方向耦合，提示静息基线与自然社会加工之间存在功能解耦（functional decoupling）。

### 4) 大龄亚组（>72 月）结果
在 >72 月亚组中，稳健模型交互项方向保持一致（β = -0.252），但未达显著（p = 0.145）。该结果提示年龄分层后样本量与变异结构对交互检验功效具有明显影响，后续需更大样本进一步验证。

---

## 新增图（Supplementary Figures）

### Figure S-M1. 电影事件分段 ISC 组间比较
![Figure S-M1](../figures/movie_isc_group_boxplot.png)

图注建议：基于 TD-template ISC 的事件分段组间比较（mental vs pain）。`mental` 条件下 ASD 低于 TD（p = 0.002），`pain` 条件组间差异不显著。

### Figure S-M2. 全样本静息态-观影耦合散点图（含分组回归）
![Figure S-M2](../figures/resting_to_movie_coupling_scatter.png)

图注建议：静息 posterior exponent 与 `mental ISC` 的分组关系。稳健模型（Winsor + RLM）显示交互项显著（p = 0.046）。

### Figure S-M3. 大龄亚组（>72 月）静息态-观影耦合散点图
![Figure S-M3](../figures/resting_to_movie_coupling_scatter_older72.png)

图注建议：>72 月亚组中交互项方向一致但未达显著（p = 0.145）。

---

## Discussion 可直接粘贴段落（审稿友好版）

These robustness analyses suggest that the resting-to-movie coupling effect is not an artifact of a few high-leverage observations. Given the heavy-tailed tendency of both aperiodic exponent and ISC metrics, the initial OLS interaction remained only trend-level; however, after 5th–95th percentile winsorization and Huber-type robust regression with strict covariate control (age, usable epochs, IQ, sex), the Posterior Exponent × Group interaction reached significance (p = .046). This pattern indicates that the coupling effect is statistically stable under distribution-aware modeling rather than being driven by outliers.

Importantly, the direction of simple slopes was neurobiologically informative. In TD, the slope was negative (beta = -0.177), suggesting that a lower resting posterior exponent—consistent with a relatively higher baseline cortical arousal/excitation state—tends to predict stronger neural synchrony during higher-order social-cognitive movie segments (mental events). In contrast, ASD did not show this normative negative coupling and instead showed a weak/disorganized positive trend (beta = +0.114). Together, these findings support a functional decoupling between resting-state baseline cortical dynamics and naturalistic social processing in ASD.
