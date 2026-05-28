# 论文锁定版最小链路重跑记录（v1）

重跑时间：2026-05-23 00:52（本地）

## 本轮执行链路
- `python scripts/26_build_ml_input_dataset.py ... --output_csv data.csv`
- `python scripts/08_main_group_analysis.py`
- `python scripts/10_channel_level_analysis.py`
- `python scripts/33_compute_segment_isc.py --config config/config_task_movie.yaml`
- `python scripts/34_resting_to_movie_coupling.py --config config/config_task_movie.yaml --resting_csv data.csv`
- `python scripts/37_delta_exponent_and_isc_cars.py`

## 口径修复点（已落地）
- `data.csv` 改为基于 `specparam_channel_results_qc.csv` 构建，并交集：
  - `participants.csv` 的 `included_final==1`
  - `derivatives/participants_analysis.csv`
  - `derivatives/specparam/specparam_qc_summary_subject.csv`（剔除 `low_quality_subject==1`）
- movie ISC（脚本 33）增加 movie 分析队列 + movie specparam 低质量被试剔除。
- 静息-movie 耦合（脚本 34）增加 `participants_task_movie.csv` 的 `included_final==1` + movie 分析队列 + movie low-quality 剔除。
- Delta/CARS（脚本 37）把 CARS 来源统一为 `participants.csv`，movie 纳入口径来自 `participants_task_movie.csv` + movie 分析队列 + movie low-quality 剔除。

## 新样本量（重跑后）
- `data.csv`: 135（ASD=60, TD=75）
- resting 主分析：138
- movie ISC（mental/pain）：ASD=58, TD=78
- resting-movie coupling：102（ASD=45, TD=57）
- Delta exponent：102（ASD=45, TD=57）
- ASD CARS 相关（脚本 37）：45（已从历史 n=0 修复）

## 关键结果变化（相对上一版）
- **Resting 主结果稳定**
  - `global_exponent` 组效应：p=0.0119（保持显著）
  - 通道 FDR 显著仍为 E33/E36/E37/E38（4通道）
- **Movie ISC 仍显著但效应减弱**
  - mental: p=0.0223（仍显著）
  - pain: p=0.00139（仍显著）
- **Cross-state 交互显著性分化**
  - OLS 交互：p=0.0792（降为不显著）
  - RLM+Winsor 交互：p=0.0195（仍显著）
- **CARS（movie）已可计算但不显著**
  - mental/pain ISC vs CARS：均 p>0.35（Pearson）和 p>0.76（Spearman）

## 当前建议的论文落点
- 主文保留：resting `global_exponent`、resting后枕FDR、movie ISC、movie Delta。
- 降级为探索性：resting-movie 交互（仅 RLM 显著）、CARS 相关。
- 暂不升级：mixed ANOVA / CBPT（仍不显著）。
