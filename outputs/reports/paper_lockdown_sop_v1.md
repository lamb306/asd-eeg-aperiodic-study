# 论文锁定版重跑 SOP（Resting + Movie）

## 目标
- 固定一个可复现的数据口径，避免同一结果在重跑后发生漂移。
- 形成可直接写入主文与补充材料的结果分层（见 `outputs/tables/paper_lock_result_tiering.csv`）。

## 当前确认的主结果（优先保留）
- Resting: `global_exponent` 组间差异（TD > ASD, p=0.0119, n=138）。
- Resting: 通道级 FDR 显著（E33/E36/E37/E38）。
- Movie: ISC 组间差异（mental/pain/neutral）。
- Movie: Delta exponent 组间差异（mental/pain）。
- Cross-state: `posterior_exponent × group` 交互（OLS 与 RLM 均显著，定位为次级探索性结论）。

## 暂不作为主文结论
- Movie mixed ANOVA（group/event/interaction 均不显著）。
- Movie peri-event CBPT（无显著 cluster）。
- Movie CARS 相关（多数不显著，且存在 `n=0` 失效文件）。
- Resting `global_offset` 组效应（p=0.095）。

## 必须先统一的 4 个口径
1. **样本口径**
   - Resting 主分析统一为 `n=138`（`outputs/tables/sample_inclusion_flow.csv`）。
   - Movie 建议同时固定两套：`n=128`（耦合模型）与 `n=56`（闭环/CARS 子样本）。
2. **QC 口径**
   - 强制所有 downstream 脚本读取同一 QC 后特征表，避免 `138/139/145` 混用。
3. **posterior 指标定义**
   - 在项目中二选一并全局复用：`E33/E36/E37/E38` 均值 或 occipital ROI 均值。
4. **CARS 来源**
   - 统一从同一 participants 主表合并，禁止脚本间混用 `participants.csv` 与 `participants_task_movie.csv` 的不同字段状态。

## 论文锁定版最小重跑顺序（先轻后重）
1. 生成统一参与者映射与审计表（必须）
   - 输出：每步 `n_total/n_ASD/n_TD`，并记录排除原因。
2. 重跑关键统计（必须）
   - Resting: `08_main_group_analysis.py` + `10_channel_level_analysis.py`
   - Movie: `33_compute_segment_isc.py` + `34_resting_to_movie_coupling.py` + `37_delta_exponent_and_isc_cars.py`
3. 统一多重比较（必须）
   - 对 ISC（3项）、Delta（2项）、耦合相关/模型族分别执行预先定义的 FDR 方案。
4. 仅在必要时重跑时程与扩展（可选）
   - `31_align_exponent_with_movie_labels.py`、`32_peri_stimulus_timecourse.py`、`38~41`。

## 出稿时的结果分层规则
- `core_significant`：主文结果段 + 主图。
- `secondary_significant`：主文次级结果段 + 明确“探索性”。
- `non_significant`：补充材料或简述为阴性结果。
- `invalid`：不报告结论，先修复管线。

## 最终冻结交付物（建议）
- `outputs/tables/paper_lock_result_tiering.csv`（结论分层主表）
- `outputs/tables/sample_inclusion_flow.csv`（样本流失主表）
- 统一口径后的关键 stats CSV（带时间戳）
- 简短审计记录（脚本版本、参数、重跑日期、Python 环境）
