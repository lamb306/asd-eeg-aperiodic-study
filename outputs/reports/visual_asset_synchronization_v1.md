# Visual Asset Synchronization v1

更新日期：2026-05-23 01:07（本地）

## 已重生成的核心视觉资产
- `outputs_task_movie/figures/movie_isc_group_boxplot.png`
- `outputs_task_movie/figures/resting_to_movie_coupling_scatter.png`
- `outputs_task_movie/figures/resting_to_movie_coupling_scatter_older72.png`
- `outputs/figures/clinical/mental_isc_vs_cars_scatter.png`
- `outputs/figures/clinical/posterior_exponent_vs_cars_scatter.png`

## 对齐到的统计主表
- `outputs/tables/final_paper_stats_locked.csv`

## 当前锁定统计（用于图文一致性核验）
- ISC_mental: Raw p=0.0222884, FDR p=0.0222884, Cohort=ASD=58/TD=78
- ISC_pain: Raw p=0.00139063, FDR p=0.00208595, Cohort=ASD=58/TD=78
- ISC_neutral: Raw p=8.84261e-06, FDR p=2.65278e-05, Cohort=ASD=58/TD=78
- Delta_mental: Raw p=0.000633462, FDR p=0.000633462, Cohort=ASD=45/TD=57
- Delta_pain: Raw p=0.000433949, FDR p=0.000633462, Cohort=ASD=45/TD=57

## 备注
- neutral ISC 已与 mental/pain 使用同一 movie QC 掩码和分析队列。
- `movie_isc_group_stats_with_neutral.csv` 已完成覆盖。
- 本次同步后，图与 `final_paper_stats_locked.csv` 统计口径一致。
