#!/usr/bin/env python
"""
32_peri_stimulus_timecourse.py
------------------------------
事件相关时间过程分析（Peri-stimulus Time-Series）：
1) 每个事件用 onset 前 -2~0s 作为局部基线
2) 计算 Delta Exponent = exponent - local_baseline
3) 绘制 mental / pain 条件下 ASD vs TD 的时间过程曲线（95% CI）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from mne.stats import permutation_cluster_test
from matplotlib import pyplot as plt
from scipy.stats import f

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import save_csv  # noqa: E402


PLOT_EVENT_TYPES = ("mental", "pain")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="绘制事件相关 Delta Exponent 时间过程")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config_task_movie.yaml",
        help="配置文件路径",
    )
    parser.add_argument(
        "--events_csv",
        type=str,
        default="data/movie_events.csv",
        help="事件标注 CSV",
    )
    parser.add_argument(
        "--pre_baseline_sec",
        type=float,
        default=2.0,
        help="局部基线长度（秒），即 onset 前窗口长度",
    )
    parser.add_argument(
        "--post_sec",
        type=float,
        default=8.0,
        help="onset 后最短追踪秒数",
    )
    parser.add_argument(
        "--time_bin_sec",
        type=float,
        default=0.5,
        help="时间序列分箱步长（秒）",
    )
    parser.add_argument(
        "--n_permutations",
        type=int,
        default=2000,
        help="CBPT 置换次数（建议 >=1000）",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="簇显著性阈值",
    )
    return parser.parse_args()


def _required_cols(df: pd.DataFrame, cols: set[str], name: str) -> None:
    miss = cols - set(df.columns)
    if miss:
        raise ValueError(f"{name} 缺少列: {sorted(miss)}")


def run_cbpt_by_event(
    subject_curve: pd.DataFrame,
    event_type: str,
    n_permutations: int,
    alpha: float,
    threshold_alpha: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """对单个事件类型执行 ASD vs TD 的 1D cluster permutation 检验。"""
    sub = subject_curve[subject_curve["event_type"] == event_type].copy()
    asd = sub[sub["group"] == "ASD"].pivot_table(
        index="subject_id",
        columns="rel_time_bin",
        values="delta_exponent",
        aggfunc="mean",
    )
    td = sub[sub["group"] == "TD"].pivot_table(
        index="subject_id",
        columns="rel_time_bin",
        values="delta_exponent",
        aggfunc="mean",
    )

    common_bins = sorted(set(asd.columns) & set(td.columns))
    if not common_bins:
        return (
            pd.DataFrame([{
                "event_type": event_type,
                "cluster_id": -1,
                "p_cluster": np.nan,
                "start_sec": np.nan,
                "end_sec": np.nan,
                "n_timebins": 0,
                "is_significant": False,
                "note": "no_common_time_bins",
            }]),
            pd.DataFrame(),
        )

    asd = asd[common_bins].dropna(axis=0, how="any")
    td = td[common_bins].dropna(axis=0, how="any")
    if asd.empty or td.empty:
        return (
            pd.DataFrame([{
                "event_type": event_type,
                "cluster_id": -1,
                "p_cluster": np.nan,
                "start_sec": np.nan,
                "end_sec": np.nan,
                "n_timebins": 0,
                "is_significant": False,
                "note": "insufficient_subjects_after_dropna",
            }]),
            pd.DataFrame(),
        )

    x_asd = asd.to_numpy(dtype=float)
    x_td = td.to_numpy(dtype=float)
    times = np.asarray(common_bins, dtype=float)
    n1, n2 = x_asd.shape[0], x_td.shape[0]
    # 两独立样本比较下，F(1, n1+n2-2) 阈值等价于 t^2 阈值。
    f_threshold = float(f.ppf(1 - threshold_alpha, dfn=1, dfd=max(1, n1 + n2 - 2)))

    t_obs, clusters, cluster_pvals, _ = permutation_cluster_test(
        [x_asd, x_td],
        n_permutations=n_permutations,
        threshold=f_threshold,
        out_type="mask",
        verbose=False,
    )

    rows = []
    for i, (mask, p_val) in enumerate(zip(clusters, cluster_pvals, strict=False)):
        idx = np.where(mask)[0]
        if len(idx) == 0:
            continue
        rows.append({
            "event_type": event_type,
            "cluster_id": i,
            "p_cluster": float(p_val),
            "start_sec": float(times[idx[0]]),
            "end_sec": float(times[idx[-1]]),
            "n_timebins": int(len(idx)),
            "is_significant": bool(p_val < alpha),
            "note": "",
        })
    if not rows:
        rows.append({
            "event_type": event_type,
            "cluster_id": -1,
            "p_cluster": np.nan,
            "start_sec": np.nan,
            "end_sec": np.nan,
            "n_timebins": 0,
            "is_significant": False,
            "note": "no_clusters_returned",
        })

    t_df = pd.DataFrame({
        "event_type": event_type,
        "rel_time_bin": times,
        "test_stat": t_obs,
    })
    return pd.DataFrame(rows), t_df


def main() -> None:
    args = parse_args()
    cfg = load_config(Path(args.config))
    log = setup_logging(cfg, name="peri_stimulus_timecourse")

    deriv = Path(cfg["paths"]["derivatives_root"])
    outputs = Path(cfg["paths"]["outputs_root"])
    ts_path = deriv / "specparam" / "specparam_exponent_timeseries_global.csv"
    events_path = (PROJECT_ROOT / args.events_csv).resolve()

    if not ts_path.exists():
        raise FileNotFoundError(f"未找到动态时序文件: {ts_path}")
    if not events_path.exists():
        raise FileNotFoundError(f"未找到事件文件: {events_path}")

    ts = pd.read_csv(ts_path)
    _required_cols(
        ts,
        {"subject_id", "group", "window_start_sec", "window_end_sec", "exponent_mean"},
        "specparam_exponent_timeseries_global.csv",
    )
    ts = ts.copy()
    ts["center_sec"] = (ts["window_start_sec"] + ts["window_end_sec"]) / 2.0

    events = pd.read_csv(events_path)
    _required_cols(events, {"onset_sec", "duration_sec", "event_type"}, "movie_events.csv")
    events = events.copy()
    events["event_type"] = events["event_type"].astype(str).str.strip().str.lower()
    events = events[events["event_type"].isin(PLOT_EVENT_TYPES)].reset_index(drop=True)
    events["event_id"] = np.arange(len(events), dtype=int)

    rows = []
    skipped_no_baseline = 0
    for (sid, grp), sub in ts.groupby(["subject_id", "group"], sort=False):
        for _, ev in events.iterrows():
            onset = float(ev["onset_sec"])
            duration = float(ev["duration_sec"])
            post_end = max(args.post_sec, duration)

            base_mask = (sub["center_sec"] >= onset - args.pre_baseline_sec) & (sub["center_sec"] < onset)
            base_sub = sub.loc[base_mask]
            if base_sub.empty:
                skipped_no_baseline += 1
                continue
            baseline_mean = float(base_sub["exponent_mean"].mean())

            win_mask = (
                (sub["center_sec"] >= onset - args.pre_baseline_sec)
                & (sub["center_sec"] <= onset + post_end)
            )
            win_sub = sub.loc[win_mask].copy()
            if win_sub.empty:
                continue

            win_sub["event_id"] = int(ev["event_id"])
            win_sub["event_type"] = ev["event_type"]
            win_sub["onset_sec"] = onset
            win_sub["duration_sec"] = duration
            win_sub["local_baseline_mean"] = baseline_mean
            win_sub["rel_time_sec"] = win_sub["center_sec"] - onset
            win_sub["delta_exponent"] = win_sub["exponent_mean"] - baseline_mean
            win_sub["subject_id"] = sid
            win_sub["group"] = grp
            rows.append(
                win_sub[
                    [
                        "subject_id",
                        "group",
                        "event_id",
                        "event_type",
                        "onset_sec",
                        "duration_sec",
                        "window_start_sec",
                        "window_end_sec",
                        "center_sec",
                        "rel_time_sec",
                        "exponent_mean",
                        "local_baseline_mean",
                        "delta_exponent",
                    ]
                ]
            )

    if not rows:
        raise RuntimeError("未生成任何事件相关窗口，请检查事件时间与动态时序是否匹配")

    peri = pd.concat(rows, ignore_index=True)
    peri["rel_time_bin"] = np.round(peri["rel_time_sec"] / args.time_bin_sec) * args.time_bin_sec
    peri = peri.sort_values(["event_type", "subject_id", "event_id", "rel_time_bin"]).reset_index(drop=True)

    # 每个被试在每种事件和时间点先求均值，避免事件数差异直接影响组平均
    subject_curve = (
        peri.groupby(["subject_id", "group", "event_type", "rel_time_bin"], as_index=False)
        .agg(delta_exponent=("delta_exponent", "mean"))
    )

    summary = (
        subject_curve.groupby(["group", "event_type", "rel_time_bin"], as_index=False)
        .agg(
            mean_delta=("delta_exponent", "mean"),
            std_delta=("delta_exponent", "std"),
            n_subject=("delta_exponent", "count"),
        )
    )
    summary["se"] = summary["std_delta"] / np.sqrt(summary["n_subject"].clip(lower=1))
    summary["ci95"] = 1.96 * summary["se"]

    stats_dir = deriv / "stats"
    fig_dir = outputs / "figures"
    stats_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    save_csv(peri, stats_dir / "movie_peri_event_delta_windows.csv")
    save_csv(subject_curve, stats_dir / "movie_peri_event_delta_subject_curves.csv")
    save_csv(summary, stats_dir / "movie_peri_event_delta_group_summary.csv")

    cluster_tables = []
    t_tables = []
    for ev in PLOT_EVENT_TYPES:
        ctab, ttab = run_cbpt_by_event(
            subject_curve=subject_curve,
            event_type=ev,
            n_permutations=args.n_permutations,
            alpha=args.alpha,
            threshold_alpha=args.alpha,
        )
        cluster_tables.append(ctab)
        if not ttab.empty:
            t_tables.append(ttab)
    clusters_df = pd.concat(cluster_tables, ignore_index=True)
    save_csv(clusters_df, stats_dir / "movie_peri_event_cbpt_clusters.csv")
    if t_tables:
        save_csv(pd.concat(t_tables, ignore_index=True), stats_dir / "movie_peri_event_cbpt_test_stats.csv")

    groups_sorted = sorted(summary["group"].dropna().unique().tolist())
    colors = {"ASD": "#1f77b4", "TD": "#d62728"}
    fig, axes = plt.subplots(1, len(PLOT_EVENT_TYPES), figsize=(13, 5), sharey=True)
    if len(PLOT_EVENT_TYPES) == 1:
        axes = [axes]

    for ax, ev_type in zip(axes, PLOT_EVENT_TYPES, strict=True):
        sub = summary[summary["event_type"] == ev_type].sort_values("rel_time_bin")
        for grp in groups_sorted:
            g = sub[sub["group"] == grp].sort_values("rel_time_bin")
            if g.empty:
                continue
            x = g["rel_time_bin"].to_numpy()
            y = g["mean_delta"].to_numpy()
            ci = g["ci95"].fillna(0).to_numpy()
            color = colors.get(grp, None)
            ax.plot(x, y, label=grp, linewidth=2, color=color)
            ax.fill_between(x, y - ci, y + ci, alpha=0.2, color=color)
        # 标注显著簇时间窗（cluster p < alpha）
        sig = clusters_df[
            (clusters_df["event_type"] == ev_type)
            & (clusters_df["is_significant"])
        ].copy()
        y_top = sub["mean_delta"].max() + sub["ci95"].max() + 0.005
        for _, row in sig.iterrows():
            start = float(row["start_sec"])
            end = float(row["end_sec"])
            p_val = float(row["p_cluster"])
            ax.axvspan(start, end, color="grey", alpha=0.15)
            ax.plot([start, end], [y_top, y_top], color="black", linewidth=2.2)
            ax.text(
                (start + end) / 2.0,
                y_top + 0.001,
                f"p={p_val:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        ax.axvline(0, color="black", linestyle="--", linewidth=1)
        ax.axhline(0, color="#666", linestyle=":", linewidth=1)
        ax.set_title(f"{ev_type.capitalize()} events")
        ax.set_xlabel("Time from onset (s)")
        ax.set_xlim(-args.pre_baseline_sec, args.post_sec)
    axes[0].set_ylabel("Delta Exponent (baseline-corrected)")
    axes[-1].legend(title="Group", frameon=True)
    fig.suptitle("Peri-stimulus Time-Course (ROI mean exponent)", y=1.02, fontsize=13)
    fig.tight_layout()
    out_fig = fig_dir / "movie_peri_event_delta_timecourse"
    fig.savefig(out_fig.with_suffix(".png"), dpi=200, bbox_inches="tight")
    fig.savefig(out_fig.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)

    log.info("事件相关窗口: %s", stats_dir / "movie_peri_event_delta_windows.csv")
    log.info("被试级时间曲线: %s", stats_dir / "movie_peri_event_delta_subject_curves.csv")
    log.info("组水平汇总: %s", stats_dir / "movie_peri_event_delta_group_summary.csv")
    log.info("CBPT 簇结果: %s", stats_dir / "movie_peri_event_cbpt_clusters.csv")
    log.info("时间过程图: %s", out_fig.with_suffix('.png'))
    log.info("无局部基线而跳过的 subject-event 数: %d", skipped_no_baseline)


if __name__ == "__main__":
    main()
