# 自闭症谱系障碍儿童静息态非周期EEG与自然电影神经同步：主口径（relaxed）与敏感性（strict）整合稿

## 摘要

**背景：** 静息态EEG非周期参数（aperiodic exponent）可表征宽频神经动力学，但其与自然社会认知加工之间的跨状态关系在ASD儿童中仍缺乏稳定证据。  
**目的：** 基于现有锁定结果文件，构建可投稿初稿，明确主口径（relaxed）结果，并将strict口径作为敏感性分析，检验主要结论的稳定性。  
**方法：** 静息态主分析样本按流程筛选为138例（ASD=61，TD=77）；电影事件ISC与耦合分析采用relaxed口径（关键模型n=128，事件比较样本ASD=73，TD=95/96），并与strict口径（关键模型n=102）对照。统计报告包含原始p值、BH-FDR（同家族校正）、效应方向及样本量；另纳入QC协变量控制模型（`mean_fit_error`、`invalid_channel_ratio`）。  
**结果：** 静息态主模型中，TD相对ASD的`global_exponent`更高（β=0.0791，p=0.0119，n=138），`global_offset`仅趋势性（β=0.0596，p=0.0951）。后部通道E33/E36/E37/E38经FDR后仍显著（q=0.0076-0.0360）。电影ISC中，mental、pain、neutral三事件均为TD>ASD且FDR后显著；Delta_Exponent在mental与pain均显著。耦合分析显示：relaxed口径下`posterior_exponent × group`在OLS与RLM均显著，而strict口径下OLS不显著、RLM仍显著。posterior-CARS相关在relaxed显著而strict不显著，提示临床相关对口径敏感。  
**结论：** 可稳健支持的主结论为：ASD在静息态非周期指数与自然电影ISC上均表现出组间差异，且跨状态耦合在稳健模型中存在；但posterior-CARS与部分OLS交互属于口径敏感证据，应降级为探索性发现。

**关键词：** ASD；EEG；非周期指数；自然电影；ISC；稳健回归；敏感性分析

## 1. 引言

ASD神经生理研究长期依赖传统频段功率指标，但该类指标易受非周期背景影响，可能掩盖真正的组间差异维度。已有本项目结果提示，静息态`global_exponent`与后部局部指数可能较周期峰参数更敏感。另一方面，自然电影范式可在较高生态效度下评估社会信息加工的群体神经同步（ISC），为“静息态基础状态 -> 任务态加工输出”提供同一被试层面的连接框架。

本稿聚焦两个问题：  
- relaxed主口径下，ASD与TD在静息态非周期参数、电影ISC及跨状态耦合上是否形成一致证据链；  
- strict口径与QC协变量控制后，哪些结论依旧稳健，哪些应降级为敏感性结论。

## 2. 方法

### 2.1 研究设计与口径定义

- **主口径（relaxed）**：当前锁定主表与快照采用的统计口径，作为主文推断依据。  
- **敏感性口径（strict）**：更严格筛选口径，仅用于稳健性检验，不与主口径混写。  

主口径来源：`outputs/tables/final_paper_stats_locked.csv`、`outputs/tables/_relaxed_significance_snapshot.csv`。  
敏感性来源：`outputs/tables/_strict_significance_snapshot.csv`。  

### 2.2 样本流程与结局

- 静息态流程：168 -> 145（`usable_epochs >= 60`）-> 138（specparam被试QC通过）。  
- 静息态主结局：`global_exponent`、`global_offset`。  
- 空间结局：通道FDR显著通道。  
- 电影结局：事件ISC（mental/pain/neutral）与Delta_Exponent（mental/pain）。  
- 跨状态耦合：`mental_isc_z ~ posterior_exponent * C(group) + covariates`（OLS与RLM winsor）。  

### 2.3 统计与多重比较

- ISC与Delta分别在各自家族内做BH-FDR。  
- 耦合模型报告OLS与RLM并行结果。  
- QC协变量控制模型作为补充路径，不替代主模型。  

## 3. 结果

### 3.1 样本流程与静息态主模型

主分析样本为138例（ASD=61，TD=77）。[来源：`outputs/tables/sample_inclusion_flow.csv`]  

主模型显示`global_exponent`为TD>ASD（β=0.0790819009578286，SE=0.03101320780757809，p=0.01191661743751248，95%CI[0.01773471050987685, 0.14042909140578036]，n=138）。[来源：`derivatives/stats/main_group_analysis.csv`]  

`global_offset`仅趋势性（β=0.05955940846317012，p=0.09506288310582732，n=138）。[来源：`derivatives/stats/main_group_analysis.csv`]  

### 3.2 通道水平FDR结果

通道E33、E36、E37、E38均表现为TD>ASD且经FDR后显著：  
- E33: β=0.10697，p=0.0007939，q=0.02540；  
- E36: β=0.11691，p=0.0016538，q=0.03528；  
- E37: β=0.17054，p=0.0022508，q=0.03601；  
- E38: β=0.13435，p=0.0001181，q=0.00756。  
[来源：`outputs/tables/significant_channels_fdr.csv`]

### 3.3 电影事件ISC（主口径relaxed）

在relaxed主口径中，三类事件均为TD>ASD并经FDR后显著：  
- mental: ASD=73, TD=95, t=-2.302147242807646, raw p=0.0228236392086339, FDR p=0.0228236392086339；  
- pain: ASD=73, TD=95, t=-3.925915102794856, raw p=0.0001356440971062, FDR p=0.00020346614565930002；  
- neutral: ASD=73, TD=96, t=-4.357184001275027, raw p=2.460057653261554e-05, FDR p=7.380172959784662e-05。  
[来源：`outputs/tables/final_paper_stats_locked.csv`；`derivatives_task_movie/stats/movie_isc_group_stats_with_neutral.csv`]

### 3.4 Delta_Exponent（主口径relaxed）

Delta_Exponent在mental与pain均显著：  
- Delta_mental: ASD=56, TD=73, t=3.5009889307920794, raw p=0.0007112589837053, FDR p=0.0007112589837053；  
- Delta_pain: ASD=56, TD=73, t=3.6950391222583874, raw p=0.0003720742183072, FDR p=0.0007112589837053。  
[来源：`outputs/tables/final_paper_stats_locked.csv`；`derivatives_task_movie/stats/delta_exponent_group_ttests.csv`]

### 3.5 跨状态耦合：主口径与敏感性对照

**relaxed主口径（n=128）**：  
- OLS交互项`posterior_exponent:C(group)[T.TD]`显著（β=-0.3518876776521916，p=0.010235334556233081）；  
- RLM winsor交互项`posterior_exponent_w:C(group)[T.TD]`显著（β=-0.5317928308721207，p=0.0025858175860909985）。  
[来源：`derivatives_task_movie/stats/resting_movie_coupling_interaction_model.csv`；`derivatives_task_movie/stats/resting_movie_coupling_interaction_model_rlm_winsor.csv`；`outputs/tables/_relaxed_significance_snapshot.csv`]

**strict敏感性（n=102）**：  
- OLS交互不显著（p=0.0792268618156943）；  
- RLM交互显著（p=0.019514529634508）。  
[来源：`outputs/tables/_strict_significance_snapshot.csv`]

### 3.6 posterior-CARS：口径敏感结果（降级解释）

**relaxed**：Spearman显著（n=62，rho=-0.2611172851025417，p=0.040373284890588584）。  
[来源：`outputs/tables/qc_covariate_control_models.csv`；`outputs/tables/_relaxed_significance_snapshot.csv`]

**strict**：不显著（n=60，p=0.06825345118589014）。  
[来源：`outputs/tables/_strict_significance_snapshot.csv`]

另外，QC协变量控制的OLS（`posterior_exponent`项）不显著（p=0.44796230778276347），支持将posterior-CARS定位为不稳健、探索性证据。  
[来源：`outputs/tables/qc_covariate_control_models.csv`]

### 3.7 QC协变量控制后的ISC

在扩大样本（mental/pain n=168，neutral n=169）并加入QC协变量后，ISC三事件仍显著且FDR后保留：  
- mental: raw p=0.02071464370698974, FDR p=0.02071464370698974；  
- pain: raw p=0.003007304496514818, FDR p=0.004510956744772227；  
- neutral: raw p=7.282946064874599e-05, FDR p=0.00021848838194623796。  
[来源：`outputs/tables/qc_covariate_control_models.csv`；`outputs/tables/qc_covariate_control_event_fdr.csv`]

## 4. 结果解释与冲突处理

本次核对发现历史稿件（v11-v15）与当前锁定结果存在若干不一致，需显式披露：

- **冲突1：ISC pain方向/显著性叙述不一致。** 旧稿中有“pain不显著”表述，但当前锁定主表与原始统计文件均显示pain显著（FDR p=0.00020346614565930002）。本稿按锁定CSV更新为“pain显著”。  
  [采用依据：`outputs/tables/final_paper_stats_locked.csv`；`derivatives_task_movie/stats/movie_isc_group_stats_with_neutral.csv`]

- **冲突2：耦合交互p值与旧稿数字不一致。** 旧稿曾出现OLS交互边缘显著、RLM较弱显著的版本；当前relaxed文件显示OLS与RLM均显著。本稿以最新文件为准，并将strict口径差异单列。  
  [采用依据：`derivatives_task_movie/stats/resting_movie_coupling_interaction_model.csv`；`derivatives_task_movie/stats/resting_movie_coupling_interaction_model_rlm_winsor.csv`；`outputs/tables/_strict_significance_snapshot.csv`]

## 5. 讨论

第一，主口径下“静息态非周期差异 + 电影ISC差异 + 跨状态耦合显著”构成一致证据链，支持ASD与TD在基础神经动力学和自然社会加工之间存在系统性差异。  

第二，耦合结果在strict口径下出现“OLS失显著、RLM仍显著”的模式，提示该关联受样本筛选与分布尾部影响，稳健模型比普通线性模型更稳定。  

第三，posterior-CARS在relaxed显著而strict不显著，且QC协变量模型不支持稳定关联，因此不应作为主结论，仅能作为假设生成信号。  

第四，ISC在QC协变量控制后仍显著，表明关键组差并非由拟合误差或坏通道比例单独驱动。

## 6. 局限性

- 本稿完全依赖现有结果文件，未重新跑原始管线；结论受既有管线设置约束。  
- 主结果来自多张口径不同的统计表，虽已分层报告，但跨表样本量（如n=128 vs n=168）提示模型目标与缺失机制并不完全一致。  
- posterior-CARS与耦合OLS在strict下不稳定，需独立样本复现。  
- 横断面设计不支持个体发育因果推断。

## 7. 结论

在主口径（relaxed）下，可稳健支持的投稿级结论为：  
- 静息态`global_exponent`存在TD>ASD差异，且后部通道簇在FDR后显著；  
- 自然电影ISC在mental/pain/neutral均表现TD>ASD；  
- 跨状态耦合交互在OLS与RLM均显著，但在strict口径下OLS不稳健；  
- posterior-CARS属于口径敏感结果，需降级解释。  

以上结论强调：本研究主贡献是“跨状态神经表型”的统计证据，而非确证性的临床相关生物标志物。

## 8. 图表清单与图注

### 8.1 主文图

**图1：静息态非周期主效应图（global exponent/offset与稳健性）**  
![图1](../figures/paper_ready_v2/fig2_main_aperiodic_effects.png)
图注：展示主模型中`global_exponent`（TD>ASD）和`global_offset`（趋势）结果及嵌套模型效应概览。  

**图2：电影ISC组间箱线图（mental/pain/neutral）**  
![图2](../../outputs_task_movie/figures/movie_isc_group_boxplot.png)
图注：三事件TD-template ISC分布与组差；当前锁定结果支持三事件均显著。  

**图3：静息-电影耦合散点（全样本）**  
![图3](../../outputs_task_movie/figures/resting_to_movie_coupling_scatter.png)
图注：`posterior_exponent`与`mental_isc_z`的分组关系，配合OLS/RLM交互统计解释。  

**图4：静息-电影耦合散点（>72月子样本）**  
![图4](../../outputs_task_movie/figures/resting_to_movie_coupling_scatter_older72.png)
图注：大龄子样本耦合模式可视化，用于发育阶段敏感性参考。  

**图5：posterior exponent vs CARS散点**  
![图5](../figures/clinical/posterior_exponent_vs_cars_scatter.png)
图注：ASD内临床相关探索图；因strict不稳健，本图仅作敏感性展示。  

**图6：mental ISC vs CARS散点**  
![图6](../figures/clinical/mental_isc_vs_cars_scatter.png)
图注：任务同步指标与症状量表关系图；用于补充临床解释边界。  

### 8.2 补充图建议

- 补图S1：strict与relaxed口径关键p值并列森林图（建议后续自动生成）。  
- 补图S2：QC协变量控制前后ISC系数变化图（建议后续自动生成）。

## 9. 主文表格（可直接投稿排版）

### 表1 样本流转（静息态主分析）

| stage | n_total | n_ASD | n_TD | excluded_total | exclusion_reason |
|---|---:|---:|---:|---:|---|
| participants_total | 168 | 80 | 88 |  |  |
| included_final | 168 | 80 | 88 | 0 | not included_final=1 |
| preprocessing_success | 168 | 80 | 88 | 0 | preprocessing failed or no epochs |
| min_usable_epochs_pass | 145 | 65 | 80 | 23 | usable_epochs < 60 |
| specparam_subject_qc_pass | 138 | 61 | 77 | 7 | low_quality_subject (invalid channel ratio > threshold) |
| roi_available_after_specparam | 138 | 61 | 77 | 0 |  |
| main_analysis_complete_case | 138 | 61 | 77 | 0 | missing outcome/covariates or specparam QC fail |

数据来源：`outputs/tables/sample_inclusion_flow.csv`

### 表2 锁定主统计表（relaxed主口径）

| Analysis_Type | Cohort_N | Test_Statistic | Raw_p | FDR_p |
|---|---|---:|---:|---:|
| ISC_mental | ASD=73,TD=95 | -2.302147242807646 | 0.0228236392086339 | 0.0228236392086339 |
| ISC_pain | ASD=73,TD=95 | -3.925915102794856 | 0.0001356440971062 | 0.00020346614565930002 |
| ISC_neutral | ASD=73,TD=96 | -4.357184001275027 | 2.460057653261554e-05 | 7.380172959784662e-05 |
| Delta_mental | ASD=56,TD=73 | 3.5009889307920794 | 0.0007112589837053 | 0.0007112589837053 |
| Delta_pain | ASD=56,TD=73 | 3.6950391222583874 | 0.0003720742183072 | 0.0007112589837053 |

数据来源：`outputs/tables/final_paper_stats_locked.csv`

### 表3 关键敏感性对照（strict vs relaxed）

| 指标 | relaxed（n/p） | strict（n/p） | 稳健性判定 |
|---|---|---|---|
| posterior-CARS Spearman | n=62, p=0.040373284890588584 | n=60, p=0.06825345118589014 | 口径敏感，降级解释 |
| coupling interaction OLS | n=128, p=0.010235334556233 | n=102, p=0.0792268618156943 | 口径敏感，OLS不稳健 |
| coupling interaction RLM | n=128, p=0.0025858175860909 | n=102, p=0.019514529634508 | 两口径均显著 |

数据来源：`outputs/tables/_relaxed_significance_snapshot.csv`；`outputs/tables/_strict_significance_snapshot.csv`

### 表4 QC协变量控制后ISC（事件家族FDR）

| event_type | raw_p | n_obs | fdr_p | significant_fdr |
|---|---:|---:|---:|---|
| mental | 0.02071464370698974 | 168 | 0.02071464370698974 | True |
| pain | 0.003007304496514818 | 168 | 0.004510956744772227 | True |
| neutral | 7.282946064874599e-05 | 169 | 0.00021848838194623796 | True |

数据来源：`outputs/tables/qc_covariate_control_event_fdr.csv`

## 10. 透明度声明

- **口径切换声明：** 主文推断以relaxed口径为准；strict仅用于敏感性验证，不直接覆盖主结论。  
- **敏感性声明：** posterior-CARS与coupling OLS在strict下不稳健，已在主文降级为探索性或模型敏感结论。  
- **QC协变量声明：** 加入`mean_fit_error`与`invalid_channel_ratio`后，ISC核心组差仍保持显著，支持主结果不完全由QC指标驱动。  
- **冲突处理声明：** 历史草稿与最新锁定CSV存在差异时，统一以锁定CSV及对应统计源文件为准，并已在“结果解释与冲突处理”中逐条标注。  

