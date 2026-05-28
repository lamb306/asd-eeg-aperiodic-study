#!/usr/bin/env python
"""
41_dynamical_trajectory_parameters.py
-------------------------------------
从0.5s滑窗时间序列提取个体动力学参数，并进行组间比较与临床关联：
1) Peak Latency
2) State Volatility
3) Transition Rate
4) Peak Amplitude
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import spearmanr, ttest_ind


METRICS = [
    "peak_latency_sec",
    "state_volatility_sd",
    "transition_rate_per_sec",
    "peak_amplitude_abs",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract dynamical trajectory parameters")
    parser.add_argument("--project_root", type=str, default=".", help="项目根目录")
    parser.add_argument(
        "--aligned_timeseries_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_event_aligned_timeseries.csv",
        help="事件对齐后的0.5s时序CSV",
    )
    parser.add_argument(
        "--events_csv",
        type=str,
        default="data/movie_events.csv",
        help="电影事件定义CSV（onset/duration/event_type）",
    )
    parser.add_argument(
        "--participants_csv",
        type=str,
        default="data/participants/participants.csv",
        help="临床量表CSV（CARS_total）",
    )
    parser.add_argument(
        "--out_stats_dir",
        type=str,
        default="derivatives_task_movie/stats",
        help="统计输出目录",
    )
    parser.add_argument(
        "--out_fig_dir",
        type=str,
        default="outputs_task_movie/figures/clinical",
        help="图像输出目录",
    )
    parser.add_argument(
        "--min_bins_per_segment",
        type=int,
        default=4,
        help="每个事件片段最少bin数",
    )
    return parser.parse_args()


def count_threshold_crossings(values: np.ndarray, threshold: float) -> int:
    if len(values) < 2:
        return 0
    centered = values - threshold
    signs = np.sign(centered)
    # 将0替换为前一个非0符号，避免平坦点造成伪切换
    for i in range(1, len(signs)):
        if signs[i] == 0:
            signs[i] = signs[i - 1]
    if signs[0] == 0:
        nz = np.nonzero(signs)[0]
        if len(nz):
            signs[0] = signs[nz[0]]
    changes = np.sum(signs[1:] * signs[:-1] < 0)
    return int(changes)


def extract_segment_metrics(
    seg_df: pd.DataFrame,
    onset_sec: float,
    duration_sec: float,
) -> dict[str, float]:
    seg = seg_df.sort_values("center_sec").copy()
    t_rel = seg["center_sec"].to_numpy(dtype=float) - float(onset_sec)
    x = seg["exponent_mean"].to_numpy(dtype=float)
    x0 = float(x[0])  # 用片段起始作为该段基线
    delta = x - x0
    abs_delta = np.abs(delta)
    peak_idx = int(np.argmax(abs_delta))

    peak_latency = float(t_rel[peak_idx])
    peak_amplitude = float(abs_delta[peak_idx])
    volatility = float(np.std(x, ddof=1)) if len(x) > 1 else 0.0

    thr = float(np.median(x))
    n_cross = count_threshold_crossings(x, thr)
    transition_rate = float(n_cross / max(float(duration_sec), 1e-6))

    return {
        "peak_latency_sec": peak_latency,
        "state_volatility_sd": volatility,
        "transition_rate_per_sec": transition_rate,
        "peak_amplitude_abs": peak_amplitude,
    }


def welch_t_by_metric(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for event_type in ["mental", "pain"]:
        sub = df[df["event_type"] == event_type].copy()
        for metric in METRICS:
            asd = pd.to_numeric(sub.loc[sub["group"] == "ASD", metric], errors="coerce").dropna()
            td = pd.to_numeric(sub.loc[sub["group"] == "TD", metric], errors="coerce").dropna()
            if len(asd) >= 2 and len(td) >= 2:
                tt = ttest_ind(asd.to_numpy(), td.to_numpy(), equal_var=False, nan_policy="omit")
                t_stat = float(tt.statistic)
                p_val = float(tt.pvalue)
            else:
                t_stat = np.nan
                p_val = np.nan
            rows.append(
                {
                    "event_type": event_type,
                    "metric": metric,
                    "n_asd": int(len(asd)),
                    "n_td": int(len(td)),
                    "asd_mean": float(asd.mean()) if len(asd) else np.nan,
                    "asd_sd": float(asd.std(ddof=1)) if len(asd) > 1 else np.nan,
                    "td_mean": float(td.mean()) if len(td) else np.nan,
                    "td_sd": float(td.std(ddof=1)) if len(td) > 1 else np.nan,
                    "t_stat_welch": t_stat,
                    "p_value_welch": p_val,
                }
            )
    return pd.DataFrame(rows)


def spearman_with_cars(df: pd.DataFrame, part: pd.DataFrame) -> pd.DataFrame:
    merged = df.merge(part[["subject_id", "group", "CARS_total", "included_final"]], on=["subject_id", "group"], how="left")
    merged = merged[(merged["group"] == "ASD") & (merged["included_final"] == 1)].copy()
    merged["CARS_total"] = pd.to_numeric(merged["CARS_total"], errors="coerce")

    rows = []
    for event_type in ["mental", "pain"]:
        sub = merged[merged["event_type"] == event_type].copy()
        for metric in METRICS:
            tmp = sub[[metric, "CARS_total"]].dropna().copy()
            n = len(tmp)
            if n >= 3:
                rho, p = spearmanr(tmp[metric].to_numpy(), tmp["CARS_total"].to_numpy())
                rho = float(rho)
                p = float(p)
            else:
                rho = np.nan
                p = np.nan
            rows.append(
                {
                    "event_type": event_type,
                    "metric": metric,
                    "n_asd": int(n),
                    "spearman_rho": rho,
                    "p_value": p,
                }
            )
    return pd.DataFrame(rows), merged


def plot_significant_group_diffs(
    subject_df: pd.DataFrame,
    t_df: pd.DataFrame,
    out_fig_dir: Path,
) -> list[str]:
    sns.set_style("whitegrid")
    paths = []
    sig = t_df[t_df["p_value_welch"] < 0.05].copy()
    for _, r in sig.iterrows():
        metric = str(r["metric"])
        ev = str(r["event_type"])
        sub = subject_df[subject_df["event_type"] == ev].copy()
        plt.figure(figsize=(6.2, 4.8))
        ax = sns.violinplot(data=sub, x="group", y=metric, inner=None, cut=0, linewidth=1)
        sns.boxplot(
            data=sub,
            x="group",
            y=metric,
            width=0.28,
            showcaps=True,
            showfliers=False,
            boxprops={"facecolor": "white", "alpha": 0.75},
            ax=ax,
        )
        sns.stripplot(data=sub, x="group", y=metric, color="k", alpha=0.4, size=3, jitter=0.15, ax=ax)
        ax.set_title(f"{ev.capitalize()} | {metric}\nWelch p={float(r['p_value_welch']):.4g}")
        ax.set_xlabel("Group")
        ax.set_ylabel(metric)
        plt.tight_layout()
        out = out_fig_dir / f"dynamics_{ev}_{metric}_group_violin.png"
        plt.savefig(out, dpi=300)
        plt.close()
        paths.append(str(out))
    return paths


def plot_significant_cars_corr(
    merged_asd_df: pd.DataFrame,
    corr_df: pd.DataFrame,
    out_fig_dir: Path,
) -> list[str]:
    sns.set_style("whitegrid")
    paths = []
    sig = corr_df[corr_df["p_value"] < 0.05].copy()
    for _, r in sig.iterrows():
        metric = str(r["metric"])
        ev = str(r["event_type"])
        sub = merged_asd_df[(merged_asd_df["event_type"] == ev)][[metric, "CARS_total"]].dropna().copy()
        if len(sub) < 3:
            continue
        plt.figure(figsize=(6.2, 4.8))
        ax = sns.regplot(
            data=sub,
            x=metric,
            y="CARS_total",
            ci=95,
            scatter_kws={"s": 42, "alpha": 0.72, "color": "#2a6fbb", "edgecolor": "none"},
            line_kws={"color": "#111111", "linewidth": 2.0},
        )
        ax.set_title(
            f"ASD {ev.capitalize()} | {metric} vs CARS\n"
            f"Spearman rho={float(r['spearman_rho']):.3f}, p={float(r['p_value']):.4g}"
        )
        ax.set_xlabel(metric)
        ax.set_ylabel("CARS_total")
        plt.tight_layout()
        out = out_fig_dir / f"dynamics_{ev}_{metric}_vs_cars_scatter.png"
        plt.savefig(out, dpi=320)
        plt.close()
        paths.append(str(out))
    return paths


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    out_stats = (root / args.out_stats_dir).resolve()
    out_fig = (root / args.out_fig_dir).resolve()
    out_stats.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)

    ts = pd.read_csv(root / args.aligned_timeseries_csv)
    ts["event_type"] = ts["event_type"].astype(str).str.lower().replace({"baseline": "neutral"})
    ts = ts[ts["event_type"].isin(["mental", "pain"])].copy()
    ts["subject_id"] = ts["subject_id"].astype(str)
    ts["group"] = ts["group"].astype(str).str.upper()
    ts["center_sec"] = pd.to_numeric(ts["center_sec"], errors="coerce")
    ts["exponent_mean"] = pd.to_numeric(ts["exponent_mean"], errors="coerce")
    ts = ts.dropna(subset=["center_sec", "exponent_mean"]).copy()

    events = pd.read_csv(root / args.events_csv)
    events["event_type"] = events["event_type"].astype(str).str.lower()
    events = events[events["event_type"].isin(["mental", "pain"])].copy()
    events["onset_sec"] = pd.to_numeric(events["onset_sec"], errors="coerce")
    events["duration_sec"] = pd.to_numeric(events["duration_sec"], errors="coerce")
    events = events.dropna(subset=["onset_sec", "duration_sec"]).copy()
    events["end_sec"] = events["onset_sec"] + events["duration_sec"]
    events = events.sort_values(["event_type", "onset_sec"]).reset_index(drop=True)
    events["event_id"] = np.arange(len(events), dtype=int)

    # 片段级指标
    seg_rows = []
    for (sid, grp), sub in ts.groupby(["subject_id", "group"], sort=False):
        for _, ev in events.iterrows():
            ev_type = str(ev["event_type"])
            onset = float(ev["onset_sec"])
            end = float(ev["end_sec"])
            dur = float(ev["duration_sec"])
            seg = sub[(sub["center_sec"] >= onset) & (sub["center_sec"] < end)].copy()
            if len(seg) < int(args.min_bins_per_segment):
                continue
            m = extract_segment_metrics(seg, onset_sec=onset, duration_sec=dur)
            seg_rows.append(
                {
                    "subject_id": sid,
                    "group": grp,
                    "event_type": ev_type,
                    "event_id": int(ev["event_id"]),
                    "onset_sec": onset,
                    "duration_sec": dur,
                    "n_bins": int(len(seg)),
                    **m,
                }
            )
    seg_df = pd.DataFrame(seg_rows)
    if seg_df.empty:
        raise RuntimeError("未提取到任何事件片段指标，请检查输入时序与事件定义。")

    # 被试级（按event_type对片段取平均）
    agg_cols = {m: "mean" for m in METRICS}
    subject_df = (
        seg_df.groupby(["subject_id", "group", "event_type"], as_index=False)
        .agg(**{k: (k, "mean") for k in METRICS}, n_segments=("event_id", "count"))
    )

    # 组间比较
    t_df = welch_t_by_metric(subject_df)

    # 临床关联（ASD）
    part = pd.read_csv(root / args.participants_csv)
    part["subject_id"] = part["subject_id"].astype(str)
    part["group"] = part["group"].astype(str).str.upper()
    part["CARS_total"] = pd.to_numeric(part["CARS_total"], errors="coerce")
    part["included_final"] = pd.to_numeric(part.get("included_final", np.nan), errors="coerce")
    corr_df, merged_asd = spearman_with_cars(subject_df, part)

    # 出图（仅显著）
    fig_group = plot_significant_group_diffs(subject_df, t_df, out_fig)
    fig_corr = plot_significant_cars_corr(merged_asd, corr_df, out_fig)

    # 保存
    seg_path = out_stats / "dynamics_segment_level_parameters.csv"
    sub_path = out_stats / "dynamics_subject_level_parameters.csv"
    t_path = out_stats / "dynamics_group_ttests.csv"
    corr_path = out_stats / "dynamics_asd_cars_spearman.csv"
    figlog_path = out_stats / "dynamics_significant_figures_log.csv"

    seg_df.to_csv(seg_path, index=False)
    subject_df.to_csv(sub_path, index=False)
    t_df.to_csv(t_path, index=False)
    corr_df.to_csv(corr_path, index=False)
    pd.DataFrame({"figure_path": fig_group + fig_corr}).to_csv(figlog_path, index=False)

    print("Saved:", seg_path)
    print("Saved:", sub_path)
    print("Saved:", t_path)
    print("Saved:", corr_path)
    print("Saved:", figlog_path)
    print("\nGroup Welch t-tests:")
    print(t_df.to_string(index=False))
    print("\nASD Spearman with CARS:")
    print(corr_df.to_string(index=False))
    print("\nGenerated significant figures:", len(fig_group) + len(fig_corr))
    for p in fig_group + fig_corr:
        print("-", p)


if __name__ == "__main__":
    main()

